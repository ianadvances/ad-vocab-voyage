# VocabVoyage 使用指南

歡迎使用 VocabVoyage！本指南將詳細介紹如何使用平台的各項功能，幫助您充分利用 AI 驅動的英語詞彙學習體驗。

## 快速開始

### 首次使用

1. **開啟應用程式**
   - 在瀏覽器中前往 `http://localhost:8501`
   - 等待應用程式完全載入

2. **建立用戶帳戶**
   - 在側邊欄輸入您的用戶名稱
   - 系統會自動為您建立個人學習檔案

3. **開始第一次對話**
   - 在聊天輸入框中輸入 "你好" 或 "Hello"
   - 體驗 AI 助手的回應

## 核心功能使用

### 1. 詞彙查詢功能 🔍

詞彙查詢是 VocabVoyage 的核心功能，提供即時、準確的英文單字資訊。

#### 基本查詢方式

**標準查詢格式：**
```
查詢單字 [單字]
解釋單字 [單字]
[單字] 是什麼意思？
[單字] 怎麼用？
```

**實際使用範例：**
```
用戶輸入：查詢單字 innovation
系統回應：
---
單字：innovation
詞性：名詞 (noun)
定義：創新；革新；新方法或新想法的引入
例句：
-> The company's innovation in renewable energy has revolutionized the industry.
   (該公司在再生能源方面的創新徹底改變了整個行業。)
-> Her innovation in teaching methods improved student engagement significantly.
   (她在教學方法上的創新顯著提高了學生的參與度。)
相關詞彙：innovative (形容詞，創新的)、innovate (動詞，創新)、innovator (名詞，創新者)
使用建議：常用於商業、科技和學術語境中，強調新穎性和改進性
---
```

#### 進階查詢技巧

**片語查詢：**
```
查詢單字 break the ice
解釋片語 piece of cake
```

**同義詞查詢：**
```
happy 的同義詞有哪些？
給我一些表達 "困難" 的英文詞彙
```

**詞性變化查詢：**
```
beautiful 的其他詞性有哪些？
create 的名詞形式是什麼？
```

### 2. 主題式詞彙學習 📚

主題學習功能基於 RAG 技術，提供結構化的詞彙學習體驗。

#### 支援的學習主題

| 主題類別 | 英文名稱 | 涵蓋內容 |
|---------|---------|---------|
| 🏠 日常生活 | Daily Life | 家庭、購物、日常活動、生活用品 |
| 💼 工作職業 | Work & Career | 職場、商務、專業技能、職業發展 |
| ✈️ 旅行交通 | Travel & Transportation | 旅遊、交通工具、地理、住宿 |
| 🍽️ 飲食餐廳 | Food & Dining | 美食、烹飪、餐廳用語、營養 |
| 📖 教育學習 | Education & Learning | 學術、研究、教學、考試 |
| 💻 科技數位 | Technology & Digital | 科技、網路、數位工具、程式設計 |
| 🏥 健康醫療 | Health & Medical | 健康、醫療、運動、心理健康 |
| 🎬 娛樂休閒 | Entertainment & Leisure | 娛樂、運動、興趣、藝術 |
| 🌱 環境自然 | Environment & Nature | 環保、自然、氣候、生態 |
| 👥 社交關係 | Social Relationships | 人際關係、情感表達、社交技巧 |

#### 使用方式

**基本主題學習：**
```
列出商業相關單字
我想學習醫療領域的詞彙
給我一些科技方面的專業用語
旅行相關的英文單字有哪些？
```

**具體領域學習：**
```
我要學習餐廳點餐的英文
職場會議常用的英文詞彙
環保議題相關的英文單字
```

#### 學習成果範例

```
用戶輸入：列出商業相關單字
系統回應：
【商業】相關單字或片語：

1. entrepreneur
- 定義：企業家；創業者
- 詞性：名詞
- 使用：用於描述創立和經營企業的人，強調創新和風險承擔
- 例句：The young entrepreneur started her tech company in her garage.
       (翻譯：這位年輕的企業家在她的車庫裡創立了科技公司。)

2. revenue
- 定義：收入；營收
- 詞性：名詞
- 使用：指公司或組織的總收入，常用於財務報告
- 例句：The company's revenue increased by 25% this quarter.
       (翻譯：該公司本季的營收增長了25%。)

[... 繼續列出其他8個單字]
```

