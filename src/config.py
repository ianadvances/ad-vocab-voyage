"""
VocabVoyage 配置管理模組

此模組負責管理應用程式的所有配置設定，包括：
- 環境變數管理和驗證
- API 金鑰和服務配置
- 資料庫連接設定
- 應用程式預設值
- 模型參數配置
"""

import os
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv
import logging

# 載入環境變數
load_dotenv()

# 配置日誌記錄
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FirebaseConfig:
    """
    Firebase 資料庫配置類別
    
    管理 Firebase Realtime Database 的連接設定，
    包括認證金鑰和資料庫 URL 的配置。
    """
    database_url: str
    credentials_path: Optional[str] = None
    credentials_json: Optional[str] = None
    
    def __post_init__(self):
        """
        配置驗證：確保至少提供一種認證方式
        
        Raises:
            ValueError: 當未提供任何認證方式或資料庫 URL 為空時
        """
        if not self.database_url:
            raise ValueError("Firebase 資料庫 URL 不能為空")
        
        if not self.credentials_path and not self.credentials_json:
            raise ValueError("必須提供 Firebase 認證金鑰檔案路徑或 JSON 字串")
    
    @property
    def has_credentials_file(self) -> bool:
        """檢查是否有認證金鑰檔案"""
        return self.credentials_path is not None and os.path.exists(self.credentials_path)
    
    @property
    def has_credentials_json(self) -> bool:
        """檢查是否有認證 JSON 字串"""
        return self.credentials_json is not None


@dataclass
class OpenAIConfig:
    """
    OpenAI API 配置類別
    
    管理 OpenAI 服務的相關設定，包括 API 金鑰、
    模型選擇、溫度參數等。
    """
    api_key: str
    chat_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    
    def __post_init__(self):
        """
        配置驗證：檢查 API 金鑰和參數有效性
        
        Raises:
            ValueError: 當 API 金鑰為空或參數無效時
        """
        if not self.api_key:
            raise ValueError("OpenAI API 金鑰不能為空")
        
        if not (0.0 <= self.temperature <= 2.0):
            raise ValueError("溫度參數必須在 0.0 到 2.0 之間")
        
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("最大 token 數必須大於 0")


@dataclass
class ChromaConfig:
    """
    Chroma 向量資料庫配置類別
    
    管理 Chroma 向量資料庫的連接和檢索設定，
    包括資料庫路徑、集合名稱和搜尋參數。
    """
    persist_directory: str = "./data/chroma_db"
    collection_name: str = "vocabulary_v1"
    search_type: str = "similarity"
    search_k: int = 1
    
    def __post_init__(self):
        """
        配置驗證：檢查資料庫路徑和參數有效性
        
        Raises:
            ValueError: 當參數無效時
        """
        if not self.persist_directory:
            raise ValueError("Chroma 資料庫路徑不能為空")
        
        if not self.collection_name:
            raise ValueError("Chroma 集合名稱不能為空")
        
        if self.search_k <= 0:
            raise ValueError("搜尋結果數量必須大於 0")
        
        if self.search_type not in ["similarity", "mmr"]:
            raise ValueError("搜尋類型必須是 'similarity' 或 'mmr'")


@dataclass
class StreamlitConfig:
    """
    Streamlit 應用程式配置類別
    
    管理 Streamlit 網頁應用程式的顯示設定，
    包括頁面標題、圖示和布局配置。
    """
    page_title: str = "VocabVoyage"
    page_icon: str = "🎓"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    
    def __post_init__(self):
        """
        配置驗證：檢查布局參數有效性
        
        Raises:
            ValueError: 當布局參數無效時
        """
        if self.layout not in ["centered", "wide"]:
            raise ValueError("布局必須是 'centered' 或 'wide'")
        
        if self.initial_sidebar_state not in ["auto", "expanded", "collapsed"]:
            raise ValueError("側邊欄狀態必須是 'auto'、'expanded' 或 'collapsed'")


