"""
VocabVoyage LangGraph 代理模組

此模組實作基於 LangGraph 的智能代理系統，負責：
- 處理用戶查詢的路由和決策
- 管理詞彙查詢、分類學習和測驗生成工具
- 整合 RAG (Retrieval-Augmented Generation) 系統
- 生成個性化的學習內容和回應
"""

from typing import TypedDict, Annotated, Sequence, Literal
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
import graphviz
import pprint
from .database import VocabDatabase
from .config import get_openai_config, get_chroma_config, get_chat_config, config

# 初始化資料庫連接
db = VocabDatabase()


def get_recent_chat_history(chat_id: str) -> list[BaseMessage]:
    """
    從資料庫獲取最近的聊天記錄
    
    Args:
        chat_id (str): 聊天會話的唯一識別碼
        
    Returns:
        list[BaseMessage]: 最近的聊天訊息列表（根據配置決定數量）
        
    功能說明：
    - 從資料庫獲取指定聊天會話的訊息歷史
    - 根據配置設定保留最近的對話數量
    - 將訊息轉換為 LangChain 的 BaseMessage 格式
    - 按時間順序排列，用於維持對話上下文
    """
    messages = db.get_chat_messages(chat_id)
    if not messages:
        return []
    
    # 從配置獲取最大歷史訊息數量
    chat_config = get_chat_config()
    max_messages = chat_config.max_history_messages
    
    # 計算每種角色的最大數量（平均分配）
    max_per_role = max_messages // 2
    
    recent_messages = []
    user_count = 0
    assistant_count = 0
    
    # 從最新的消息開始往前遍歷
    for msg in reversed(messages):
        if msg["role"] == "user" and user_count < max_per_role:
            recent_messages.insert(0, HumanMessage(content=msg["content"]))
            user_count += 1
        elif msg["role"] == "assistant" and assistant_count < max_per_role:
            recent_messages.insert(0, AIMessage(content=msg["content"]))
            assistant_count += 1
            
        # 達到目標數量後停止
        if user_count >= max_per_role and assistant_count >= max_per_role:
            break
            
    return recent_messages


# 定義 LangGraph 狀態類型
class VocabState(TypedDict):
    """
    詞彙學習代理的狀態定義
    
    Attributes:
        messages: 對話訊息序列，支援自動合併新訊息
        context: 上下文資訊字典，用於存儲額外的處理資訊
        user_id: 用戶的唯一識別碼
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    context: dict
    user_id: str


# 系統提示詞模板
SYSTEM_PROMPTS = {
    "search": """
你是一個專業的英語教師。請使用繁體中文提供這個單字的詳細資訊，格式如下：
---
單字：[英文單字]
詞性：[以繁體中文說明詞性]
定義：[繁體中文定義]
例句：
-> [英文例句1]
    (中文翻譯：[繁體中文翻譯])
-> [英文例句2]
    (中文翻譯：[繁體中文翻譯])
相關詞彙：[相關英文詞彙（其詞性及繁體中文解釋）、相關英文詞彙（其詞性及繁體中文解釋）...](接續在後面就好，不要條列！)
使用建議：[單字使用建議的繁體中文說明]
---
請確保回應嚴格遵循以上格式，所有解釋都使用繁體中文。
""",

    "category": """
根據檢索到的資料列出相關單字。
檢索到的資料：{context}

請列出其中隨機10個單字或片語，記得要隨機選單字或片語，不要都只選前面的或特定的，
使用繁體中文解釋，格式如下：

【類別名稱】相關單字或片語：

1. [英文單字/片語1]
- 定義：[繁體中文定義]
- 詞性：[詞性]
- 使用：[單字使用建議的說明(繁體中文)]
- 例句：[英文例句]
       (翻譯：[繁體中文翻譯])

2. [英文單字/片語2]
...（依此類推）
""",

    "quiz": """