### 3. 智能測驗生成 📝

測驗功能幫助您檢驗學習成效，提供多樣化的題型和即時回饋。

#### 測驗生成方式

**基本測驗生成：**
```
生成商業英文測驗
我要做科技詞彙的測驗
幫我出一份環保主題的單字測驗
測試我的醫療英文程度
```

**指定難度測驗：**
```
生成初級商業英文測驗
我要做進階科技詞彙測驗
```

#### 測驗類型

**1. 選擇題測驗**
```
用戶輸入：生成商業英文測驗
系統回應：
【商業英文詞彙測驗】

1. "Innovation" 的中文意思是？
   A) 投資
   B) 創新
   C) 保險
   D) 利息
   
2. 下列哪個詞彙表示 "企業家"？
   A) Employee
   B) Entrepreneur
   C) Engineer
   D) Economist

[... 繼續其他題目]

答案：
1. B) 創新
2. B) Entrepreneur
```

**2. 填空題測驗**
```
請填入適當的單字：

1. The company's _______ (營收) has doubled this year.
2. She is a successful _______ (企業家) in the tech industry.
3. We need to _______ (創新) our products to stay competitive.
```

**3. 配對題測驗**
```
請將左側的英文詞彙與右側的中文定義配對：

英文詞彙          中文定義
1. Revenue        A) 企業家
2. Entrepreneur   B) 創新
3. Innovation     C) 營收
4. Investment     D) 投資
```

### 4. 個人詞彙本管理 💾

個人詞彙本功能讓您建立和管理專屬的學習詞彙庫。

#### 新增單字到詞彙本

**方法一：查詢後直接新增**
1. 使用詞彙查詢功能查詢單字
2. 在查詢結果下方點擊 "加入詞彙本" 按鈕
3. 系統自動儲存單字資訊

**方法二：手動新增**
1. 在側邊欄選擇 "個人詞彙本"
2. 點擊 "新增單字" 按鈕
3. 填入單字、定義、例句等資訊
4. 點擊 "儲存" 完成新增

#### 管理詞彙本

**查看詞彙列表：**
- 在側邊欄點擊 "個人詞彙本"
- 瀏覽所有已儲存的單字
- 使用搜尋功能快速找到特定單字

**編輯單字資訊：**
- 點擊單字旁的 "編輯" 按鈕
- 修改定義、例句或個人筆記
- 儲存變更

**刪除單字：**
- 點擊單字旁的 "刪除" 按鈕
- 確認刪除操作

#### 詞彙本統計

系統會自動追蹤您的學習進度：
- 總詞彙數量
- 本週新增單字數
- 最常查詢的主題
- 學習天數統計

### 5. 智能對話學習 🤖

對話功能提供自然的學習互動體驗，支援多種學習場景。

#### 基本對話功能

**學習諮詢：**
```
用戶：我想提升商業英文，有什麼建議？
系統：建議您從以下幾個方面開始：
1. 學習基礎商業詞彙...
2. 練習商務會議用語...
3. 閱讀商業新聞和報告...
```

**文法問題：**
```
用戶：什麼時候用 "a" 什麼時候用 "an"？
系統：這是關於不定冠詞的使用規則...
```

**寫作協助：**
```
用戶：幫我修改這個句子：I am very happy to meet you.
系統：這個句子在文法上是正確的，但可以有以下改進建議...
```

#### 進階對話功能

**情境對話練習：**
```
用戶：我想練習餐廳點餐的英文對話
系統：好的！我來扮演服務生，您扮演顧客。讓我們開始：
"Good evening! Welcome to our restaurant. Do you have a reservation?"
```

**商務英文練習：**
```
用戶：幫我練習商務會議的開場白
系統：以下是一些常用的會議開場白...
```