@dataclass
class ChatConfig:
    """
    聊天功能配置類別
    
    管理聊天相關的設定，包括歷史記錄數量、
    訊息長度限制等。
    """
    max_history_messages: int = 4
    max_message_length: int = 2000
    default_chat_name: str = "聊天"
    welcome_message: str = """歡迎使用 VocabVoyage！

你可以：
1. 📖 查詢單字的詳細用法
   - "解釋 'sustainability' 的意思"
   - "說明 'blockchain' 怎麼用"
   - "'machine learning' 這個詞組是什麼意思？"
2. 📚 學習特定主題的單字
   - "我想學習飲食美食相關的單字"
   - "教我一些環保議題常用的詞彙"
   - "介紹金融科技領域的重要單字"
3. 📝 進行主題測驗
   - "測驗我的科技英文程度"
   - "出一份關於永續發展的詞彙測驗"
   - "測試我對商業用語的掌握"
4. 💭 提出英文相關協助
   - "幫我寫一篇關於冒險的英文故事"
   - "幫我潤飾這段英文文章"
"""
    
    def __post_init__(self):
        """
        配置驗證：檢查聊天參數有效性
        
        Raises:
            ValueError: 當參數無效時
        """
        if self.max_history_messages <= 0:
            raise ValueError("歷史訊息數量必須大於 0")
        
        if self.max_message_length <= 0:
            raise ValueError("訊息長度限制必須大於 0")