你是一個專業的英語教師。請根據提供的單字資訊生成以下其中一種測驗。
所有說明和解釋都需使用繁體中文。

以下是相關的單字資訊：
{context}

===== 測驗說明 =====
第一種 -> 選擇題：測試單字的定義和用法理解
第二種 -> 填空題：測試單字在語境中的正確使用
第三種 -> 配對題：測試單字與其定義的對應關係

===== 測驗開始 =====

【第一種：選擇題】(共5題)
說明：每題皆有四個選項，請選出最適當的答案
--------------------
1. [題目內容(中文)] \n
   A) [選項A(英文)]
   B) [選項B(英文)]
   C) [選項C(英文)]
   D) [選項D(英文)]

2. [依此格式撰寫其餘題目...]

【第二種：填空題】(共5題)
說明：請將適當的單字填入句子空格中，單字需做適當的語態變化
--------------------
1. The company needs to ________ its marketing strategy to adapt to the changing market.   ----- (提示：調整/修改)

2. [依此格式撰寫其餘題目...]

【第三種：配對題】(共5題)
說明：請將上方的單字與下方的解釋配對，在橫線上填入對應的選項代號
--------------------
單字：
1. ________ innovation
2. ________ sustainable
3. ________ implement
4. ________ strategy
5. ________ efficiency \n
解釋：
A) 可持續發展的
B) 創新
C) 執行
D) 策略
E) 效率

===== 答案與解釋 =====

【選擇題答案】
1. [正確選項] \n
解釋：[詳細說明為什麼這是正確答案，並解釋其他選項為何不適當]

2. [依此格式提供其餘答案...]

【填空題答案】
1. adjust/modify \n
解釋：[說明為什麼這個單字最適合此語境，並解釋單字的用法和其他可能的同義詞]

2. [依此格式提供其餘答案...]

【配對題答案】
1. B  2. A  3. C  4. D  5. E \n
解釋：
- innovation (B)：[詳細解釋單字意義和用法]
- sustainable (A)：[詳細解釋單字意義和用法]
[依此格式解釋其餘配對]

----
答案與解釋請完整、詳細、友善、像老師。
請把格式排版好看。是 markdown 格式。
三種題型選擇一種來出題就好。
""",

    "other": """
你是一個友善的英語學習助手。請使用繁體中文回應。

如果用戶的問題與英語學習無關，請友善地引導他們詢問英語相關的問題。
你可以提供以下建議：
1. 查詢單字或片語的意思和用法
2. 瀏覽特定主題領域的詞彙（如：商業、科技、醫療等）
3. 進行特定主題的詞彙測驗

如果用戶的問題確實與英語學習有關，則直接回答他們的問題。要求短篇英文小文章或翻譯是可以的。

請使用友善且鼓勵的語氣，確保說明的部分都使用繁體中文。
"""
}


def agent(state: VocabState):
    """
    智能代理節點：決定是否使用工具或直接生成回應
    
    Args:
        state (VocabState): 當前的對話狀態
        
    Returns:
        dict: 更新後的狀態，包含代理的決策結果
        
    功能說明：
    - 分析用戶的查詢意圖
    - 決定是否需要使用特定工具（詞彙查詢、分類學習、測驗生成）
    - 如果不需要工具，標記為直接回應
    - 使用 GPT-4o-mini 模型進行決策推理
    """
    print(" *** 調用代理 *** ")
    messages = state["messages"]

    # 系統提示詞：定義代理的角色和決策邏輯
    system_message = """你是一個英語學習助手的路由器。