### 6. 聊天記錄管理 📱

聊天記錄功能幫助您組織不同的學習主題和對話。

#### 建立新聊天室

1. 在側邊欄點擊 "新增聊天室"
2. 輸入聊天室名稱 (例如：商業英文學習、旅遊英文練習)
3. 點擊 "建立" 完成

#### 管理聊天室

**切換聊天室：**
- 在側邊欄的聊天室列表中點擊要切換的聊天室
- 系統會載入該聊天室的歷史對話

**重新命名聊天室：**
- 點擊聊天室名稱旁的編輯圖示
- 輸入新名稱並儲存

**刪除聊天室：**
- 點擊聊天室旁的刪除按鈕
- 確認刪除操作 (注意：刪除後無法復原)

#### 搜尋歷史對話

- 使用搜尋框輸入關鍵字
- 系統會在所有聊天記錄中搜尋相關內容
- 點擊搜尋結果可直接跳轉到相關對話

## 進階使用技巧

### 1. 組合功能使用

**學習流程建議：**
1. **主題探索** → 使用主題學習功能了解某個領域的詞彙
2. **深度學習** → 對感興趣的單字使用詞彙查詢功能
3. **記憶強化** → 將重要單字加入個人詞彙本
4. **知識檢驗** → 使用測驗功能檢驗學習成效
5. **實際應用** → 透過對話功能練習使用新學的詞彙

### 2. 個人化學習策略

**建立學習計畫：**
```
用戶：幫我制定一個月的商業英文學習計畫
系統：為您推薦以下學習計畫：
第一週：基礎商業詞彙 (50個核心單字)
第二週：會議和簡報用語
第三週：財務和數據分析詞彙
第四週：綜合練習和測驗
```

**設定學習目標：**
- 每日學習 10 個新單字
- 每週完成 2 次主題測驗
- 每月複習個人詞彙本中的所有單字

### 3. 多場景應用

**職場應用：**
```
我明天要參加英文會議，需要準備哪些詞彙？
幫我練習產品介紹的英文表達
如何用英文寫專業的電子郵件？
```

**考試準備：**
```
TOEIC 考試常考的商業詞彙有哪些？
幫我生成 IELTS 寫作常用詞彙測驗
```

**日常生活：**
```
出國旅遊需要知道哪些英文詞彙？
在國外餐廳點餐的英文怎麼說？
```

## API 使用範例

對於開發者，VocabVoyage 提供了程式化的 API 介面。

### 基本 API 呼叫

```python
from src.agents import search_vocabulary, get_category_vocabulary, generate_quiz

# 詞彙查詢
result = search_vocabulary("innovation")
print(result)

# 主題學習
business_vocab = get_category_vocabulary("商業")
print(business_vocab)

# 測驗生成
quiz = generate_quiz("科技")
print(quiz)
```

### 批次處理範例

```python
# 批次查詢多個單字
words = ["innovation", "entrepreneur", "revenue", "investment"]
results = []

for word in words:
    result = search_vocabulary(word)
    results.append(result)
    
# 儲存結果到檔案
with open("vocabulary_results.txt", "w", encoding="utf-8") as f:
    for result in results:
        f.write(result + "\n\n")
```

### 自訂學習內容

```python
# 建立自訂主題詞彙列表
custom_topics = ["人工智慧", "區塊鏈", "永續發展"]

for topic in custom_topics:
    vocab_list = get_category_vocabulary(topic)
    quiz = generate_quiz(topic)
    
    print(f"=== {topic} 詞彙 ===")
    print(vocab_list)
    print(f"\n=== {topic} 測驗 ===")
    print(quiz)
    print("\n" + "="*50 + "\n")
```

## 最佳實踐建議

### 1. 有效學習策略

**間隔重複學習：**
- 新學的單字在 1 天、3 天、7 天、14 天後各複習一次
- 使用個人詞彙本的複習提醒功能

**主動學習：**
- 不只是被動記憶，要主動使用新詞彙造句
- 透過對話功能練習實際應用