class ConfigManager:
    """
    配置管理器主類別
    
    負責載入、驗證和管理所有應用程式配置，
    提供統一的配置存取介面。
    """
    
    def __init__(self):
        """
        初始化配置管理器
        
        載入所有配置類別並進行驗證，
        確保應用程式具備完整的運行配置。
        """
        self._load_configurations()
        self._validate_configurations()
        logger.info("配置管理器初始化完成")
    
    def _load_configurations(self):
        """
        載入所有配置設定
        
        從環境變數和預設值載入各個模組的配置，
        建立完整的配置物件。
        """
        # Firebase 配置
        self.firebase = FirebaseConfig(
            database_url=self._get_env_var("FIREBASE_DATABASE_URL", required=True),
            credentials_path=self._get_env_var("FIREBASE_CREDENTIALS_PATH", "FirebaseKey.json"),
            credentials_json=self._get_env_var("FIREBASE_CREDENTIALS")
        )
        
        # OpenAI 配置
        self.openai = OpenAIConfig(
            api_key=self._get_env_var("OPENAI_API_KEY", required=True),
            chat_model=self._get_env_var("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            embedding_model=self._get_env_var("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            temperature=float(self._get_env_var("OPENAI_TEMPERATURE", "0.7")),
            max_tokens=self._get_optional_int("OPENAI_MAX_TOKENS")
        )
        
        # Chroma 配置
        self.chroma = ChromaConfig(
            persist_directory=self._get_env_var("CHROMA_PERSIST_DIR", "./data/chroma_db"),
            collection_name=self._get_env_var("CHROMA_COLLECTION_NAME", "vocabulary_v1"),
            search_type=self._get_env_var("CHROMA_SEARCH_TYPE", "similarity"),
            search_k=int(self._get_env_var("CHROMA_SEARCH_K", "1"))
        )
        
        # Streamlit 配置
        self.streamlit = StreamlitConfig(
            page_title=self._get_env_var("STREAMLIT_PAGE_TITLE", "VocabVoyage"),
            page_icon=self._get_env_var("STREAMLIT_PAGE_ICON", "🎓"),
            layout=self._get_env_var("STREAMLIT_LAYOUT", "wide"),
            initial_sidebar_state=self._get_env_var("STREAMLIT_SIDEBAR_STATE", "expanded")
        )
        
        # 聊天配置
        self.chat = ChatConfig(
            max_history_messages=int(self._get_env_var("CHAT_MAX_HISTORY", "4")),
            max_message_length=int(self._get_env_var("CHAT_MAX_LENGTH", "2000")),
            default_chat_name=self._get_env_var("CHAT_DEFAULT_NAME", "聊天")
        )
        
        # 應用程式環境配置
        self.environment = self._get_env_var("ENV", "production")
        self.debug_mode = self._get_env_var("DEBUG", "false").lower() == "true"
        self.log_level = self._get_env_var("LOG_LEVEL", "INFO")
    
    def _get_env_var(self, key: str, default: Optional[str] = None, required: bool = False) -> str:
        """
        獲取環境變數值
        
        Args:
            key (str): 環境變數名稱
            default (Optional[str]): 預設值
            required (bool): 是否為必需變數
            
        Returns:
            str: 環境變數值
            
        Raises:
            ValueError: 當必需的環境變數未設定時
        """
        value = os.getenv(key, default)
        
        if required and not value:
            raise ValueError(f"必需的環境變數 '{key}' 未設定")
        
        return value or ""
    
    def _get_optional_int(self, key: str) -> Optional[int]:
        """
        獲取可選的整數環境變數
        
        Args:
            key (str): 環境變數名稱
            
        Returns:
            Optional[int]: 整數值或 None
        """
        value = os.getenv(key)
        if value:
            try:
                return int(value)
            except ValueError:
                logger.warning(f"環境變數 '{key}' 的值 '{value}' 不是有效的整數")
        return None
    
    def _validate_configurations(self):
        """
        驗證所有配置的完整性和有效性
        
        檢查各個配置物件是否正確初始化，
        並記錄配置狀態。
        """
        configs_to_validate = [
            ("Firebase", self.firebase),
            ("OpenAI", self.openai),
            ("Chroma", self.chroma),
            ("Streamlit", self.streamlit),
            ("Chat", self.chat)
        ]
        
        for config_name, config_obj in configs_to_validate:
            try:
                # 配置物件的 __post_init__ 方法會進行驗證
                logger.info(f"{config_name} 配置驗證通過")
            except Exception as e:
                logger.error(f"{config_name} 配置驗證失敗: {e}")
                raise
    
    def get_firebase_credentials(self) -> Dict[str, Any]:
        """
        獲取 Firebase 認證資訊
        
        Returns:
            Dict[str, Any]: Firebase 認證字典
            
        Raises:
            ValueError: 當無法獲取有效認證資訊時
        """
        if self.firebase.has_credentials_json:
            try:
                return json.loads(self.firebase.credentials_json)
            except json.JSONDecodeError as e:
                raise ValueError(f"Firebase 認證 JSON 格式錯誤: {e}")
        
        elif self.firebase.has_credentials_file:
            try:
                with open(self.firebase.credentials_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                raise ValueError(f"無法讀取 Firebase 認證檔案: {e}")
        
        else:
            raise ValueError("無法獲取 Firebase 認證資訊")
    
    def is_development(self) -> bool:
        """檢查是否為開發環境"""
        return self.environment.lower() in ["dev", "development", "local", "loc"]
    
    def is_production(self) -> bool:
        """檢查是否為生產環境"""
        return self.environment.lower() in ["prod", "production"]
    
    def get_chroma_config_dict(self) -> Dict[str, Any]:
        """
        獲取 Chroma 配置字典
        
        Returns:
            Dict[str, Any]: Chroma 配置參數字典
        """
        return {
            "persist_directory": self.chroma.persist_directory,
            "collection_name": self.chroma.collection_name
        }
    
    def get_retriever_config(self) -> Dict[str, Any]:
        """
        獲取檢索器配置字典
        
        Returns:
            Dict[str, Any]: 檢索器配置參數字典
        """
        return {
            "search_type": self.chroma.search_type,
            "search_kwargs": {"k": self.chroma.search_k}
        }
    
    def get_streamlit_config_dict(self) -> Dict[str, str]:
        """
        獲取 Streamlit 配置字典
        
        Returns:
            Dict[str, str]: Streamlit 頁面配置字典
        """
        return {
            "page_title": self.streamlit.page_title,
            "page_icon": self.streamlit.page_icon,
            "layout": self.streamlit.layout,
            "initial_sidebar_state": self.streamlit.initial_sidebar_state
        }
    
    def print_config_summary(self):
        """
        列印配置摘要資訊
        
        用於調試和系統狀態檢查，
        不會顯示敏感資訊如 API 金鑰。
        """
        print("=== VocabVoyage 配置摘要 ===")
        print(f"環境: {self.environment}")
        print(f"除錯模式: {self.debug_mode}")
        print(f"日誌等級: {self.log_level}")
        print()
        
        print("Firebase 配置:")
        print(f"  資料庫 URL: {self.firebase.database_url}")
        print(f"  認證方式: {'JSON 字串' if self.firebase.has_credentials_json else '檔案路徑'}")
        print()
        
        print("OpenAI 配置:")
        print(f"  聊天模型: {self.openai.chat_model}")
        print(f"  嵌入模型: {self.openai.embedding_model}")
        print(f"  溫度參數: {self.openai.temperature}")
        print(f"  最大 Token: {self.openai.max_tokens or '未設定'}")
        print()
        
        print("Chroma 配置:")
        print(f"  資料庫路徑: {self.chroma.persist_directory}")
        print(f"  集合名稱: {self.chroma.collection_name}")
        print(f"  搜尋類型: {self.chroma.search_type}")
        print(f"  搜尋結果數: {self.chroma.search_k}")
        print()
        
        print("Streamlit 配置:")
        print(f"  頁面標題: {self.streamlit.page_title}")
        print(f"  頁面圖示: {self.streamlit.page_icon}")
        print(f"  布局: {self.streamlit.layout}")
        print()
        
        print("聊天配置:")
        print(f"  歷史訊息數: {self.chat.max_history_messages}")
        print(f"  訊息長度限制: {self.chat.max_message_length}")
        print(f"  預設聊天名稱: {self.chat.default_chat_name}")
        print("=" * 30)


# 全域配置實例
# 在模組載入時自動初始化配置管理器
try:
    config = ConfigManager()
    logger.info("全域配置管理器載入成功")
except Exception as e:
    logger.error(f"配置管理器初始化失敗: {e}")
    raise


# 便利函數：提供快速存取常用配置的函數
def get_openai_config() -> OpenAIConfig:
    """獲取 OpenAI 配置"""
    return config.openai


def get_firebase_config() -> FirebaseConfig:
    """獲取 Firebase 配置"""
    return config.firebase


def get_chroma_config() -> ChromaConfig:
    """獲取 Chroma 配置"""
    return config.chroma


def get_streamlit_config() -> StreamlitConfig:
    """獲取 Streamlit 配置"""
    return config.streamlit


def get_chat_config() -> ChatConfig:
    """獲取聊天配置"""
    return config.chat


def is_debug_mode() -> bool:
    """檢查是否為除錯模式"""
    return config.debug_mode


def is_development_env() -> bool:
    """檢查是否為開發環境"""
    return config.is_development()


# 模組測試區域
if __name__ == "__main__":
    """
    配置模組測試
    
    用於驗證配置載入和驗證功能，
    可以在開發時執行此腳本檢查配置狀態。
    """
    try:
        # 列印配置摘要
        config.print_config_summary()
        
        # 測試各種配置存取方法
        print("\n=== 配置存取測試 ===")
        print(f"OpenAI 聊天模型: {get_openai_config().chat_model}")
        print(f"Firebase 資料庫 URL: {get_firebase_config().database_url}")
        print(f"Chroma 集合名稱: {get_chroma_config().collection_name}")
        print(f"是否為開發環境: {is_development_env()}")
        print(f"是否為除錯模式: {is_debug_mode()}")
        
        print("\n配置模組測試完成！")
        
    except Exception as e:
        print(f"配置測試失敗: {e}")
        raise