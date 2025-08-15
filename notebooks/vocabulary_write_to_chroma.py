"""
詞彙向量資料庫寫入範例程式

這個程式展示了如何將生成的詞彙文件載入到 Chroma 向量資料庫中。
主要功能包括：
1. 讀取 data/vocabulary 目錄下的所有詞彙文件
2. 將詞彙內容轉換為向量嵌入
3. 存儲到 Chroma 向量資料庫中
4. 支援基於主題的元資料標記

技術特點：
- 使用 OpenAI 的 text-embedding-3-small 模型生成向量嵌入
- 支援批量處理多個詞彙文件
- 自動提取主題資訊作為元資料
- 持久化存儲到本地 Chroma 資料庫

使用場景：
- 建立詞彙檢索系統
- 支援語義搜索功能
- 為 RAG (檢索增強生成) 系統提供詞彙知識庫
- 主題式詞彙分類和檢索

作者：VocabVoyage 團隊
日期：2024年
"""

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
import time

# ============================================================================
# 配置和常數
# ============================================================================

# 詞彙文件目錄
VOCABULARY_DIR = "data/vocabulary"

# Chroma 資料庫目錄
CHROMA_DB_DIR = "./data/chroma_db"

# Chroma 集合名稱
COLLECTION_NAME = "vocabulary_v1"

# OpenAI 嵌入模型
EMBEDDING_MODEL = "text-embedding-3-small"

# 支援的文件副檔名
SUPPORTED_EXTENSIONS = ['.txt']

# ============================================================================
# 詞彙文件載入功能
# ============================================================================

def load_vocabulary_files(vocab_dir: str = VOCABULARY_DIR) -> List[Document]:
    """
    載入詞彙目錄下的所有文件並轉換為 Document 對象
    
    這個函數會遍歷指定目錄下的所有 .txt 文件，讀取內容並創建
    LangChain Document 對象，同時提取主題資訊作為元資料。
    
    Args:
        vocab_dir (str): 詞彙文件目錄路徑
        
    Returns:
        List[Document]: Document 對象列表
        
    Raises:
        FileNotFoundError: 當詞彙目錄不存在時
        Exception: 當讀取文件時發生錯誤
    """
    try:
        print(f"📂 開始載入詞彙文件：{vocab_dir}")
        
        # 檢查目錄是否存在
        vocab_path = Path(vocab_dir)
        if not vocab_path.exists():
            raise FileNotFoundError(f"詞彙目錄不存在：{vocab_dir}")
        
        documents = []
        processed_files = 0
        skipped_files = 0
        
        # 遍歷目錄下的所有文件
        for file_path in vocab_path.iterdir():
            if file_path.is_file() and file_path.suffix in SUPPORTED_EXTENSIONS:
                try:
                    print(f"  📄 正在處理：{file_path.name}")
                    
                    # 讀取文件內容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 檢查文件是否為空
                    if not content.strip():
                        print(f"    ⚠️  跳過空文件：{file_path.name}")
                        skipped_files += 1
                        continue
                    
                    # 從文件名中提取主題
                    topic = extract_topic_from_filename(file_path.name)
                    
                    # 從文件內容中提取額外的元資料
                    metadata = extract_metadata_from_content(content, topic)
                    
                    # 創建 Document 對象
                    doc = Document(
                        page_content=content,
                        metadata=metadata
                    )
                    
                    documents.append(doc)
                    processed_files += 1
                    
                    print(f"    ✅ 成功載入，內容長度：{len(content)} 字符")
                    
                except Exception as e:
                    print(f"    ❌ 載入文件失敗：{file_path.name} - {str(e)}")
                    skipped_files += 1
                    continue
            else:
                # 跳過不支援的文件類型
                if file_path.is_file():
                    print(f"  ⏭️  跳過不支援的文件：{file_path.name}")
                    skipped_files += 1
        
        print(f"\n📊 載入統計：")
        print(f"  ✅ 成功載入：{processed_files} 個文件")
        print(f"  ⏭️  跳過文件：{skipped_files} 個文件")
        print(f"  📝 總文檔數：{len(documents)} 個")
        
        return documents
        
    except FileNotFoundError as e:
        print(f"❌ 目錄錯誤：{e}")
        return []
    except Exception as e:
        print(f"❌ 載入詞彙文件時發生錯誤：{str(e)}")
        return []

def extract_topic_from_filename(filename: str) -> str:
    """
    從文件名中提取主題名稱
    
    Args:
        filename (str): 文件名
        
    Returns:
        str: 提取的主題名稱
    """
    # 移除副檔名
    topic = Path(filename).stem
    
    # 將底線轉換為空格並轉換為標題格式
    topic = topic.replace('_', ' ').title()
    
    return topic

