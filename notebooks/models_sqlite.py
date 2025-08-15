"""
SQLite 資料庫模型範例程式

這個程式展示了如何使用 SQLite 資料庫來管理 VocabVoyage 應用程式的資料。
主要功能包括：
1. 用戶管理 - 創建和管理用戶帳戶
2. 詞彙管理 - 用戶個人詞彙表的 CRUD 操作
3. 聊天會話管理 - 管理用戶的聊天記錄和會話
4. 雲端同步 - 支援 Google Cloud Storage 的資料同步

技術特點：
- 支援本地和雲端兩種部署模式
- 使用臨時文件處理雲端資料庫同步
- 完整的錯誤處理和事務管理
- 結構化的資料模型設計
- 支援 JSON 格式的複雜資料存儲

適用場景：
- 個人詞彙學習記錄
- 聊天機器人對話歷史
- 用戶學習進度追蹤
- 多平台資料同步

作者：VocabVoyage 團隊
日期：2024年
"""

from datetime import datetime
import sqlite3
import json
import os
import uuid
import tempfile
from typing import Optional, List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# 嘗試導入 Google Cloud Storage（可選依賴）
try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    print("⚠️  Google Cloud Storage 未安裝，將使用本地模式")

# 載入環境變數
load_dotenv()

# ============================================================================
# 配置和常數
# ============================================================================

# 預設資料庫路徑
DEFAULT_DB_PATH = "data/vocab_learning.db"

# 預設 GCS 儲存桶名稱
DEFAULT_BUCKET_NAME = "ian-line-bot-files"

# 資料庫表結構版本
DB_VERSION = "1.0"

# ============================================================================
# 主要資料庫類別
# ============================================================================