**多感官學習：**
- 結合視覺 (閱讀定義)、聽覺 (發音練習) 和動覺 (書寫筆記)

### 2. 學習進度追蹤

**設定明確目標：**
- 每日目標：學習 5-10 個新單字
- 每週目標：完成 1-2 個主題的深度學習
- 每月目標：掌握 100-200 個新詞彙

**定期評估：**
- 每週使用測驗功能檢驗學習成效
- 每月回顧個人詞彙本，清理不熟悉的單字
- 每季評估整體英語能力提升情況

### 3. 個人化調整

**根據程度調整：**
- 初學者：專注於日常生活和基礎商業詞彙
- 中級學習者：擴展到專業領域和學術詞彙
- 高級學習者：關注細微語義差別和高級表達

**根據需求調整：**
- 職場需求：重點學習商業、科技、管理詞彙
- 學術需求：專注於學術寫作和研究相關詞彙
- 生活需求：強化日常對話和文化理解詞彙

## 故障排除

### 常見使用問題

**Q: 系統回應速度慢**
A: 可能原因和解決方案：
- 網路連線問題：檢查網路狀況
- API 配額限制：檢查 OpenAI API 使用量
- 伺服器負載：稍後再試或重新啟動應用程式

**Q: 詞彙查詢結果不準確**
A: 改進建議：
- 使用更具體的查詢詞彙
- 提供更多上下文資訊
- 嘗試不同的查詢方式

**Q: 個人詞彙本無法儲存**
A: 檢查項目：
- Firebase 連線是否正常
- 用戶權限是否正確設定
- 瀏覽器是否允許本地儲存

### 效能優化建議

**提升回應速度：**
- 使用較快的 OpenAI 模型 (如 gpt-3.5-turbo)
- 減少同時進行的查詢數量
- 清除瀏覽器快取

**改善學習體驗：**
- 定期整理個人詞彙本
- 使用具體的學習目標
- 結合多種學習功能

## 進階功能

### 1. 自訂提示詞

對於進階用戶，可以自訂 AI 的回應風格：

```python
# 在 src/config.py 中自訂提示詞
CUSTOM_PROMPTS = {
    "formal_style": "請使用正式的商務英語風格回應",
    "casual_style": "請使用輕鬆友善的對話風格回應",
    "academic_style": "請使用學術研究的專業風格回應"
}
```

### 2. 學習數據分析

```python
# 分析個人學習數據
def analyze_learning_progress(user_id):
    vocab_data = get_user_vocabulary(user_id)
    
    # 統計分析
    total_words = len(vocab_data)
    categories = {}
    
    for word_data in vocab_data:
        category = word_data.get('category', 'general')
        categories[category] = categories.get(category, 0) + 1
    
    return {
        'total_words': total_words,
        'categories': categories,
        'learning_trend': calculate_learning_trend(vocab_data)
    }
```

### 3. 匯出學習資料

```python
# 匯出個人詞彙本為 CSV 檔案
import csv

def export_vocabulary_to_csv(user_id, filename):
    vocab_data = get_user_vocabulary(user_id)
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['word', 'definition', 'examples', 'notes', 'created_at']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for word_data in vocab_data:
            writer.writerow(word_data)
```

## 社群和支援

### 獲得幫助

**官方資源：**
- [GitHub 儲存庫](https://github.com/your-username/VocabVoyage)
- [問題回報](https://github.com/your-username/VocabVoyage/issues)
- [功能建議](https://github.com/your-username/VocabVoyage/discussions)

**社群支援：**
- 加入我們的 Discord 社群
- 關注官方 Twitter 帳號
- 訂閱學習技巧電子報

### 貢獻和回饋

**提供回饋：**
- 回報使用問題和建議
- 分享學習心得和技巧
- 參與功能測試和改進

**參與開發：**
- 提交程式碼改進
- 翻譯和本地化
- 文件撰寫和維護

---

希望這份使用指南能幫助您充分利用 VocabVoyage 的所有功能。如果您有任何問題或建議，歡迎隨時與我們聯繫！

**祝您學習愉快！** 🚀📚