def extract_metadata_from_content(content: str, topic: str) -> Dict[str, str]:
    """
    從文件內容中提取元資料
    
    Args:
        content (str): 文件內容
        topic (str): 主題名稱
        
    Returns:
        Dict[str, str]: 元資料字典
    """
    metadata = {
        "topic": topic,
        "content_type": "vocabulary",
        "language": "en-zh",  # 英文-中文
    }
    
    # 統計詞彙數量（簡單計算行數）
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    vocab_lines = [line for line in lines if '-' in line]  # 包含翻譯的行
    
    metadata["estimated_vocab_count"] = str(len(vocab_lines))
    metadata["total_lines"] = str(len(lines))
    
    # 檢查是否包含主題標記
    if "主題：" in content or "Topic:" in content:
        metadata["has_topic_header"] = "true"
    else:
        metadata["has_topic_header"] = "false"
    
    return metadata

# ============================================================================
# 向量資料庫操作功能
# ============================================================================

def create_vector_store(documents: List[Document], 
                       collection_name: str = COLLECTION_NAME,
                       persist_dir: str = CHROMA_DB_DIR) -> Optional[Chroma]:
    """
    創建 Chroma 向量資料庫並存儲文檔
    
    Args:
        documents (List[Document]): 要存儲的文檔列表
        collection_name (str): 集合名稱
        persist_dir (str): 持久化目錄
        
    Returns:
        Optional[Chroma]: 創建的向量存儲對象，失敗時返回 None
    """
    try:
        print(f"🔄 開始創建向量資料庫...")
        print(f"  📍 集合名稱：{collection_name}")
        print(f"  📁 存儲目錄：{persist_dir}")
        print(f"  🤖 嵌入模型：{EMBEDDING_MODEL}")
        
        # 確保存儲目錄存在
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        
        # 初始化嵌入模型
        print("  🔧 初始化嵌入模型...")
        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        
        # 創建向量存儲
        print(f"  📊 開始處理 {len(documents)} 個文檔...")
        start_time = time.time()
        
        vectorstore = Chroma.from_documents(
            documents=documents,
            collection_name=collection_name,
            embedding=embeddings,
            persist_directory=persist_dir
        )
        
        processing_time = time.time() - start_time
        print(f"  ✅ 向量資料庫創建完成，耗時：{processing_time:.2f} 秒")
        
        return vectorstore
        
    except Exception as e:
        print(f"❌ 創建向量資料庫時發生錯誤：{str(e)}")
        return None

def verify_vector_store(vectorstore: Chroma) -> bool:
    """
    驗證向量資料庫的完整性
    
    Args:
        vectorstore (Chroma): 向量存儲對象
        
    Returns:
        bool: 驗證成功返回 True，失敗返回 False
    """
    try:
        print("🔍 驗證向量資料庫...")
        
        # 獲取集合資訊
        collection = vectorstore._collection
        doc_count = collection.count()
        
        print(f"  📊 文檔總數：{doc_count}")
        
        # 測試檢索功能
        print("  🔎 測試檢索功能...")
        test_query = "vocabulary learning"
        results = vectorstore.similarity_search(test_query, k=3)
        
        print(f"  📝 測試查詢：'{test_query}'")
        print(f"  📋 返回結果：{len(results)} 個文檔")
        
        if results:
            print("  ✅ 檢索功能正常")
            
            # 顯示第一個結果的元資料
            first_result = results[0]
            print(f"  📄 第一個結果主題：{first_result.metadata.get('topic', 'Unknown')}")
            
            return True
        else:
            print("  ⚠️  檢索未返回結果")
            return False
            
    except Exception as e:
        print(f"❌ 驗證向量資料庫時發生錯誤：{str(e)}")
        return False

# ============================================================================
# 統計和報告功能
# ============================================================================

def generate_statistics(documents: List[Document]) -> Dict:
    """
    生成詞彙處理統計資訊
    
    Args:
        documents (List[Document]): 處理的文檔列表
        
    Returns:
        Dict: 統計資訊字典
    """
    stats = {
        "total_documents": len(documents),
        "topics": {},
        "total_content_length": 0,
        "estimated_total_vocab": 0
    }
    
    for doc in documents:
        topic = doc.metadata.get("topic", "Unknown")
        content_length = len(doc.page_content)
        vocab_count = int(doc.metadata.get("estimated_vocab_count", "0"))
        
        # 統計主題資訊
        if topic not in stats["topics"]:
            stats["topics"][topic] = {
                "document_count": 0,
                "content_length": 0,
                "vocab_count": 0
            }
        
        stats["topics"][topic]["document_count"] += 1
        stats["topics"][topic]["content_length"] += content_length
        stats["topics"][topic]["vocab_count"] += vocab_count
        
        # 總計
        stats["total_content_length"] += content_length
        stats["estimated_total_vocab"] += vocab_count
    
    return stats

def print_statistics(stats: Dict):
    """
    打印統計資訊
    
    Args:
        stats (Dict): 統計資訊字典
    """
    print("\n📊 詞彙處理統計報告")
    print("=" * 60)
    
    print(f"📝 總文檔數：{stats['total_documents']}")
    print(f"🔤 估計詞彙總數：{stats['estimated_total_vocab']:,}")
    print(f"📄 總內容長度：{stats['total_content_length']:,} 字符")
    print(f"🏷️  主題數量：{len(stats['topics'])}")
    
    print(f"\n📋 各主題詳細統計：")
    print("-" * 60)
    
    for topic, topic_stats in stats["topics"].items():
        print(f"  📚 {topic}:")
        print(f"    文檔數：{topic_stats['document_count']}")
        print(f"    詞彙數：{topic_stats['vocab_count']:,}")
        print(f"    內容長度：{topic_stats['content_length']:,} 字符")
        print()

