"""
詞彙生成器範例程式

這個程式展示了如何使用 AI 模型（Google Gemini）自動生成特定主題的英語詞彙表。
主要功能包括：
1. 針對不同主題生成相關的英語詞彙
2. 提供繁體中文翻譯和詞性標註
3. 避免重複詞彙的生成
4. 將生成的詞彙保存到文件中

技術特點：
- 使用 Google Vertex AI 的 Gemini 模型進行詞彙生成
- 支援多個主題的詞彙生成
- 自動檢測和避免重複詞彙
- 將結果保存為結構化的文本文件

使用場景：
- 英語學習應用的詞彙庫建立
- 主題式詞彙表的自動生成
- 語言學習資源的批量創建

作者：VocabVoyage 團隊
日期：2024年
"""

import time
import json
from vertexai.generative_models import GenerativeModel
from pathlib import Path
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# ============================================================================
# 配置和常數定義
# ============================================================================

# 定義要生成詞彙的主題列表
# 可以根據需要添加或修改主題
TOPICS = [
    "Daily Life",              # 日常生活
    "Work & Career",           # 工作與職業
    "Travel & Transportation", # 旅行與交通
    "Food & Dining",          # 食物與用餐
    "Education & Learning",    # 教育與學習
    "Technology & Digital",    # 科技與數位
    "Health & Medical",       # 健康與醫療
    "Entertainment & Leisure", # 娛樂與休閒
    "Environment & Nature",    # 環境與自然
    "Social Relationships"     # 社交關係
]

# 每個主題要生成的詞彙數量
WORDS_PER_TOPIC = 150

# API 請求之間的延遲時間（秒）
REQUEST_DELAY = 1

# ============================================================================
# 全域變數
# ============================================================================

# 用於儲存所有已生成的單字，避免重複
generated_words = set()

# ============================================================================
# 核心功能函數
# ============================================================================

def generate_vocabulary(topic: str) -> str:
    """
    為指定主題生成詞彙表
    
    使用 Google Gemini 模型生成特定主題的英語詞彙，包含繁體中文翻譯。
    
    Args:
        topic (str): 要生成詞彙的主題名稱
        
    Returns:
        str: 生成的詞彙內容，如果失敗則返回 None
        
    Raises:
        Exception: 當 API 調用失敗時拋出異常
    """
    try:
        # 建立所有主題的字串，並標記當前正在處理的主題
        all_topics_str = "\n".join([
            f"{'-> ' if t == topic else '   '}{t}" 
            for t in TOPICS
        ])
        
        # 建立詳細的提示詞，指導 AI 生成高品質的詞彙
        prompt = f"""我正在為以下主題創建詞彙表：

{all_topics_str}

目前正在生成主題：{topic}

請為 {topic} 生成 {WORDS_PER_TOPIC} 個中高級程度的英語單字或片語。要求：

1. 格式：每行一個詞彙，格式為「英文單字/片語 - 繁體中文翻譯 (詞性)」
2. 詞彙應該實用且常用
3. 包含不同詞性（名詞、動詞、形容詞、片語等）
4. 確保每個單字/片語：
   - 與當前主題「{topic}」高度相關
   - 不會太通用以至於可能出現在其他主題中
   - 在此主題內是唯一的，不重複
5. 對於可以作為不同詞性的單字，請標註所有可能的用法
6. 所有中文翻譯必須使用繁體中文字
7. 只提供詞彙列表，不需要額外的解釋或註釋

範例格式：
1. advocate - 提倡，倡導 (v.) / 擁護者，提倡者 (n.)
2. sustainable - 可持續的，永續的 (adj.)
3. ...

請開始生成："""

        # 初始化 Gemini 模型
        model = GenerativeModel('gemini-1.5-pro-001')
        
        # 發送請求並獲取回應
        print(f"  正在向 Gemini API 發送請求...")
        response = model.generate_content(prompt)
        content = response.text
        
        # 提取新生成的單字（取英文部分進行重複檢查）
        new_words = []
        for line in content.split('\n'):
            if '-' in line:
                # 提取英文部分並轉為小寫進行比較
                english_part = line.split('-')[0].strip().lower()
                # 移除行號（如果有的話）
                english_part = english_part.split('.', 1)[-1].strip()
                new_words.append(english_part)
        
        # 檢查是否有重複的單字
        duplicates = set(new_words) & generated_words
        if duplicates:
            print(f"  ⚠️  警告：在 {topic} 中發現重複單字：{duplicates}")
        
        # 更新全域單字集合
        generated_words.update(new_words)
        
        print(f"  ✅ 成功生成 {len(new_words)} 個詞彙")
        return content
        
    except Exception as e:
        print(f"  ❌ 生成 {topic} 詞彙時發生錯誤：{str(e)}")
        return None