你的唯一任務是決定是否使用提供的工具來回答用戶的問題。
- 如果問題需要用工具回答，請使用適當的工具
- 如果問題不需要工具（比如一般英語學習建議或非英語相關問題），請回覆 "DIRECT_RESPONSE"
- 注意不要輕易的使用category_vocabulary_list跟vocabulary_quiz_generator這兩個工具，要確定你真的必須使用它們再使用
不要直接回答用戶的問題，只需決定使用工具或返回標記。"""
    
    # 將系統訊息添加到對話開頭
    messages = [HumanMessage(content=system_message)] + messages

    # 從配置獲取 OpenAI 設定並初始化模型
    openai_config = get_openai_config()
    model = ChatOpenAI(
        temperature=openai_config.temperature, 
        model=openai_config.chat_model,
        max_tokens=openai_config.max_tokens
    )
    model = model.bind_tools(tools)
    
    # 獲取模型回應
    response = model.invoke(messages)
    
    return {
        "messages": [response],
        "context": state["context"],
        "user_id": state["user_id"]
    }


def generate_response(state: VocabState):
    """
    回應生成節點：生成最終的用戶回應
    
    Args:
        state (VocabState): 當前的對話狀態
        
    Returns:
        dict: 包含最終回應的狀態更新
        
    功能說明：
    - 處理工具調用的結果
    - 對於非工具查詢，生成個性化回應
    - 整合聊天歷史以維持對話連貫性
    - 使用適當的提示詞模板生成友善的回應
    """
    print(" *** 生成回應 *** ")
    messages = state["messages"]
    last_message = messages[-1]
    
    # 如果最後一條訊息是工具回應，直接返回
    if isinstance(last_message, ToolMessage):
        return {
            "messages": [last_message],
            "context": state["context"],
            "user_id": state["user_id"]
        }
    
    # 處理其他情況：生成個性化回應
    openai_config = get_openai_config()
    llm = ChatOpenAI(
        model=openai_config.chat_model, 
        temperature=openai_config.temperature,
        max_tokens=openai_config.max_tokens
    )

    # 將聊天歷史轉換為格式化的字符串
    chat_history = []
    for msg in messages[:-2]:  # 除了最新消息外的所有歷史
        role = "用戶" if isinstance(msg, HumanMessage) else "助手"
        chat_history.append(f"{role}: {msg.content}")
    formatted_history = "\n".join(chat_history)
    
    # 獲取當前用戶問題
    current_question = messages[-2].content  # 最新的問題

    # 使用提示詞模板生成回應
    prompt = PromptTemplate(
        template=SYSTEM_PROMPTS["other"] + "\n\n=== 聊天歷史 ===\n{chat_history}\n\n=== 最新問題 ===\n{query}",
        input_variables=["chat_history", "query"]
    )
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({
        "chat_history": formatted_history,
        "query": current_question
    })
    
    return {
        "messages": [AIMessage(content=response)],
        "context": state["context"],
        "user_id": state["user_id"]
    }


def setup_rag():
    """
    設置 RAG (Retrieval-Augmented Generation) 相關組件
    
    Returns:
        VectorStoreRetriever: 配置好的向量資料庫檢索器
        
    功能說明：
    - 使用配置管理器初始化 Chroma 向量資料庫連接
    - 配置 OpenAI 嵌入模型
    - 設置搜索參數
    - 返回可用於詞彙檢索的檢索器實例
    """
    print(" *** 調用 RAG *** ")
    
    # 從配置獲取相關設定
    chroma_config = get_chroma_config()
    openai_config = get_openai_config()
    
    # 初始化 Chroma 向量資料庫
    vectorstore = Chroma(
        persist_directory=chroma_config.persist_directory,
        embedding_function=OpenAIEmbeddings(model=openai_config.embedding_model),
        collection_name=chroma_config.collection_name
    )
    
    # 使用配置的檢索器參數
    retriever_config = config.get_retriever_config()
    return vectorstore.as_retriever(**retriever_config)


def search_vocabulary(query: str) -> str:
    """
    處理單字查詢工具
    
    Args:
        query (str): 用戶查詢的英文單字或片語
        
    Returns:
        str: 格式化的單字詳細資訊
        
    功能說明：
    - 使用配置的 OpenAI 模型分析單字
    - 按照標準格式提供單字資訊
    - 包含詞性、定義、例句、相關詞彙和使用建議
    - 所有解釋都使用繁體中文
    """
    print(" *** 調用單字查詢 *** ")
    
    # 從配置初始化語言模型
    openai_config = get_openai_config()
    llm = ChatOpenAI(
        model=openai_config.chat_model, 
        temperature=openai_config.temperature,
        max_tokens=openai_config.max_tokens
    )
    
    # 建立提示詞模板
    prompt = PromptTemplate(
        template=SYSTEM_PROMPTS["search"] + "\n\n查詢單字: {query}",
        input_variables=["query"]
    )
    
    # 建立處理鏈並執行查詢
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"query": query})
    
    return response


def get_category_vocabulary(category: str) -> str:
    """
    處理類別詞彙查詢工具
    
    Args:
        category (str): 用戶指定的詞彙類別或主題
        
    Returns:
        str: 該類別的相關詞彙列表和詳細說明
        
    功能說明：
    - 使用 RAG 系統從向量資料庫檢索相關詞彙
    - 隨機選擇10個相關單字或片語
    - 提供每個詞彙的定義、詞性、使用建議和例句
    - 格式化輸出，便於學習和理解
    """
    print(" *** 調用類別查詢 *** ")
    
    # 設置 RAG 檢索器
    retriever = setup_rag()
    
    # 從向量資料庫檢索相關文檔
    docs = retriever.invoke(category)
    context = "\n".join(doc.page_content for doc in docs)
    
    # 從配置初始化語言模型
    openai_config = get_openai_config()
    llm = ChatOpenAI(
        model=openai_config.chat_model, 
        temperature=openai_config.temperature,
        max_tokens=openai_config.max_tokens
    )
    
    # 建立提示詞模板
    prompt = PromptTemplate(
        template=SYSTEM_PROMPTS["category"],
        input_variables=["context"]
    )
    
    # 建立處理鏈並執行查詢
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"context": context})
    
    return response


def generate_quiz(category: str) -> str:
    """
    生成類別測驗工具
    
    Args:
        category (str): 測驗主題或類別
        
    Returns:
        str: 完整的測驗內容，包含題目和答案解析
        
    功能說明：
    - 使用 RAG 系統獲取相關詞彙資料
    - 生成三種類型測驗之一：選擇題、填空題或配對題
    - 提供詳細的答案解析和學習建議
    - 使用 Markdown 格式，便於閱讀和理解
    """
    print(" *** 調用生成類別測驗 *** ")
    
    # 設置 RAG 檢索器
    retriever = setup_rag()
    
    # 從向量資料庫檢索相關文檔
    docs = retriever.invoke(category)
    context = "\n".join(doc.page_content for doc in docs)
    
    # 從配置初始化語言模型
    openai_config = get_openai_config()
    llm = ChatOpenAI(
        model=openai_config.chat_model, 
        temperature=openai_config.temperature,
        max_tokens=openai_config.max_tokens
    )
    
    # 建立提示詞模板
    prompt = PromptTemplate(
        template=SYSTEM_PROMPTS["quiz"],
        input_variables=["context"]
    )
    
    # 建立處理鏈並執行查詢
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"context": context})
    
    return response


# 創建 LangChain 工具列表
tools = [
    Tool(
        name="search_vocabulary_details",
        description="""
