"""
LangGraph 工具使用範例程式

這個範例展示了如何使用 LangGraph 建立一個具有多種工具的智能代理。
代理具備以下功能：
1. 數學計算工具 - 執行基本的四則運算
2. 日期轉換工具 - 將日期格式進行轉換
3. 人工協助請求 - 當遇到超出能力範圍的問題時請求人工介入
4. 記憶功能 - 使用檢查點保存對話狀態
5. 中斷機制 - 在需要人工介入時暫停執行

技術特點：
- 狀態管理：使用 TypedDict 定義複雜的狀態結構
- 工具整合：展示如何將自定義函數包裝為 LangGraph 工具
- 條件路由：根據不同情況選擇不同的執行路徑
- 檢查點機制：實現對話狀態的持久化存儲
- 中斷處理：支援人工介入的工作流程

作者：VocabVoyage 團隊
日期：2024年
"""

from typing import Annotated, Literal
import re
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langchain.tools import Tool
from pydantic import BaseModel
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# ============================================================================ 
# 狀態定義
# ============================================================================ 

class State(TypedDict):
    """
    代理狀態類型定義
    
    Attributes:
        messages: 對話訊息列表，自動累積新訊息
        ask_human: 布林值，指示是否需要人工協助
    """
    messages: Annotated[list, add_messages]
    ask_human: bool

# ============================================================================ 
# 請求協助模型定義
# ============================================================================ 

class RequestAssistance(BaseModel):
    """
    請求專家協助的資料模型
    
    當代理遇到無法處理的問題或需要超出其權限的支援時，
    會使用這個模型來結構化請求協助的內容。
    """
    request: str = "請求專家協助。當無法直接回答或需要超出權限的支援時使用。"

# ============================================================================ 
# 自定義工具函數
# ============================================================================ 

def math_calculator(expression: str) -> str:
    """
    執行基本的數學計算工具
    
    這個函數支援基本的四則運算，包括加法、減法、乘法和除法。
    使用正則表達式解析數學表達式，並按順序執行運算。
    
    Args:
        expression (str): 數學表達式，格式如 "10 + 5" 或 "15.5 * 3 - 7.2"
        
    Returns:
        str: 計算結果或錯誤訊息
        
    Examples:
        >>> math_calculator("10 + 5")
        "計算結果：15.0"
        >>> math_calculator("20 / 0")
        "錯誤：除數不能為零。"
    """
    try:
        # 使用正則表達式提取數字和運算符
        # 支援整數和小數，以及基本運算符
        parts = re.findall(r'(\d+(?:\.\d+)?|\+|\-|\*|\/)', expression)
        
        if len(parts) < 3:
            return "錯誤：表達式格式不正確。請提供至少兩個數字和一個運算符。"
        
        # 從第一個數字開始計算
        result = float(parts[0])
        
        # 按順序處理運算符和操作數
        for i in range(1, len(parts), 2):
            if i + 1 >= len(parts):
                break
                
            operator = parts[i]
            operand = float(parts[i + 1])
            
            # 執行相應的運算
            if operator == '+':
                result += operand
            elif operator == '-':
                result -= operand
            elif operator == '*':
                result *= operand
            elif operator == '/':
                if operand == 0:
                    return "錯誤：除數不能為零。"
                result /= operand
            else:
                return f"錯誤：不支援的運算符 '{operator}'"
        
        return f"計算結果：{result}"
        
    except ValueError as e:
        return f"錯誤：數字格式不正確 - {str(e)}"
    except Exception as e:
        return f"計算錯誤：{str(e)}"

def date_converter(date_string: str, output_format: str = "%Y年%m月%d日") -> str:
    """
    日期格式轉換工具
    
    將標準的 ISO 日期格式 (YYYY-MM-DD) 轉換為指定的輸出格式。
    預設輸出格式為繁體中文的年月日格式。
    
    Args:
        date_string (str): 輸入日期字符串，格式為 YYYY-MM-DD
        output_format (str): 輸出格式，使用 Python strftime 格式
        
    Returns:
        str: 轉換後的日期字符串或錯誤訊息
        
    Examples:
        >>> date_converter("2023-11-08")
        "2023年11月08日"
        >>> date_converter("2023-11-08", "%m/%d/%Y")
        "11/08/2023"
    """
    try:
        # 解析輸入的日期字符串
        date_obj = datetime.strptime(date_string, "%Y-%m-%d")
        
        # 轉換為指定格式
        formatted_date = date_obj.strftime(output_format)
        
        return f"轉換結果：{formatted_date}"
        
    except ValueError:
        return "錯誤：日期格式不正確。請使用 YYYY-MM-DD 格式，例如：2023-11-08"
    except Exception as e:
        return f"日期轉換錯誤：{str(e)}"

# ============================================================================ 
# 工具建立和配置
# ============================================================================ 