class VocabDatabase:
    """
    VocabVoyage 詞彙學習資料庫管理類別
    
    這個類別提供了完整的資料庫操作功能，支援本地和雲端兩種模式。
    在雲端模式下，資料庫會自動同步到 Google Cloud Storage。
    
    Attributes:
        is_cloud (bool): 是否為雲端模式
        db_path (str): 資料庫文件路徑
        bucket_name (str): GCS 儲存桶名稱
        storage_client: GCS 客戶端（雲端模式）
        bucket: GCS 儲存桶對象（雲端模式）
        blob: GCS Blob 對象（雲端模式）
    """
    
    def __init__(self, db_path: str = DEFAULT_DB_PATH, bucket_name: str = DEFAULT_BUCKET_NAME):
        """
        初始化資料庫連接
        
        Args:
            db_path (str): 資料庫文件路徑
            bucket_name (str): GCS 儲存桶名稱（雲端模式）
        """
        # 判斷是否為雲端環境
        self.is_cloud = os.getenv('ENV') == 'prod' and GCS_AVAILABLE
        self.db_path = db_path
        self.bucket_name = bucket_name
        
        # 初始化雲端存儲（如果需要）
        if self.is_cloud:
            try:
                self.storage_client = storage.Client()
                self.bucket = self.storage_client.bucket(bucket_name)
                self.blob = self.bucket.blob(db_path)
                print(f"☁️  雲端模式已啟用，儲存桶：{bucket_name}")
            except Exception as e:
                print(f"⚠️  雲端初始化失敗，切換到本地模式：{str(e)}")
                self.is_cloud = False
        else:
            print("💻 本地模式已啟用")
        
        # 初始化資料庫結構
        self.init_db()

    def _get_connection(self):
        """
        獲取資料庫連接
        
        在雲端模式下，會先下載資料庫到臨時文件；
        在本地模式下，直接連接到本地文件。
        
        Returns:
            tuple: (連接對象, 臨時文件路徑)
        """
        if self.is_cloud:
            # 雲端模式：創建臨時文件
            temp_db = tempfile.NamedTemporaryFile(delete=False)
            temp_path = temp_db.name
            temp_db.close()

            # 如果雲端資料庫存在，下載到臨時文件
            try:
                if self.blob.exists():
                    print("📥 正在從雲端下載資料庫...")
                    self.blob.download_to_filename(temp_path)
                    print("✅ 資料庫下載完成")
                else:
                    print("🆕 雲端資料庫不存在，將創建新的資料庫")
            except Exception as e:
                print(f"⚠️  下載資料庫失敗：{str(e)}")
            
            conn = sqlite3.connect(temp_path)
            return conn, temp_path
        else:
            # 本地模式：確保目錄存在
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            return sqlite3.connect(self.db_path), None

    def _close_connection(self, conn, temp_path: Optional[str] = None):
        """
        關閉資料庫連接並處理雲端同步
        
        Args:
            conn: 資料庫連接對象
            temp_path (Optional[str]): 臨時文件路徑（雲端模式）
        """
        conn.close()
        
        if self.is_cloud and temp_path:
            try:
                # 上傳更新後的資料庫到雲端
                print("📤 正在上傳資料庫到雲端...")
                self.blob.upload_from_filename(temp_path)
                print("✅ 資料庫上傳完成")
                
                # 刪除臨時文件
                os.unlink(temp_path)
            except Exception as e:
                print(f"⚠️  上傳資料庫失敗：{str(e)}")
                # 保留臨時文件以便手動處理
                print(f"臨時文件保留在：{temp_path}")

    def init_db(self):
        """
        初始化資料庫表結構
        
        創建所有必要的資料表，包括：
        - users: 用戶資訊表
        - user_vocabulary: 用戶詞彙表
        - chat_sessions: 聊天會話表
        - chat_messages: 聊天訊息表
        """
        print("🔧 正在初始化資料庫結構...")
        
        conn, temp_path = self._get_connection()
        c = conn.cursor()
        
        try:
            # 用戶表
            c.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP,
                last_active TIMESTAMP,
                preferences TEXT DEFAULT '{}'
            )''')
            
            # 用戶詞彙表
            c.execute('''CREATE TABLE IF NOT EXISTS user_vocabulary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                word TEXT NOT NULL,
                definition TEXT NOT NULL,
                examples TEXT DEFAULT '[]',
                notes TEXT DEFAULT '',
                difficulty_level INTEGER DEFAULT 1,
                review_count INTEGER DEFAULT 0,
                last_reviewed TIMESTAMP,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(user_id, word)
            )''')
            
            # 聊天會話表
            c.execute('''CREATE TABLE IF NOT EXISTS chat_sessions (
                chat_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP,
                last_message_at TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )''')
            
            # 聊天訊息表
            c.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chat_sessions(chat_id)
            )''')
            
            # 創建索引以提升查詢效能
            c.execute('''CREATE INDEX IF NOT EXISTS idx_user_vocabulary_user_id 
                        ON user_vocabulary(user_id)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_chat_messages_chat_id 
                        ON chat_messages(chat_id)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id 
                        ON chat_sessions(user_id)''')
            
            conn.commit()
            print("✅ 資料庫結構初始化完成")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ 資料庫初始化失敗：{str(e)}")
            raise e
        finally:
            self._close_connection(conn, temp_path)

    # ========================================================================
    # 用戶管理功能
    # ========================================================================

    def get_or_create_user(self, username: str) -> str:
        """
        獲取現有用戶或創建新用戶
        
        Args:
            username (str): 用戶名稱
            
        Returns:
            str: 用戶 ID
            
        Raises:
            Exception: 當資料庫操作失敗時
        """
        conn, temp_path = self._get_connection()
        c = conn.cursor()
        
        try:
            # 檢查用戶是否已存在
            c.execute('SELECT user_id FROM users WHERE username = ?', (username,))
            result = c.fetchone()
            
            if result:
                user_id = result[0]
                # 更新最後活動時間
                now = datetime.now()
                c.execute('UPDATE users SET last_active = ? WHERE user_id = ?', 
                         (now, user_id))
                print(f"👤 用戶已存在：{username} (ID: {user_id})")
            else:
                # 創建新用戶
                user_id = str(uuid.uuid4())
                now = datetime.now()
                c.execute('''INSERT INTO users (user_id, username, created_at, last_active)
                            VALUES (?, ?, ?, ?)''', (user_id, username, now, now))
                print(f"🆕 創建新用戶：{username} (ID: {user_id})")
            
            conn.commit()
            return user_id
            
        except Exception as e:
            conn.rollback()
            print(f"❌ 用戶操作失敗：{str(e)}")
            raise e
        finally:
            self._close_connection(conn, temp_path)

    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        獲取用戶詳細資訊
        
        Args:
            user_id (str): 用戶 ID
            
        Returns:
            Optional[Dict[str, Any]]: 用戶資訊字典，不存在時返回 None
        """
        conn, temp_path = self._get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''SELECT user_id, username, created_at, last_active, preferences
                        FROM users WHERE user_id = ?''', (user_id,))
            result = c.fetchone()
            
            if result:
                return {
                    'user_id': result[0],
                    'username': result[1],
                    'created_at': result[2],
                    'last_active': result[3],
                    'preferences': json.loads(result[4] or '{}')
                }
            return None
            
        finally:
            self._close_connection(conn, temp_path)

    # ========================================================================
    # 詞彙管理功能
    # ========================================================================

    def add_vocabulary(self, user_id: str, word: str, definition: str, 
                      examples: List[str], notes: str = "", difficulty_level: int = 1):
        """
        添加新單字到用戶的詞彙表
        
        Args:
            user_id (str): 用戶 ID
            word (str): 英文單字
            definition (str): 中文定義
            examples (List[str]): 例句列表
            notes (str): 用戶筆記
            difficulty_level (int): 難度等級 (1-5)
            
        Returns:
            bool: 添加成功返回 True
            
        Raises:
            ValueError: 當單字已存在時
            Exception: 當資料庫操作失敗時
        """
        conn, temp_path = self._get_connection()
        c = conn.cursor()
        
        try:
            # 檢查單字是否已存在
            c.execute('''SELECT COUNT(*) FROM user_vocabulary 
                        WHERE user_id = ? AND word = ?''', (user_id, word))
            
            if c.fetchone()[0] > 0:
                raise ValueError(f"單字 '{word}' 已經存在於您的詞彙表中")
            
            # 添加新單字
            now = datetime.now()
            c.execute('''INSERT INTO user_vocabulary 
                        (user_id, word, definition, examples, notes, difficulty_level, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                     (user_id, word, definition, json.dumps(examples, ensure_ascii=False), 
                      notes, difficulty_level, now))
            
            conn.commit()
            print(f"📝 成功添加單字：{word}")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"❌ 添加單字失敗：{str(e)}")
            raise e
        finally:
            self._close_connection(conn, temp_path)

    def get_user_vocabulary(self, user_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        獲取用戶的詞彙表
        
        Args:
            user_id (str): 用戶 ID
            limit (Optional[int]): 限制返回數量
            
        Returns:
            List[Dict[str, Any]]: 詞彙列表
        """
        conn, temp_path = self._get_connection()
        c = conn.cursor()
        
        try:
            query = '''SELECT word, definition, examples, notes, difficulty_level, 
                             review_count, last_reviewed, created_at
                      FROM user_vocabulary 
                      WHERE user_id = ?
                      ORDER BY created_at DESC'''
            
            if limit:
                query += f' LIMIT {limit}'
            
            c.execute(query, (user_id,))
            results = c.fetchall()
            
            vocabulary_list = []
            for record in results:
                vocabulary_list.append({
                    'word': record[0],
                    'definition': record[1],
                    'examples': json.loads(record[2]),
                    'notes': record[3],
                    'difficulty_level': record[4],
                    'review_count': record[5],
                    'last_reviewed': record[6],
                    'created_at': record[7]
                })
            
            return vocabulary_list
            
        finally:
            self._close_connection(conn, temp_path)

    def delete_vocabulary(self, user_id: str, word: str) -> bool:
        """
        刪除用戶的單字
        
        Args:
            user_id (str): 用戶 ID
            word (str): 要刪除的單字
            
        Returns:
            bool: 刪除成功返回 True
        """
        conn, temp_path = self._get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''DELETE FROM user_vocabulary 
                        WHERE user_id = ? AND word = ?''', (user_id, word))
            
            deleted_count = c.rowcount
            conn.commit()
            
            if deleted_count > 0:
                print(f"🗑️  成功刪除單字：{word}")
                return True
            else:
                print(f"⚠️  單字不存在：{word}")
                return False
                
        except Exception as e:
            conn.rollback()
            print(f"❌ 刪除單字失敗：{str(e)}")
            return False
        finally:
            self._close_connection(conn, temp_path)

    def update_vocabulary_review(self, user_id: str, word: str) -> bool:
        """
        更新單字的複習記錄
        
        Args:
            user_id (str): 用戶 ID
            word (str): 單字
            
        Returns:
            bool: 更新成功返回 True
        """
        conn, temp_path = self._get_connection()
        c = conn.cursor()
        
        try:
            now = datetime.now()
            c.execute('''UPDATE user_vocabulary 
                        SET review_count = review_count + 1, last_reviewed = ?
                        WHERE user_id = ? AND word = ?''', (now, user_id, word))
            
            updated_count = c.rowcount
            conn.commit()
            
            return updated_count > 0
            
        except Exception as e:
            conn.rollback()
            print(f"❌ 更新複習記錄失敗：{str(e)}")
            return False
        finally:
            self._close_connection(conn, temp_path)

    # ========================================================================
    # 聊天會話管理功能
    # ========================================================================

    def create_chat_session(self, user_id: str, name: str, chat_id: Optional[str] = None) -> str:
        """
        創建新的聊天會話
        
        Args:
            user_id (str): 用戶 ID
            name (str): 會話名稱
            chat_id (Optional[str]): 指定的會話 ID，不提供則自動生成
            
        Returns:
            str: 會話 ID
        """
        conn, temp_path = self._get_connection()
        c = conn.cursor()
        
        try:
            if chat_id is None:
                chat_id = str(uuid.uuid4())
            
            now = datetime.now()
            c.execute('''INSERT INTO chat_sessions (chat_id, user_id, name, created_at, last_message_at)
                        VALUES (?, ?, ?, ?, ?)''', (chat_id, user_id, name, now, now))
            
            conn.commit()
            print(f"💬 創建新聊天會話：{name} (ID: {chat_id})")
            return chat_id
            
        except Exception as e:
            conn.rollback()
            print(f"❌ 創建聊天會話失敗：{str(e)}")
            raise e
        finally:
            self._close_connection(conn, temp_path)

    def get_user_chats(self, user_id: str) -> List[Dict[str, Any]]:
        """
        獲取用戶的所有聊天會話
        
        Args:
            user_id (str): 用戶 ID
            
        Returns:
            List[Dict[str, Any]]: 聊天會話列表
        """
        conn, temp_path = self._get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''SELECT chat_id, name, created_at, last_message_at, message_count
                        FROM chat_sessions 
                        WHERE user_id = ?
                        ORDER BY last_message_at DESC''', (user_id,))
            
            chats = []
            for row in c.fetchall():
                chats.append({
                    "id": row[0],
                    "name": row[1],
                    "created_at": row[2],
                    "last_message_at": row[3],
                    "message_count": row[4]
                })
            
            return chats
            
        finally:
            self._close_connection(conn, temp_path)

    def add_chat_message(self, chat_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """
        添加聊天訊息
        
        Args:
            chat_id (str): 會話 ID
            role (str): 訊息角色 ('user', 'assistant', 'system')
            content (str): 訊息內容
            metadata (Optional[Dict]): 額外的元資料
        """
        conn, temp_path = self._get_connection()
        c = conn.cursor()
        
        try:
            now = datetime.now()
            metadata_json = json.dumps(metadata or {}, ensure_ascii=False)
            
            # 添加訊息
            c.execute('''INSERT INTO chat_messages (chat_id, role, content, metadata, created_at)
                        VALUES (?, ?, ?, ?, ?)''', (chat_id, role, content, metadata_json, now))
            
            # 更新會話的最後訊息時間和訊息計數
            c.execute('''UPDATE chat_sessions 
                        SET last_message_at = ?, message_count = message_count + 1
                        WHERE chat_id = ?''', (now, chat_id))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"❌ 添加聊天訊息失敗：{str(e)}")
            raise e
        finally:
            self._close_connection(conn, temp_path)

    def get_chat_messages(self, chat_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        獲取聊天會話的所有訊息
        
        Args:
            chat_id (str): 會話 ID
            limit (Optional[int]): 限制返回數量
            
        Returns:
            List[Dict[str, Any]]: 訊息列表
        """
        conn, temp_path = self._get_connection()
        c = conn.cursor()
        
        try:
            query = '''SELECT role, content, metadata, created_at 
                      FROM chat_messages 
                      WHERE chat_id = ?
                      ORDER BY created_at ASC'''
            
            if limit:
                query += f' LIMIT {limit}'
            
            c.execute(query, (chat_id,))
            
            messages = []
            for row in c.fetchall():
                messages.append({
                    "role": row[0],
                    "content": row[1],
                    "metadata": json.loads(row[2]),
                    "created_at": row[3]
                })
            
            return messages
            
        finally:
            self._close_connection(conn, temp_path)

    def delete_chat_session(self, chat_id: str) -> bool:
        """
        刪除聊天會話及其所有訊息
        
        Args:
            chat_id (str): 會話 ID
            
        Returns:
            bool: 刪除成功返回 True
        """
        conn, temp_path = self._get_connection()
        c = conn.cursor()
        
        try:
            # 首先刪除所有相關的訊息
            c.execute('DELETE FROM chat_messages WHERE chat_id = ?', (chat_id,))
            message_count = c.rowcount
            
            # 然後刪除會話
            c.execute('DELETE FROM chat_sessions WHERE chat_id = ?', (chat_id,))
            session_count = c.rowcount
            
            conn.commit()
            
            if session_count > 0:
                print(f"🗑️  成功刪除聊天會話和 {message_count} 條訊息")
                return True
            else:
                print("⚠️  聊天會話不存在")
                return False
                
        except Exception as e:
            conn.rollback()
            print(f"❌ 刪除聊天會話失敗：{str(e)}")
            return False
        finally:
            self._close_connection(conn, temp_path)

    def update_chat_name(self, chat_id: str, new_name: str) -> bool:
        """
        更新聊天會話名稱
        
        Args:
            chat_id (str): 會話 ID
            new_name (str): 新的會話名稱
            
        Returns:
            bool: 更新成功返回 True
        """
        conn, temp_path = self._get_connection()
        c = conn.cursor()
        
        try:
            c.execute('''UPDATE chat_sessions 
                        SET name = ?
                        WHERE chat_id = ?''', (new_name, chat_id))
            
            updated_count = c.rowcount
            conn.commit()
            
            if updated_count > 0:
                print(f"✏️  成功更新會話名稱：{new_name}")
                return True
            else:
                print("⚠️  聊天會話不存在")
                return False
                
        except Exception as e:
            conn.rollback()
            print(f"❌ 更新會話名稱失敗：{str(e)}")
            return False
        finally:
            self._close_connection(conn, temp_path)

    # ========================================================================
    # 統計和維護功能
    # ========================================================================

    def get_database_stats(self) -> Dict[str, Any]:
        """
        獲取資料庫統計資訊
        
        Returns:
            Dict[str, Any]: 統計資訊字典
        """
        conn, temp_path = self._get_connection()
        c = conn.cursor()
        
        try:
            stats = {}
            
            # 用戶統計
            c.execute('SELECT COUNT(*) FROM users')
            stats['total_users'] = c.fetchone()[0]
            
            # 詞彙統計
            c.execute('SELECT COUNT(*) FROM user_vocabulary')
            stats['total_vocabulary'] = c.fetchone()[0]
            
            # 聊天會話統計
            c.execute('SELECT COUNT(*) FROM chat_sessions')
            stats['total_chat_sessions'] = c.fetchone()[0]
            
            # 聊天訊息統計
            c.execute('SELECT COUNT(*) FROM chat_messages')
            stats['total_chat_messages'] = c.fetchone()[0]
            
            # 平均每用戶詞彙數
            if stats['total_users'] > 0:
                stats['avg_vocabulary_per_user'] = stats['total_vocabulary'] / stats['total_users']
            else:
                stats['avg_vocabulary_per_user'] = 0
            
            return stats
            
        finally:
            self._close_connection(conn, temp_path)

    def test_connection(self) -> bool:
        """
        測試資料庫連接
        
        Returns:
            bool: 連接成功返回 True
        """
        try:
            conn, temp_path = self._get_connection()
            c = conn.cursor()
            c.execute('SELECT 1')
            result = c.fetchone()
            self._close_connection(conn, temp_path)
            
            return result is not None
            
        except Exception as e:
            print(f"❌ 資料庫連接測試失敗：{str(e)}")
            return False

# ============================================================================
# 使用範例和測試功能
# ============================================================================

def demo_usage():
    """展示資料庫使用範例"""
    print("VocabVoyage SQLite 資料庫使用範例")
    print("=" * 60)
    
    # 初始化資料庫
    db = VocabDatabase()
    
    # 測試連接
    if not db.test_connection():
        print("❌ 資料庫連接失敗")
        return
    
    print("✅ 資料庫連接成功")
    
    # 創建測試用戶
    print("\n📝 創建測試用戶...")
    user_id = db.get_or_create_user("demo_user")
    
    # 添加測試詞彙
    print("\n📚 添加測試詞彙...")
    try:
        db.add_vocabulary(
            user_id=user_id,
            word="vocabulary",
            definition="詞彙，單字",
            examples=["I'm learning new vocabulary.", "This app helps expand your vocabulary."],
            notes="這是一個很重要的單字",
            difficulty_level=2
        )
        print("✅ 詞彙添加成功")
    except ValueError as e:
        print(f"⚠️  {e}")
    
    # 獲取用戶詞彙
    print("\n📖 獲取用戶詞彙...")
    vocab_list = db.get_user_vocabulary(user_id, limit=5)
    for vocab in vocab_list:
        print(f"  - {vocab['word']}: {vocab['definition']}")
    
    # 創建聊天會話
    print("\n💬 創建聊天會話...")
    chat_id = db.create_chat_session(user_id, "測試聊天")
    
    # 添加聊天訊息
    print("\n📝 添加聊天訊息...")
    db.add_chat_message(chat_id, "user", "Hello, how are you?")
    db.add_chat_message(chat_id, "assistant", "I'm doing well, thank you! How can I help you today?")
    
    # 獲取聊天記錄
    print("\n💬 獲取聊天記錄...")
    messages = db.get_chat_messages(chat_id)
    for msg in messages:
        print(f"  {msg['role']}: {msg['content']}")
    
    # 顯示統計資訊
    print("\n📊 資料庫統計...")
    stats = db.get_database_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_usage()
    else:
        print("VocabVoyage SQLite 資料庫模型")
        print("=" * 60)
        print("這是一個資料庫模型範例程式")
        print("\n使用方法：")
        print(f"  python {sys.argv[0]} --demo    # 執行使用範例")
        print(f"  python {sys.argv[0]} --help    # 顯示幫助")
        print("\n功能特點：")
        print("  - 用戶管理")
        print("  - 詞彙管理") 
        print("  - 聊天會話管理")
        print("  - 雲端同步支援")
        print("  - 完整的錯誤處理")