用於查詢單個英文單字或片語的詳細資訊。適用情況：
1. 想知道某個英文單字的中文意思
2. 需要查詢單字的詳細用法和例句
3. 想了解單字的相關詞彙
使用方式：輸入「查詢單字 [你想查的單字]」或「解釋單字 [你想查的單字]」
例如：
- 查詢單字 resilient
- 解釋單字 innovation
- artificial 是什麼
""",
        func=search_vocabulary,
        return_direct=True  # 直接返回工具結果，不需要進一步處理
    ),
    Tool(
        name="category_vocabulary_list",
        description="""
用於獲取特定主題或領域的相關英文單字列表(只問或只需要一個單字則不會用到)。
適用情況：
1. 想學習特定領域的多個專業詞彙
2. 需要某個主題的相關單字
3. 想擴充特定場景的詞彙量
支援的類別包括但不限於：
- 商業/金融 (Business/Finance)
- 科技/IT (Technology/IT)
- 醫療/健康 (Medical/Health)
- 教育/學術 (Education/Academic)
- 環境/生態 (Environment/Ecology)
使用方式：輸入「列出 [類別] 相關單字」或「我想學習 [領域] 的單字」
例如：
- 列出商業相關單字
- 我想學習醫療領域的詞彙
- 給我一些科技方面的專業用語
""",
        func=get_category_vocabulary,
        return_direct=True  # 直接返回工具結果，不需要進一步處理
    ),
    Tool(
        name="vocabulary_quiz_generator",
        description="""