# 建立數學計算工具
math_tool = Tool(
    name="math_calculator",
    description="執行基本的數學計算，包括加法(+)、減法(-)、乘法(*)和除法(/)。輸入格式：'數字 運算符 數字'，例如：'10 + 5' 或 '15.5 * 3'",
    func=math_calculator
)

# 建立日期轉換工具
date_tool = Tool(
    name="date_converter", 
    description="將日期從 YYYY-MM-DD 格式轉換為繁體中文格式。輸入格式：'YYYY-MM-DD'，例如：'2023-11-08'",
    func=date_converter
)

# 工具列表
tools = [math_tool, date_tool]

# ============================================================================ 
# LLM 設置和配置
# ============================================================================ 

# 初始化 OpenAI 語言模型
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

# 將工具和請求協助功能綁定到 LLM
llm_with_tools = llm.bind_tools(tools + [RequestAssistance])

# ============================================================================ 
# 節點函數定義
# ============================================================================ 

def chatbot(state: State):
    """
    聊天機器人主節點
    
    這是代理的核心節點，負責：
    1. 接收用戶輸入並生成回應
    2. 決定是否需要調用工具
    3. 判斷是否需要請求人工協助
    
    Args:
        state (State): 當前的對話狀態
        
    Returns:
        dict: 更新後的狀態，包含新的訊息和人工協助標誌
    """
    # 調用帶有工具的 LLM 生成回應
    response = llm_with_tools.invoke(state["messages"])
    
    # 檢查是否請求了人工協助
    ask_human = False
    if (
        response.tool_calls
        and response.tool_calls[0]["name"] == RequestAssistance.__name__
    ):
        ask_human = True
        print(" *** 代理請求人工協助 *** ")
    
    return {"messages": [response], "ask_human": ask_human}

def create_response(response: str, ai_message: AIMessage):
    """
    建立工具回應訊息
    
    這個輔助函數用於建立符合 LangGraph 格式的工具回應訊息。
    
    Args:
        response (str): 回應內容
        ai_message (AIMessage): 原始的 AI 訊息
        
    Returns:
        ToolMessage: 格式化的工具訊息
    """
    return ToolMessage(
        content=response,
        tool_call_id=ai_message.tool_calls[0]["id"],
    )

def human_node(state: State):
    """
    人工介入節點
    
    當代理請求人工協助時，這個節點會被激活。
    在實際應用中，這裡會暫停執行等待人工輸入。
    在這個範例中，我們提供一個預設的回應。
    
    Args:
        state (State): 當前的對話狀態
        
    Returns:
        dict: 更新後的狀態，重置人工協助標誌
    """
    new_messages = []
    
    # 如果最後一條訊息不是工具訊息，則建立一個預設回應
    if not isinstance(state["messages"][-1], ToolMessage):
        default_response = "抱歉，這個問題超出了我的處理能力範圍。建議您聯繫相關專家或查閱專業資料。"
        new_messages.append(
            create_response(default_response, state["messages"][-1])
        )
        print(f" *** 人工節點回應：{default_response} *** ")
    
    return {
        "messages": new_messages,
        "ask_human": False,
    }

# ============================================================================ 
# 路由邏輯定義
# ============================================================================ 

def select_next_node(state: State):
    """
    選擇下一個執行節點的路由函數
    
    根據當前狀態決定工作流程的下一步：
    1. 如果需要人工協助，路由到人工節點
    2. 如果有工具調用，路由到工具節點
    3. 否則結束對話
    
    Args:
        state (State): 當前的對話狀態
        
    Returns:
        str: 下一個節點的名稱或 END
    """
    # 優先檢查是否需要人工協助
    if state["ask_human"]:
        return "human"
    
    # 檢查是否有工具調用
    if state["messages"][-1].tool_calls:
        return "tools"
    
    # 沒有特殊情況，結束對話
    return END

# ============================================================================ 
# 工作流程圖建立
# ============================================================================ 

# 建立狀態圖
graph_builder = StateGraph(State)

# 添加節點
graph_builder.add_node("chatbot", chatbot)              # 聊天機器人主節點
graph_builder.add_node("tools", ToolNode(tools=tools)) # 工具執行節點
graph_builder.add_node("human", human_node)             # 人工介入節點

# 建立邊（定義節點之間的連接）
graph_builder.add_edge(START, "chatbot")  # 從開始節點到聊天機器人

# 條件邊：根據聊天機器人的輸出決定下一步
graph_builder.add_conditional_edges(
    "chatbot",
    select_next_node,
    {
        "human": "human",   # 需要人工協助
        "tools": "tools",   # 需要調用工具
        END: END           # 結束對話
    },
)

# 直接邊
graph_builder.add_edge("human", "chatbot")  # 人工處理後回到聊天機器人
graph_builder.add_edge("tools", "chatbot")  # 工具執行後回到聊天機器人

