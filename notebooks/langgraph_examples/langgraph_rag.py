"""
LangGraph RAG (檢索增強生成) 範例程式

這個範例展示了如何使用 LangGraph 建立一個具有檢索增強生成功能的智能代理。
代理能夠：
1. 接收用戶問題
2. 決定是否需要檢索相關文檔
3. 評估檢索到的文檔相關性
4. 根據需要重寫問題以獲得更好的檢索結果
5. 基於相關文檔生成最終答案

技術架構：
- LangGraph: 用於建立複雜的代理工作流程
- Chroma: 向量資料庫，用於文檔檢索
- OpenAI: 提供嵌入模型和語言模型
- 狀態管理: 使用 TypedDict 管理對話狀態

作者：VocabVoyage 團隊
日期：2024年
"""

# ============================================================================ 
# 資料建立部分（已註解）
# 這部分程式碼用於初始化向量資料庫，通常只需要執行一次
# ============================================================================ 

# from langchain_chroma import Chroma
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.document_loaders import WebBaseLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# # 定義要載入的網頁 URL
# urls = [
#     "https://lilianweng.github.io/posts/2023-06-23-agent/",
#     "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
#     "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
# ]

# # 載入網頁內容
# docs = [WebBaseLoader(url).load() for url in urls]
# docs_list = [item for sublist in docs for item in sublist]

# # 文本分割器，將長文檔分割成較小的塊
# text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
#     chunk_size=100, chunk_overlap=50
# )
# doc_splits = text_splitter.split_documents(docs_list)

# # 建立向量資料庫
# vectorstore = Chroma.from_documents(
#     documents=doc_splits,
#     collection_name="rag-example",
#     embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
#     persist_directory="./data/chroma_db"
# )

# ============================================================================ 
# 資料查詢部分（已註解）
# 這部分程式碼用於檢查向量資料庫的內容
# ============================================================================ 

# import chromadb

# # 連接到持久化的 Chroma 資料庫
# client = chromadb.PersistentClient(path="./data/chroma_db")
# collection = client.get_collection("rag-example")

# # 獲取所有文檔
# results = collection.get()

# # 查看資料庫內容預覽
# results_ = collection.peek()
# print(results_)

# # 統計文檔數量
# doc_count = collection.count()
# print(f"資料庫中的文檔數量: {doc_count}")

# ============================================================================ 
# 主要 RAG 系統實作
# ============================================================================ 

from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from typing import Annotated, Literal, Sequence
from langchain import hub
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langgraph.prebuilt import tools_condition
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
import pprint

# ============================================================================ 
# 向量資料庫和檢索器設置
# ============================================================================ 

# 載入已存在的向量資料庫
vectorstore = Chroma(
    persist_directory="./data/chroma_db",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
    collection_name="rag-example"
)

# 創建檢索器，用於從向量資料庫中檢索相關文檔
retriever = vectorstore.as_retriever()

# 創建檢索工具，將檢索器包裝成 LangGraph 可使用的工具
retriever_tool = create_retriever_tool(
    retriever=retriever,
    name="retrieve_blog_posts",
    description="搜索並返回有關 Lilian Weng 在 LLM 代理、提示工程和對 LLM 的對抗性攻擊的博客文章的信息。",
)
tools = [retriever_tool]

# ============================================================================ 
# 狀態定義
# ============================================================================ 