def save_to_file(topic: str, content: str) -> bool:
    """
    將生成的詞彙內容保存到文件
    
    Args:
        topic (str): 主題名稱
        content (str): 要保存的詞彙內容
        
    Returns:
        bool: 保存成功返回 True，失敗返回 False
    """
    try:
        # 創建輸出目錄（如果不存在）
        output_dir = Path("data/vocabulary")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 將主題名稱轉換為適合的檔案名稱
        # 例如："Work & Career" -> "work_career.txt"
        filename = topic.lower().replace(" & ", "_").replace(" ", "_") + ".txt"
        file_path = output_dir / filename
        
        # 寫入文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"主題：{topic}\n")
            f.write("=" * 50 + "\n\n")
            f.write(content)
        
        print(f"  💾 成功保存詞彙到：{file_path}")
        
        # 保存已生成的單字列表（用於除錯和統計）
        debug_file = output_dir / "generated_words_list.json"
        with open(debug_file, "w", encoding="utf-8") as f:
            json.dump(
                list(generated_words), 
                f, 
                ensure_ascii=False, 
                indent=2,
                sort_keys=True
            )
        
        return True
        
    except Exception as e:
        print(f"  ❌ 保存 {topic} 文件時發生錯誤：{str(e)}")
        return False

def generate_statistics() -> dict:
    """
    生成詞彙生成的統計資訊
    
    Returns:
        dict: 包含統計資訊的字典
    """
    return {
        "total_topics": len(TOPICS),
        "total_unique_words": len(generated_words),
        "average_words_per_topic": len(generated_words) / len(TOPICS) if TOPICS else 0,
        "target_words_per_topic": WORDS_PER_TOPIC
    }

def save_statistics(stats: dict):
    """
    保存統計資訊到文件
    
    Args:
        stats (dict): 統計資訊字典
    """
    try:
        output_dir = Path("data/vocabulary")
        stats_file = output_dir / "generation_statistics.json"
        
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"📊 統計資訊已保存到：{stats_file}")
        
    except Exception as e:
        print(f"❌ 保存統計資訊時發生錯誤：{str(e)}")

# ============================================================================
# 主程式邏輯
# ============================================================================

def main():
    """
    主程式函數
    
    執行完整的詞彙生成流程：
    1. 遍歷所有主題
    2. 為每個主題生成詞彙
    3. 保存生成的內容
    4. 生成統計報告
    """
    print("🚀 開始詞彙生成程序")
    print("=" * 60)
    
    successful_generations = 0
    failed_generations = 0
    
    # 遍歷所有主題進行詞彙生成
    for i, topic in enumerate(TOPICS, 1):
        print(f"\n📚 [{i}/{len(TOPICS)}] 正在處理主題：{topic}")
        print("-" * 40)
        
        # 生成詞彙內容
        content = generate_vocabulary(topic)
        
        if content:
            # 保存到文件
            if save_to_file(topic, content):
                successful_generations += 1
            else:
                failed_generations += 1
                
            # 在每次請求之間暫停，避免超過 API 速率限制
            if i < len(TOPICS):  # 最後一個主題不需要等待
                print(f"  ⏳ 等待 {REQUEST_DELAY} 秒後繼續...")
                time.sleep(REQUEST_DELAY)
        else:
            print(f"  ⏭️  跳過 {topic}，因為生成失敗")
            failed_generations += 1
        
        # 顯示目前進度
        print(f"  📈 目前已生成的唯一詞彙總數：{len(generated_words)}")
    
    # 生成最終統計報告
    print("\n" + "=" * 60)
    print("📊 詞彙生成完成統計")
    print("=" * 60)
    
    stats = generate_statistics()
    
    print(f"✅ 成功生成的主題：{successful_generations}")
    print(f"❌ 失敗的主題：{failed_generations}")
    print(f"📝 總主題數：{stats['total_topics']}")
    print(f"🔤 唯一詞彙總數：{stats['total_unique_words']}")
    print(f"📊 平均每主題詞彙數：{stats['average_words_per_topic']:.1f}")
    print(f"🎯 目標每主題詞彙數：{stats['target_words_per_topic']}")
    
    # 保存統計資訊
    save_statistics(stats)
    
    if successful_generations == len(TOPICS):
        print("\n🎉 所有主題的詞彙生成完成！")
    else:
        print(f"\n⚠️  有 {failed_generations} 個主題生成失敗，請檢查錯誤訊息")

# ============================================================================
# 輔助功能函數
# ============================================================================

def preview_topic_list():
    """預覽將要處理的主題列表"""
    print("📋 將要生成詞彙的主題列表：")
    print("-" * 30)
    for i, topic in enumerate(TOPICS, 1):
        print(f"{i:2d}. {topic}")
    print(f"\n總共 {len(TOPICS)} 個主題")

def estimate_time():
    """估算完成時間"""
    total_time = len(TOPICS) * REQUEST_DELAY
    minutes = total_time // 60
    seconds = total_time % 60
    print(f"⏱️  預估完成時間：約 {minutes} 分 {seconds} 秒")

# ============================================================================
# 程式入口點
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("VocabVoyage 詞彙生成器")
    print("=" * 60)
    
    # 檢查命令列參數
    if len(sys.argv) > 1:
        if sys.argv[1] == "--preview":
            preview_topic_list()
            estimate_time()
            sys.exit(0)
        elif sys.argv[1] == "--help":
            print("使用方法：")
            print("  python vocabulary_generator.py          # 開始生成詞彙")
            print("  python vocabulary_generator.py --preview # 預覽主題列表")
            print("  python vocabulary_generator.py --help    # 顯示幫助")
            sys.exit(0)
    
    # 顯示預覽資訊
    preview_topic_list()
    estimate_time()
    
    # 確認是否繼續
    try:
        response = input("\n是否開始生成詞彙？(y/N): ").strip().lower()
        if response not in ['y', 'yes', '是']:
            print("已取消詞彙生成")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n已取消詞彙生成")
        sys.exit(0)
    
    # 執行主程式
    main()