def save_statistics(stats: Dict, output_path: str = "vocabulary_import_stats.json"):
    """
    保存統計資訊到文件
    
    Args:
        stats (Dict): 統計資訊字典
        output_path (str): 輸出文件路徑
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"📊 統計資訊已保存到：{output_path}")
        
    except Exception as e:
        print(f"❌ 保存統計資訊時發生錯誤：{str(e)}")

# ============================================================================
# 主程式邏輯
# ============================================================================

def main():
    """
    主程式函數
    
    執行完整的詞彙向量化流程：
    1. 載入詞彙文件
    2. 創建向量資料庫
    3. 驗證資料庫完整性
    4. 生成統計報告
    """
    print("VocabVoyage 詞彙向量資料庫建立工具")
    print("=" * 60)
    
    # 步驟 1：載入詞彙文件
    print("\n🔄 步驟 1：載入詞彙文件")
    print("-" * 30)
    
    documents = load_vocabulary_files()
    
    if not documents:
        print("❌ 沒有載入到任何詞彙文件，程式結束")
        return
    
    # 步驟 2：生成統計資訊
    print("\n🔄 步驟 2：生成統計資訊")
    print("-" * 30)
    
    stats = generate_statistics(documents)
    print_statistics(stats)
    save_statistics(stats)
    
    # 步驟 3：創建向量資料庫
    print("\n🔄 步驟 3：創建向量資料庫")
    print("-" * 30)
    
    vectorstore = create_vector_store(documents)
    
    if not vectorstore:
        print("❌ 向量資料庫創建失敗，程式結束")
        return
    
    # 步驟 4：驗證資料庫
    print("\n🔄 步驟 4：驗證資料庫完整性")
    print("-" * 30)
    
    if verify_vector_store(vectorstore):
        print("✅ 資料庫驗證成功")
    else:
        print("⚠️  資料庫驗證失敗，但資料庫已創建")
    
    # 完成
    print("\n" + "=" * 60)
    print("🎉 詞彙向量資料庫建立完成！")
    print("=" * 60)
    print(f"📁 資料庫位置：{CHROMA_DB_DIR}")
    print(f"🏷️  集合名稱：{COLLECTION_NAME}")
    print(f"📊 處理文檔：{len(documents)} 個")
    print(f"🔤 估計詞彙：{stats['estimated_total_vocab']:,} 個")

# ============================================================================
# 輔助功能
# ============================================================================

def check_prerequisites():
    """檢查必要的依賴和環境"""
    print("🔍 檢查系統環境...")
    
    # 檢查 OpenAI API 金鑰
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  警告：未設置 OPENAI_API_KEY 環境變數")
        print("   請確保已設置 OpenAI API 金鑰")
        return False
    
    # 檢查詞彙目錄
    if not Path(VOCABULARY_DIR).exists():
        print(f"❌ 錯誤：詞彙目錄不存在：{VOCABULARY_DIR}")
        print("   請先運行詞彙生成程式或手動創建詞彙文件")
        return False
    
    print("✅ 環境檢查通過")
    return True

def show_help():
    """顯示幫助資訊"""
    print("VocabVoyage 詞彙向量資料庫建立工具")
    print("=" * 60)
    print("\n功能說明：")
    print("  這個工具將詞彙文件轉換為向量嵌入並存儲到 Chroma 資料庫中")
    print("  支援批量處理和主題分類")
    print("\n使用方法：")
    print(f"  python {os.path.basename(__file__)}           # 執行完整流程")
    print(f"  python {os.path.basename(__file__)} --help    # 顯示幫助")
    print(f"  python {os.path.basename(__file__)} --check   # 檢查環境")
    print("\n前置條件：")
    print("  1. 設置 OPENAI_API_KEY 環境變數")
    print("  2. 在 data/vocabulary/ 目錄下準備詞彙文件")
    print("  3. 安裝必要的 Python 套件")
    print("\n輸出：")
    print(f"  - 向量資料庫：{CHROMA_DB_DIR}")
    print("  - 統計報告：vocabulary_import_stats.json")

# ============================================================================
# 程式入口點
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # 檢查命令列參數
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            show_help()
            sys.exit(0)
        elif sys.argv[1] == "--check":
            if check_prerequisites():
                print("✅ 所有前置條件都已滿足")
            else:
                print("❌ 請解決上述問題後再運行程式")
            sys.exit(0)
    
    # 檢查前置條件
    if not check_prerequisites():
        print("\n請使用 --help 查看詳細說明")
        sys.exit(1)
    
    # 執行主程式
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程式已中斷")
    except Exception as e:
        print(f"\n❌ 程式執行時發生未預期的錯誤：{str(e)}")
        import traceback
        traceback.print_exc()