class AgentState(TypedDict):
    """
    代理狀態類型定義
    
    Attributes:
        messages: 對話訊息列表，使用 add_messages 函數進行累積
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]

# ============================================================================ 
# 節點函數定義
# ============================================================================ 

def grade_documents(state) -> Literal["generate", "rewrite"]:
    """
    評估檢索到的文檔與用戶問題的相關性
    
    這個函數使用 LLM 來判斷檢索到的文檔是否與用戶的問題相關。
    如果相關，則進入生成答案階段；如果不相關，則重寫問題以獲得更好的檢索結果。
    
    Args:
        state: 當前的代理狀態，包含對話訊息
        
    Returns:
        str: "generate" 如果文檔相關，"rewrite" 如果文檔不相關
    """
    print(" *** 檢查文檔相關性 *** ")

    # 定義相關性評分的資料模型
    class grade(BaseModel):
        """相關性檢查的二元評分模型"""
        binary_score: str = Field(description="相關性評分 'yes' 或 'no'")

    # 初始化 LLM 模型
    model = ChatOpenAI(temperature=0, model="gpt-4o-mini", streaming=True)
    
    # 將模型與結構化輸出綁定
    llm_with_tool = model.with_structured_output(grade)

    # 定義評估提示詞
    prompt = PromptTemplate(
        template="""你是一個評分員，評估檢索到的文檔與用戶問題的相關性。\n 
        這是檢索到的文檔：\n\n {context} \n\n
        這是用戶問題：{question} \n
        如果文檔包含與用戶問題相關的關鍵詞或語義含義，將其評為相關。\n
        給出二元評分 'yes' 或 'no' 來表示文檔是否與問題相關。""",
        input_variables=["context", "question"],
    )

    # 建立處理鏈
    chain = prompt | llm_with_tool

    # 從狀態中提取訊息
    messages = state["messages"]
    last_message = messages[-1]
    question = messages[0].content  # 原始問題
    docs = last_message.content     # 檢索到的文檔

    # 執行相關性評估
    scored_result = chain.invoke({"question": question, "context": docs})
    score = scored_result.binary_score

    # 根據評分決定下一步行動
    if score == "yes":
        print(" *** 決定：文檔相關，進入生成階段 *** ")
        return "generate"
    else:
        print(" *** 決定：文檔不相關，需要重寫問題 *** ")
        print(f"評分結果：{score}")
        return "rewrite"

def agent(state):
    """
    主要代理節點，負責決策和工具調用
    
    這個函數是整個工作流程的核心，它接收用戶問題並決定是否需要使用檢索工具。
    代理會分析問題的性質，如果需要外部知識，就會調用檢索工具。
    
    Args:
        state: 當前的代理狀態
        
    Returns:
        dict: 包含代理回應的更新狀態
    """
    print(" *** 調用主代理 *** ")
    
    messages = state["messages"]
    
    # 初始化帶有工具綁定的 LLM
    model = ChatOpenAI(temperature=0, streaming=True, model="gpt-4o-mini")
    model = model.bind_tools(tools)
    
    # 生成回應
    response = model.invoke(messages)
    
    # 返回更新的狀態（以列表形式，因為會被添加到現有訊息列表中）
    return {"messages": [response]}

def rewrite(state):
    """
    重寫用戶問題以改善檢索效果
    
    當檢索到的文檔與問題不相關時，這個函數會重新表述問題，
    以便在下一次檢索時獲得更相關的結果。
    
    Args:
        state: 當前的代理狀態
        
    Returns:
        dict: 包含重寫問題的更新狀態
    """
    print(" *** 重寫問題以改善檢索 *** ")
    
    messages = state["messages"]
    question = messages[0].content  # 獲取原始問題

    # 建立重寫問題的提示訊息
    msg = [
        HumanMessage(
            content=f""" \n 
    查看輸入並嘗試推理潛在的語義意圖/含義。\n 
    這是初始問題：
    \n  ***  *** - \n
    {question} 
    \n  ***  *** - \n
    制定一個改進的問題：""",
        )
    ]

    # 使用 LLM 重寫問題
    model = ChatOpenAI(temperature=0, model="gpt-4o-mini", streaming=True)
    response = model.invoke(msg)
    
    return {"messages": [response]}

def generate(state):
    """
    基於檢索到的相關文檔生成最終答案
    
    這個函數使用檢索到的文檔作為上下文，結合用戶的原始問題，
    生成一個準確且有用的答案。
    
    Args:
        state: 當前的代理狀態
        
    Returns:
        dict: 包含生成答案的更新狀態
    """
    print(" *** 生成最終答案 *** ")
    
    messages = state["messages"]
    question = messages[0].content    # 原始問題
    last_message = messages[-1]
    docs = last_message.content       # 檢索到的文檔

    # 從 LangChain Hub 載入 RAG 提示詞模板
    prompt = hub.pull("rlm/rag-prompt")

    # 初始化 LLM
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, streaming=True)

    # 文檔格式化函數
    def format_docs(docs):
        """將文檔列表格式化為字符串"""
        return "\n\n".join(doc.page_content for doc in docs)

    # 建立 RAG 處理鏈
    rag_chain = prompt | llm | StrOutputParser()

    # 生成答案
    response = rag_chain.invoke({"context": docs, "question": question})
    
    return {"messages": [response]}

# ============================================================================ 
# 工作流程圖建立
# ============================================================================ 

# 建立狀態圖
workflow = StateGraph(AgentState)

# 添加節點
workflow.add_node("agent", agent)        # 主代理節點
retrieve = ToolNode([retriever_tool])
workflow.add_node("retrieve", retrieve)  # 檢索節點
workflow.add_node("rewrite", rewrite)    # 問題重寫節點
workflow.add_node("generate", generate)  # 答案生成節點

# 建立邊（定義節點之間的連接）
workflow.add_edge(START, "agent")        # 從開始節點到代理節點

# 條件邊：代理決定是否需要檢索
workflow.add_conditional_edges(
    "agent",
    tools_condition,  # 評估代理是否調用了工具
    {
        "tools": "retrieve",  # 如果調用了工具，進入檢索節點
        END: END,            # 如果沒有調用工具，結束流程
    },
)

# 條件邊：檢索後決定是否生成答案或重寫問題
workflow.add_conditional_edges(
    "retrieve",
    grade_documents,  # 評估檢索文檔的相關性
    # grade_documents 函數返回 "generate" 或 "rewrite"
)

# 直接邊
workflow.add_edge("generate", END)    # 生成答案後結束
workflow.add_edge("rewrite", "agent") # 重寫問題後回到代理

# 編譯工作流程圖
graph = workflow.compile()

# ============================================================================ 
# 可視化圖形（可選）
# ============================================================================ 

# 如果需要可視化工作流程圖，可以取消註解以下程式碼：
# from IPython.display import Image, display
# display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# ============================================================================ 
# 使用範例
# ============================================================================ 

if __name__ == "__main__":
    # 定義輸入訊息
    inputs = {
        "messages": [
            ("user", "Lilian Weng 說了什麼? 使用繁體中文回答"),
        ]
    }
    
    print("=== 開始 RAG 對話流程 ===")
    
    # 執行工作流程並輸出每個步驟的結果
    for output in graph.stream(inputs):
        for key, value in output.items():
            pprint.pprint(f"來自節點 '{key}' 的輸出:")
            pprint.pprint(" ===== ")
            pprint.pprint(value, indent=2, width=80, depth=None)
        pprint.pprint(" ========== ")
    
    print("=== RAG 對話流程結束 ===")