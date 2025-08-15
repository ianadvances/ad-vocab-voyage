# VocabVoyage 安裝指南

本指南將協助您完成 VocabVoyage 英語詞彙學習平台的安裝和設定。我們提供兩種安裝方式：Docker 容器化部署和本地開發環境安裝。

## 系統需求

### 基本需求
- **作業系統**：Windows 10+、macOS 10.14+、或 Linux (Ubuntu 18.04+)
- **記憶體**：至少 4GB RAM (建議 8GB 以上)
- **儲存空間**：至少 2GB 可用空間
- **網路連線**：穩定的網際網路連線 (用於 API 呼叫)

### 軟體需求
- **Python**：3.11 或更高版本
- **Poetry**：Python 套件管理工具
- **Docker**：(可選) 用於容器化部署
- **Git**：版本控制工具

## 方法一：Docker 容器化部署 (推薦)

Docker 部署是最簡單且最可靠的安裝方式，適合生產環境和快速體驗。

### 1. 安裝 Docker

#### Windows
1. 下載並安裝 [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/install/)
2. 啟動 Docker Desktop
3. 確認安裝成功：
   ```cmd
   docker --version
   ```

#### macOS
1. 下載並安裝 [Docker Desktop for Mac](https://docs.docker.com/desktop/mac/install/)
2. 啟動 Docker Desktop
3. 確認安裝成功：
   ```bash
   docker --version
   ```

#### Linux (Ubuntu)
```bash
# 更新套件列表
sudo apt update

# 安裝必要套件
sudo apt install apt-transport-https ca-certificates curl software-properties-common

# 添加 Docker 官方 GPG 金鑰
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# 添加 Docker 儲存庫
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# 安裝 Docker
sudo apt update
sudo apt install docker-ce

# 啟動 Docker 服務
sudo systemctl start docker
sudo systemctl enable docker

# 確認安裝成功
docker --version
```

### 2. 下載專案

```bash
# 複製專案儲存庫
git clone https://github.com/your-username/VocabVoyage.git
cd VocabVoyage
```

### 3. 環境設定

```bash
# 複製環境變數範例檔案
cp .env.example .env

# 複製 Firebase 金鑰範例檔案
cp firebase-key.example.json FirebaseKey.json
```

### 4. 編輯配置檔案

#### 編輯 .env 檔案
使用您偏好的文字編輯器開啟 `.env` 檔案：

```bash
# OpenAI API 設定
OPENAI_API_KEY=your_openai_api_key_here

# Firebase 設定
GOOGLE_APPLICATION_CREDENTIALS=./FirebaseKey.json
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com/

# Streamlit 設定
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

#### 編輯 FirebaseKey.json 檔案
將您的 Firebase 服務帳戶金鑰內容貼入 `FirebaseKey.json` 檔案中。

### 5. 建置和執行

#### 方法 A：使用 Docker Compose (推薦)
```bash
# 建置並啟動服務
docker-compose up --build

# 背景執行
docker-compose up -d --build
```

#### 方法 B：直接使用 Docker
```bash
# 建置 Docker 映像
docker build -t vocabvoyage .

# 執行容器
docker run -p 8080:8080 --env-file .env -v $(pwd)/data:/app/data vocabvoyage
```

### 6. 存取應用程式

開啟瀏覽器並前往 `http://localhost:8080` 即可使用 VocabVoyage。

#### 開發模式 (可選)
如需開發模式，可使用：
```bash
# 啟動開發環境
docker-compose --profile dev up

# 存取開發環境
# http://localhost:8501
```

## 方法二：本地開發環境安裝

本地安裝適合開發者進行程式碼修改和功能開發。

### 1. 安裝 Python

#### Windows
1. 前往 [Python 官網](https://www.python.org/downloads/windows/)
2. 下載 Python 3.11 或更高版本
3. 安裝時勾選 "Add Python to PATH"
4. 確認安裝成功：
   ```cmd
   python --version
   ```

#### macOS
```bash
# 使用 Homebrew 安裝 (推薦)
brew install python@3.11

# 或下載官方安裝程式
# https://www.python.org/downloads/macos/

# 確認安裝成功
python3 --version
```

#### Linux (Ubuntu)
```bash
# 更新套件列表
sudo apt update

# 安裝 Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv

# 確認安裝成功
python3.11 --version
```

### 2. 安裝 Poetry

Poetry 是現代化的 Python 套件管理工具，用於管理專案依賴。

#### 官方安裝方式 (推薦)
```bash
# Linux/macOS/Windows (PowerShell)
curl -sSL https://install.python-poetry.org | python3 -

# 或使用 pip 安裝
pip install poetry
```

#### 確認安裝成功
```bash
poetry --version
```

### 3. 下載和設定專案

```bash
# 複製專案
git clone https://github.com/your-username/VocabVoyage.git
cd VocabVoyage

# 安裝專案依賴
poetry install

# 複製配置檔案
cp .env.example .env
cp firebase-key.example.json FirebaseKey.json
```

### 4. 環境配置

#### 資料庫配置選項

VocabVoyage 支援兩種資料庫模式，根據 `ENV` 環境變數自動切換：

**本地開發模式（推薦用於開發和個人使用）**：
```env
ENV=local  # 或 dev, development, loc
OPENAI_API_KEY=your_openai_api_key_here
```

**生產模式（用於正式部署）**：
```env
ENV=prod
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_APPLICATION_CREDENTIALS=./FirebaseKey.json
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com/
```

**重要說明**：
- 當 `ENV` 設定為 `local`, `dev`, `development`, 或 `loc` 時，系統會自動使用本地 SQLite 資料庫
- SQLite 資料庫檔案會自動創建於 `data/vocab_learning.db`
- 本地模式不需要 Firebase 配置，可以跳過 Firebase 相關設定步驟
- 首次啟動時，系統會自動初始化 SQLite 資料庫結構

#### 編輯 .env 檔案
```bash
# 使用您偏好的編輯器開啟 .env
nano .env  # 或 vim .env 或 code .env
```

填入以下資訊：
```env
# OpenAI API 設定
OPENAI_API_KEY=sk-your-openai-api-key-here

# Firebase 設定  
GOOGLE_APPLICATION_CREDENTIALS=./FirebaseKey.json
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com/

# Streamlit 設定
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

#### 設定 Firebase 金鑰
將您從 Firebase Console 下載的服務帳戶金鑰內容複製到 `FirebaseKey.json` 檔案中。

### 5. 啟動應用程式

```bash
# 啟動 Poetry 虛擬環境
poetry shell

# 執行應用程式
streamlit run src/app.py

# 或者直接使用 Poetry 執行
poetry run streamlit run src/app.py
```

### 6. 存取應用程式

應用程式啟動後，Streamlit 會自動開啟瀏覽器並導向 `http://localhost:8501`。

## 服務設定指南

### OpenAI API 設定

1. **註冊 OpenAI 帳戶**
   - 前往 [OpenAI 官網](https://platform.openai.com/)
   - 註冊帳戶並完成驗證

2. **獲取 API 金鑰**
   - 登入 OpenAI 平台
   - 前往 "API Keys" 頁面
   - 點擊 "Create new secret key"
   - 複製生成的金鑰並保存在安全的地方

3. **設定使用額度**
   - 在 "Billing" 頁面設定付費方式
   - 建議設定使用限額以控制成本

### Firebase 設定

1. **建立 Firebase 專案**
   - 前往 [Firebase Console](https://console.firebase.google.com/)
   - 點擊 "建立專案"
   - 輸入專案名稱並完成設定

2. **啟用 Realtime Database**
   - 在專案控制台中選擇 "Realtime Database"
   - 點擊 "建立資料庫"
   - 選擇適當的安全規則 (開發階段可選擇測試模式)

3. **下載服務帳戶金鑰**
   - 前往 "專案設定" > "服務帳戶"
   - 點擊 "產生新的私密金鑰"
   - 下載 JSON 檔案並重新命名為 `FirebaseKey.json`

4. **設定資料庫規則**
   ```json
   {
     "rules": {
       ".read": "auth != null",
       ".write": "auth != null"
     }
   }
   ```

### Google Cloud 設定 (Gemini 模型)

1. **建立 Google Cloud 專案**
   - 前往 [Google Cloud Console](https://console.cloud.google.com/)
   - 建立新專案或選擇現有專案

2. **啟用 Vertex AI API**
   - 在 API 庫中搜尋 "Vertex AI API"
   - 點擊啟用

3. **設定服務帳戶**
   - 前往 "IAM 與管理" > "服務帳戶"
   - 建立服務帳戶並下載金鑰檔案
   - 將金鑰檔案路徑設定到環境變數中

## 驗證安裝

### 功能測試清單

安裝完成後，請依序測試以下功能：

1. **基本啟動測試**
   - [ ] 應用程式能正常啟動
   - [ ] 網頁介面正常載入
   - [ ] 無明顯錯誤訊息

2. **詞彙查詢測試**
   - [ ] 輸入 "查詢單字 hello" 能正常回應
   - [ ] 回應包含定義、例句、相關詞彙
   - [ ] 格式正確且使用繁體中文

3. **主題學習測試**
   - [ ] 輸入 "列出商業相關單字" 能正常回應
   - [ ] 回應包含 10 個相關單字
   - [ ] 每個單字都有完整的說明

4. **測驗生成測試**
   - [ ] 輸入 "生成科技詞彙測驗" 能正常回應
   - [ ] 測驗格式正確
   - [ ] 包含選擇題和答案選項

5. **個人詞彙本測試**
   - [ ] 能新增單字到個人詞彙本
   - [ ] 能查看已保存的單字列表
   - [ ] 能刪除不需要的單字

### 效能測試

```bash
# 測試 API 回應時間
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8501"

# 監控記憶體使用量
docker stats vocabvoyage  # Docker 部署
# 或
ps aux | grep streamlit   # 本地部署
```

## 常見問題解決

### 安裝問題

**Q: Poetry 安裝失敗**
```bash
# 解決方案 1: 使用 pip 安裝
pip install --user poetry

# 解決方案 2: 使用系統套件管理器
# Ubuntu/Debian
sudo apt install python3-poetry

# macOS
brew install poetry
```

**Q: Python 版本不相容**
```bash
# 檢查 Python 版本
python --version

# 使用 pyenv 管理多個 Python 版本
curl https://pyenv.run | bash
pyenv install 3.11.0
pyenv global 3.11.0
```

**Q: 依賴安裝失敗**
```bash
# 清除快取並重新安裝
poetry cache clear pypi --all
poetry install --no-cache
```

### 執行問題

**Q: Streamlit 無法啟動**
```bash
# 檢查埠號是否被佔用
netstat -tulpn | grep 8501

# 使用不同埠號
streamlit run src/app.py --server.port 8502
```

**Q: API 金鑰錯誤**
```bash
# 檢查環境變數是否正確載入
echo $OPENAI_API_KEY

# 重新載入環境變數
source .env
```

**Q: Firebase 連線失敗**
```bash
# 檢查金鑰檔案是否存在
ls -la FirebaseKey.json

# 檢查檔案權限
chmod 600 FirebaseKey.json

# 測試 Firebase 連線
python -c "import firebase_admin; print('Firebase 可正常匯入')"
```

### Docker 問題

**Q: Docker 建置失敗**
```bash
# 清除 Docker 快取
docker system prune -a

# 重新建置映像
docker build --no-cache -t vocabvoyage .
```

**Q: 容器無法存取檔案**
```bash
# 檢查檔案掛載
docker run -v $(pwd):/app -p 8080:8080 vocabvoyage

# 檢查檔案權限
ls -la .env FirebaseKey.json
```

### 效能問題

**Q: 回應速度慢**
- 檢查網路連線品質
- 確認 API 配額是否充足
- 考慮使用較快的 OpenAI 模型 (如 gpt-3.5-turbo)

**Q: 記憶體使用量過高**
- 重啟應用程式清除快取
- 調整 Streamlit 設定減少記憶體使用
- 考慮使用 Docker 限制記憶體使用量

## 進階設定

### 自訂配置

#### Streamlit 設定
建立 `.streamlit/config.toml` 檔案：
```toml
[server]
port = 8501
address = "0.0.0.0"
maxUploadSize = 200

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

#### 日誌設定
```python
# 在 src/config.py 中設定日誌
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vocabvoyage.log'),
        logging.StreamHandler()
    ]
)
```

### 生產環境部署

#### 使用 Docker Compose
專案已包含 `docker-compose.yml` 檔案，支援生產和開發環境：

```bash
# 生產環境部署
docker-compose up -d --build

# 開發環境部署（包含即時程式碼更新）
docker-compose --profile dev up --build
```

Docker Compose 配置特色：
- **生產環境**：端口 8080，資料持久化
- **開發環境**：端口 8501，即時程式碼更新
- **健康檢查**：自動監控應用程式狀態
- **資料卷掛載**：確保資料不會遺失

#### Google Cloud Run 部署
```bash
# 建置並推送映像到 Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/vocabvoyage

# 部署到 Cloud Run
gcloud run deploy vocabvoyage \
  --image gcr.io/PROJECT_ID/vocabvoyage \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated
```

## 更新和維護

### 更新應用程式
```bash
# 拉取最新程式碼
git pull origin main

# 更新依賴
poetry update

# 重新啟動應用程式
poetry run streamlit run src/app.py
```

### 備份資料
```bash
# 備份 Firebase 資料
# (需要使用 Firebase CLI 或管理控制台)

# 備份本地向量資料庫
cp -r data/chroma_db data/chroma_db_backup_$(date +%Y%m%d)

# 備份配置檔案
cp .env .env.backup
cp FirebaseKey.json FirebaseKey.json.backup
```

### 監控和日誌
```bash
# 查看應用程式日誌
tail -f vocabvoyage.log

# 監控系統資源使用
htop

# 檢查 Docker 容器狀態
docker ps
docker logs vocabvoyage
```

---

如果您在安裝過程中遇到任何問題，請參考 README.md 中的故障排除指南或在專案的 Issues 頁面中回報問題。