# ============================================================================ 
# 圖形編譯和記憶設置
# ============================================================================ 

# 建立記憶存儲器，用於保存對話狀態
memory = MemorySaver()

# 編譯圖形，設置檢查點和中斷點
graph = graph_builder.compile(
    checkpointer=memory,           # 啟用狀態檢查點
    interrupt_before=["human"],    # 在人工節點前中斷，等待輸入
)

# ============================================================================ 
# 可視化圖形（可選）
# ============================================================================ 

# 如果需要可視化工作流程圖，可以取消註解以下程式碼：
# from IPython.display import Image, display
# display(Image(graph.get_graph().draw_mermaid_png()))

# ============================================================================ 
# 使用範例和測試
# ============================================================================ 

def run_conversation_example():
    """執行完整的對話範例，展示各種功能"""
    
    # 設置對話配置（用於狀態管理）
    config = {"configurable": {"thread_id": "demo_conversation"}}
    
    print("=== LangGraph 工具使用範例開始 ===\n")
    
    # ========================================================================
    # 範例 1：基本對話
    # ========================================================================
    print("📝 範例 1：基本對話和介紹")
    print("-" * 50)
    
    events = graph.stream(
        {"messages": [("user", "你好，我正在學習 LangGraph。你能告訴我它的主要特點嗎？")]},
        config,
        stream_mode="values"
    )
    
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()
    
    print("\n")
    
    # ========================================================================
    # 範例 2：數學計算工具使用
    # ========================================================================
    print("🧮 範例 2：數學計算工具")
    print("-" * 50)
    
    events = graph.stream(
        {"messages": [("user", "太好了！現在，你能幫我計算 15.5 * 3 - 7.2 嗎？")]},
        config,
        stream_mode="values"
    )
    
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()
    
    print("\n")
    
    # ========================================================================
    # 範例 3：日期轉換工具使用
    # ========================================================================
    print("📅 範例 3：日期轉換工具")
    print("-" * 50)
    
    events = graph.stream(
        {"messages": [("user", "謝謝。接下來，你能將日期 2023-11-08 轉換為中文格式嗎？")]},
        config,
        stream_mode="values"
    )
    
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()
    
    print("\n")
    
    # ========================================================================
    # 範例 4：請求人工協助（超出能力範圍）
    # ========================================================================
    print("🆘 範例 4：請求人工協助")
    print("-" * 50)
    
    events = graph.stream(
        {"messages": [("user", "我需要你幫我審核並簽署一份重要的法律文件，這份文件涉及公司的重大決策。")]},
        config,
        stream_mode="values"
    )
    
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()
    
    print("\n")
    
    # ========================================================================
    # 展示對話歷史功能
    # ========================================================================
    print("📚 對話歷史回顧")
    print("-" * 50)
    
    # 獲取當前狀態
    current_state = graph.get_state(config)
    print(f"當前對話包含 {len(current_state.values['messages'])} 條訊息")
    
    # 展示狀態歷史（時間旅行功能）
    print("\n🕰️ 狀態歷史（時間旅行功能演示）：")
    history_count = 0
    for state in graph.get_state_history(config):
        history_count += 1
        if history_count <= 5:  # 只顯示前5個狀態
            print(f"狀態 {history_count}: 訊息數量={len(state.values['messages'])}, 下一步={state.next}")
    
    print(f"\n總共記錄了 {history_count} 個狀態快照")
    print("\n=== LangGraph 工具使用範例結束 ===")

def run_interactive_mode():
    """執行互動模式，允許用戶輸入問題"""
    
    config = {"configurable": {"thread_id": "interactive_session"}}
    
    print("=== LangGraph 互動模式 ===")
    print("輸入 'quit' 或 'exit' 結束對話")
    print("可以嘗試數學計算（如：10 + 5）或日期轉換（如：2023-12-25）")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n👤 您: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出', '結束']:
                print("👋 再見！")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 助手:")
            events = graph.stream(
                {"messages": [("user", user_input)]},
                config,
                stream_mode="values"
            )
            
            for event in events:
                if "messages" in event:
                    last_message = event["messages"][-1]
                    if hasattr(last_message, 'content'):
                        print(last_message.content)
            
        except KeyboardInterrupt:
            print("\n\n👋 對話已中斷，再見！")
            break
        except Exception as e:
            print(f"\n❌ 發生錯誤: {e}")

# ============================================================================ 
# 主程式執行
# ============================================================================ 

if __name__ == "__main__":
    import sys
    
    print("LangGraph 工具使用範例程式")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        # 互動模式
        run_interactive_mode()
    else:
        # 範例模式
        run_conversation_example()
        
        print("\n💡 提示：使用 --interactive 參數可以進入互動模式")
        print("   例如：python examples/langgraph_tools.py --interactive")