用於生成特定主題的英文單字測驗(只問或只需要一個單字則不會用到)。
適用情況：
1. 想測試特定領域的詞彙掌握程度
2. 需要練習題進行自我評估
3. 想以測驗方式學習新單字
使用方式：輸入「生成 [主題] 測驗」或「我要做 [領域] 的單字測驗」
例如：
- 生成商業英文測驗
- 我要做科技詞彙的測驗
- 幫我出一份環保主題的單字測驗
""",
        func=generate_quiz,
        return_direct=True  # 直接返回工具結果，不需要進一步處理
    )
]


def create_vocab_chain():
    """
    創建主要的 LangGraph 工作流程
    
    Returns:
        CompiledGraph: 編譯後的 LangGraph 工作流程
        
    功能說明：
    - 建立包含代理、工具和回應生成的完整工作流程
    - 配置節點間的條件邊和固定邊
    - 實現智能路由：根據查詢類型選擇適當的處理路徑
    - 支援工具調用和直接回應兩種處理模式
    """
    # 創建工具節點
    tool_node = ToolNode(tools=tools)
    
    # 建立 LangGraph 工作流程圖
    workflow = StateGraph(VocabState)
    
    # 添加處理節點
    workflow.add_node("agent", agent)           # 智能代理節點
    workflow.add_node("tools", tool_node)       # 工具執行節點
    workflow.add_node("generate", generate_response)  # 回應生成節點
    
    # 添加工作流程邊
    workflow.add_edge(START, "agent")  # 從開始節點到代理節點
    
    # 從代理到工具或生成的條件邊
    workflow.add_conditional_edges(
        "agent",
        tools_condition,  # 使用 LangGraph 內建的工具條件判斷
        {
            "tools": "tools",      # 如果需要工具，前往工具節點
            END: "generate",       # 如果不需要工具，前往生成節點
        }
    )
    
    # 工具節點執行完成後前往生成節點
    workflow.add_edge("tools", "generate")
    
    # 生成節點完成後結束工作流程
    workflow.add_edge("generate", END)

    # 編譯並返回工作流程
    return workflow.compile()


def process_vocab_query(query_data: dict):
    """
    處理詞彙查詢請求的主要入口函數
    
    Args:
        query_data (dict): 包含用戶查詢資訊的字典
            - messages: 用戶訊息列表
            - user_id: 用戶唯一識別碼
            - thread_id: 聊天會話識別碼
            
    Returns:
        str: 處理後的回應內容
        
    功能說明：
    - 整合聊天歷史以維持對話連貫性
    - 執行 LangGraph 工作流程
    - 處理各種類型的用戶查詢
    - 返回最終的回應內容
    """
    # 創建工作流程實例
    app = create_vocab_chain()
    chat_id = query_data["thread_id"]

    # 獲取最近的聊天記錄以維持上下文
    previous_messages = get_recent_chat_history(chat_id)
    
    # 將新訊息添加到歷史記錄中
    input_messages = previous_messages + query_data["messages"]

    # 準備輸入資料
    input_data = {
        "messages": input_messages,
        "context": {},
        "user_id": query_data["user_id"]
    }

    # 執行工作流程並獲取結果
    for output in app.stream(input_data):
        for key, value in output.items():
            # 可以在這裡添加調試輸出
            # if "messages" in value:
            #     value["messages"][-1].pretty_print()
            #     print('================================================================================')
            print()
    
    # 返回最終回應內容
    return value['messages'][-1].content


def generate_workflow_graph():
    """
    生成 LangGraph 工作流程的視覺化圖表
    
    Returns:
        graphviz.Digraph: 工作流程的圖形化表示
        
    功能說明：
    - 使用 Graphviz 創建工作流程圖
    - 顯示各個節點和它們之間的連接關係
    - 用於系統架構展示和調試
    - 幫助理解代理決策流程
    """
    # 創建有向圖
    dot = graphviz.Digraph(comment='Vocabulary Learning Workflow')
    dot.attr(rankdir='TB')  # 從上到下的布局
    
    # 添加節點
    dot.node('START', 'Start')
    dot.node('agent', 'Agent\n(Decision Making)')
    dot.node('tools', 'Tools\n(Search/Category/Quiz)')
    dot.node('generate', 'Generate Response')
    dot.node('END', 'End')
    
    # 添加邊（連接線）
    dot.edge('START', 'agent')
    dot.edge('agent', 'tools', 'needs tools')
    dot.edge('agent', 'generate', 'direct response')
    dot.edge('tools', 'generate', 'complete')
    dot.edge('generate', 'END')
    
    return dot


# 測試和調試區域
if __name__ == "__main__":
    """
    模組測試區域
    
    包含各種測試案例，用於驗證代理系統的功能：
    - 單字查詢測試
    - 類別學習測試
    - 測驗生成測試
    - 一般對話測試
    - 非英語學習問題處理測試
    """
    # 測試案例定義
    test_cases = [
        # 可以取消註釋以下測試案例進行功能驗證
        # {
        #     "name": "Word Search",
        #     "query": {
        #         "messages": [HumanMessage(content="resilient 是什麼意思")],
        #         "user_id": "test_user_1"
        #     }
        # },
        # {
        #     "name": "Category Search",
        #     "query": {
        #         "messages": [HumanMessage(content="想了解商業相關單字")],
        #         "user_id": "test_user_1"
        #     }
        # },
        # {
        #     "name": "Quiz Generation",
        #     "query": {
        #         "messages": [HumanMessage(content="我想測驗科技相關的單字")],
        #         "user_id": "test_user_1"
        #     }
        # },
        # {
        #     "name": "General Conversation",
        #     "query": {
        #         "messages": [HumanMessage(content="我想學習英文，但不知道從何開始？")],
        #         "user_id": "test_user_1"
        #     }
        # },
        # {
        #     "name": "Non-English Learning Question",
        #     "query": {
        #         "messages": [HumanMessage(content="今天天氣如何？")],
        #         "user_id": "test_user_1"
        #     }
        # }
        {
            "name": "General Conversation",
            "query": {
                "messages": [HumanMessage(content="給我一個高深的單字，一個就好")],
                "user_id": "test",
                "thread_id": "3dc6d9cd-95ef-44fc-aa30-935f6592c648"
            }
        },
        {
            "name": "Follow-up Question", 
            "query": {
                "messages": [HumanMessage(content="針對這個單字給我一個例句")],
                "user_id": "test",
                "thread_id": "3dc6d9cd-95ef-44fc-aa30-935f6592c648"
            }
        }
    ]

    # 執行測試案例
    for test in test_cases:
        print(f"\n=== Test Case: {test['name']} ===")
        response = process_vocab_query(test["query"])
        db.add_chat_message('3dc6d9cd-95ef-44fc-aa30-935f6592c648', "assistant", response)
        print("\nResponse:", response)