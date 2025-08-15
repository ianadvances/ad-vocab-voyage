


          
# VocabVoyage - 英語詞彙學習平台 (Chatbot)

![截圖 2025-05-02 下午5.09.43](https://hackmd.io/_uploads/HJ6gCZfell.png)

## 專案概述

VocabVoyage 是一個互動式英語詞彙學習平台，旨在幫助使用者透過 AI 對話、詞彙查詢和測驗等功能提升英語詞彙能力。該平台結合了大型語言模型 (LLM) 技術與結構化學習方法，為使用者提供個人化的英語學習體驗。

## 技術架構

### 前端技術
- **Streamlit**：用於構建互動式網頁界面
- **Markdown**：用於格式化文本顯示

### 後端技術
- **Python**：核心開發語言
- **Firebase Realtime Database**：主要資料儲存解決方案
- **LangChain & LangGraph**：用於構建 LLM 工作流程
- **OpenAI API**：提供 GPT 模型支援
- **Google Vertex AI**：提供 Gemini 模型支援

### 部署技術
- **Docker**：容器化應用程式
- **Google Cloud Run**：全代管式 Serverless 服務

## 系統架構圖

### 整體系統
```
+---------------------------------+
          (Streamlit App)         
+----------------+----------------+
                 |
                 v
+----------------+----------------+          
            (LangGraph)           
+----------------+----------------+
                 |
        +--------+--------+
        |                 |
        v                 v
+---------------+  +---------------+
     資料庫介面          LLM 服務    
    (Firebase)      （GPT/Gemini)    
+---------------+  +---------------+
```
### 資料流程
```
+-------------+     +-------------+     +-------------+
     用戶輸入     -->    Agent 決策   -->     工具處理     
+-------------+     +-------------+     +-------------+
                                               |
                                               v
+-------------+     +-------------+     +-------------+
     儲存回應     <--     生成回應     <--     檢索資料    
+-------------+     +-------------+     +-------------+
```

### LangGraph 流程
![VocabVoyage](https://hackmd.io/_uploads/B17kV-Mlll.png)


## 核心功能

### 1. 詞彙查詢

使用者可以查詢任何英文單字，系統會返回：
- 詞性和定義
- 例句
- 相關詞彙
- 使用建議

```python
SYSTEM_PROMPTS = {
"search": """
你是一個專業的英語教師。請使用繁體中文提供這個單字的詳細資訊，格式如下：
---
單字：[英文單字]
詞性：[說明詞性]
定義：[繁體中文定義]
例句：
-> [英文例句1]
-> [英文例句2]
相關詞彙：[相關英文詞彙（其詞性及繁體中文解釋）、相關英文詞彙（其詞性及繁體中文解釋）...](接續在後面就好，不要條列！)
使用建議：[單字使用建議的繁體中文說明]
---
請確保回應嚴格遵循以上格式，所有解釋都使用繁體中文。
""", ...}

def search_vocabulary(query: str) -> str:
    """處理單字查詢"""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    prompt = PromptTemplate(
        template=SYSTEM_PROMPTS["search"] + "\n\n查詢單字: {query}",
        input_variables=["query"]
    )
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"query": query})
    return response
```

### 2. 主題式詞彙學習

系統支援多種主題的詞彙學習，包括：
- 日常生活
- 工作與職業
- 旅行與交通
- 飲食與餐廳
- 教育與學習
- 科技與數位
- 健康與醫療
- 娛樂與休閒
- 環境與自然
- 社交關係

```python
SYSTEM_PROMPTS = {
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
""", ...}

def setup_rag():
    """設置 RAG 相關組件"""
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
        collection_name="vocabulary_v1"
    )
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 1}
    )

def get_category_vocabulary(category: str) -> str:
    """處理類別查詢"""
    retriever = setup_rag()
    docs = retriever.invoke(category)
    context = "\n".join(doc.page_content for doc in docs)
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    prompt = PromptTemplate(
        template=SYSTEM_PROMPTS["category"],
        input_variables=["context"]
    )
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"context": context})
    return response
```

### 3. 互動式詞彙測驗

系統能夠根據用戶學習的詞彙自動生成測驗，包括：
- 選擇題：測試單字的定義和用法理解
- 填空題：測試單字在語境中的正確使用
- 配對題：測試單字與其定義的對應關係

```python
def generate_quiz(category: str) -> str:
    """生成類別測驗"""
    retriever = setup_rag()
    docs = retriever.invoke(category)
    context = "\n".join(doc.page_content for doc in docs)
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    prompt = PromptTemplate(
        template=SYSTEM_PROMPTS["quiz"],
        input_variables=["context"]
    )
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"context": context})
    return response
```

### 4. 個人詞彙本管理

使用者可以：
- 添加新單字到個人詞彙本
- 查看已保存的單字列表
- 刪除不需要的單字

```python
def add_vocabulary(self, user_id: str, word: str, definition: str, 
                  examples: List[str], notes: str = ""):
    """添加新單字到用戶的詞彙表"""
    vocab_ref = self.db.child('vocabulary').child(user_id)
    
    # 檢查單字是否已存在
    existing_vocab = vocab_ref.order_by_child('word').equal_to(word).get()
    if existing_vocab:
        raise ValueError(f"單字 '{word}' 已經存在於您的單字本中")
    
    # 添加新單字
    new_vocab = {
        'word': word,
        'definition': definition,
        'examples': examples,
        'notes': notes,
        'created_at': str(datetime.now())
    }
    vocab_ref.push().set(new_vocab)
    return True
```

### 5. 聊天式學習

使用者可以通過自然語言對話方式：
- 詢問英語學習相關問題
- 獲取詞彙解釋和用法建議
- 進行主題式詞彙學習
- 生成並參與詞彙測驗
- 撰寫或修飾文章

### 6. 聊天紀錄管理
- 聊天室新增/刪除
- 聊天室切換
- 聊天室改名

## 技術亮點

### 1. Agent

採用 LangGraph 構建的 Agent 系統，能夠：
- 理解用戶意圖
- 選擇合適的工具回應查詢
- 生成結構化的學習內容

```python
def agent(state: VocabState):
    """
    代理節點：決定是否使用工具或直接生成回應
    """
    messages = state["messages"]

    system_message = """你是一個英語學習助手的路由器。
    你的唯一任務是決定是否使用提供的工具來回答用戶的問題。
    - 如果問題需要用工具回答，請使用適當的工具
    - 如果問題不需要工具（比如一般英語學習建議或非英語相關問題），請回覆 "DIRECT_RESPONSE"
    - 注意不要輕易的使用 category_vocabulary_list 跟 vocabulary_quiz_generator 這兩個工具，要確定你真的必須使用它們再使用
    不要直接回答用戶的問題，只需決定使用工具或返回標記。"""
    messages = [HumanMessage(content=system_message)] + messages

    model = ChatOpenAI(temperature=0.7, model="gpt-4o-mini")
    model = model.bind_tools(tools)
    response = model.invoke(messages)
    return {
        "messages": [response],
        "context": state["context"],
        "user_id": state["user_id"]
    }
```

### 2. Tools

定義 Tools 讓 Agent 可選擇使用

```python
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
        return_direct=True
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
        return_direct=True
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
        return_direct=True
    )
]
```

### 3. LangGraph 圖
定義「狀態、節點、邊」構建為圖
```python
# 定義狀態
class VocabState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    context: dict
    user_id: str

def create_vocab_chain():
    """創建主要工作流程"""
    
    # 創建工具節點
    tool_node = ToolNode(tools=tools)
    
    # 建立工作流程圖
    workflow = StateGraph(VocabState)
    
    # 添加節點
    workflow.add_node("agent", agent)
    workflow.add_node("tools", tool_node)
    workflow.add_node("generate", generate_response)
    
    # 添加邊
    workflow.add_edge(START, "agent")
    
    # 從代理到工具或生成的條件邊
    workflow.add_conditional_edges(
        "agent",
        tools_condition,
        {
            "tools": "tools",
            END: "generate",
        }
    )
    
    # 工具節點到生成節點
    workflow.add_edge("tools", "generate")
    
    workflow.add_edge("generate", END)

    # 編譯時加入 checkpointer
    return workflow.compile()
```

### 4. 容器化部署

使用 Docker 容器化應用程式，確保：
- 環境一致性
- 簡化部署流程
- 提高可擴展性

```dockerfile
# 使用官方 Python 3.11 映像作為基礎
FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 安裝 Poetry
RUN pip install poetry==1.7.1

# 複製 pyproject.toml 和 poetry.lock 文件（如果存在）
COPY pyproject.toml poetry.lock* ./

# 安裝項目依賴
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# 複製項目文件
COPY . .

# 設置環境變量
ENV PORT 8080

# 運行應用
CMD streamlit run --server.port $PORT app.py
```

## 未來展望

1. **多語言支援**：擴展至其他語言學習
2. **語音互動**：添加語音識別和合成功能
3. **學習進度分析**：提供詳細的學習統計和建議
4. **社交學習功能**：支援用戶之間的詞彙分享和競賽
5. **移動應用開發**：開發原生移動應用提升可訪問性

## 結論

VocabVoyage 是一個結合現代 AI 技術與教育理念的英語詞彙學習平台，通過個人化、互動式的學習體驗幫助用戶有效提升英語詞彙量和應用能力。該項目展示了在開發、AI 應用和教育科技領域的綜合能力。
