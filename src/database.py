"""
VocabVoyage 資料庫管理模組

此模組負責處理所有與 Firebase 資料庫相關的操作，包括：
- 用戶管理
- 詞彙管理
- 聊天會話管理
- 聊天訊息管理
"""

import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import json
from typing import List, Optional
import os
from .config import get_firebase_config, config


class VocabDatabase:
    """
    詞彙學習平台資料庫管理類別
    
    負責管理 Firebase Realtime Database 的所有操作，
    包括用戶資料、詞彙資料、聊天會話和訊息的 CRUD 操作。
    """
    
    def __init__(self):
        """
        初始化 Firebase 連接
        
        使用配置管理器設定 Firebase 認證並建立資料庫連接。
        支援環境變數或服務帳戶金鑰檔案兩種認證方式。
        """
        # 檢查是否已經初始化 Firebase 應用程式
        if not firebase_admin._apps:
            # 獲取 Firebase 配置
            firebase_config = get_firebase_config()
            
            # 獲取認證資訊
            try:
                credentials_data = config.get_firebase_credentials()
                cred = credentials.Certificate(credentials_data)
            except ValueError as e:
                raise ValueError(f"Firebase 認證配置錯誤: {e}")
                
            # 初始化 Firebase 應用程式
            firebase_admin.initialize_app(cred, {
                'databaseURL': firebase_config.database_url
            })
        
        # 建立資料庫參考
        self.db = db.reference()

    def get_or_create_user(self, username: str) -> str:
        """
        獲取或創建用戶
        
        Args:
            username (str): 用戶名稱
            
        Returns:
            str: 用戶的唯一識別碼 (user_id)
            
        功能說明：
        - 首先查詢是否已存在該用戶名的用戶
        - 如果存在，返回現有用戶的 ID
        - 如果不存在，創建新用戶並返回新用戶的 ID
        """
        users_ref = self.db.child('users')
        
        # 查找是否已存在該用戶名的用戶
        existing_users = users_ref.order_by_child('username').equal_to(username).get()
        
        if existing_users:
            # 返回現有用戶的 ID（取第一個匹配的用戶）
            return list(existing_users.keys())[0]
        else:
            # 創建新用戶
            new_user_ref = users_ref.push()
            new_user_ref.set({
                'username': username,
                'created_at': str(datetime.now())
            })
            return new_user_ref.key

    def add_vocabulary(self, user_id: str, word: str, definition: str, 
                      examples: List[str], notes: str = "") -> bool:
        """
        添加新單字到用戶的詞彙表
        
        Args:
            user_id (str): 用戶的唯一識別碼
            word (str): 英文單字
            definition (str): 單字定義
            examples (List[str]): 例句列表
            notes (str, optional): 額外筆記. Defaults to "".
            
        Returns:
            bool: 操作成功返回 True
            
        Raises:
            ValueError: 當單字已存在於用戶詞彙表中時拋出異常
            
        功能說明：
        - 檢查單字是否已存在於用戶的詞彙表中
        - 如果不存在，將新單字資料儲存到資料庫
        - 記錄創建時間戳
        """
        vocab_ref = self.db.child('vocabulary').child(user_id)
        
        # 檢查單字是否已存在於用戶的詞彙表中
        existing_vocab = vocab_ref.order_by_child('word').equal_to(word).get()
        if existing_vocab:
            raise ValueError(f"單字 '{word}' 已經存在於您的單字本中")
        
        # 建立新單字資料結構
        new_vocab = {
            'word': word,
            'definition': definition,
            'examples': examples,
            'notes': notes,
            'created_at': str(datetime.now())
        }
        
        # 將新單字儲存到資料庫
        vocab_ref.push().set(new_vocab)
        return True

    def get_user_vocabulary(self, user_id: str) -> List[dict]:
        """
        獲取用戶的詞彙表
        
        Args:
            user_id (str): 用戶的唯一識別碼
            
        Returns:
            List[dict]: 用戶的詞彙列表，按單字字母順序排序
            
        功能說明：
        - 從資料庫獲取指定用戶的所有詞彙
        - 將資料整理成標準格式
        - 按單字字母順序排序後返回
        """
        vocab_ref = self.db.child('vocabulary').child(user_id).get()
        if not vocab_ref:
            return []
        
        vocab_list = []
        # 遍歷用戶的所有詞彙記錄
        for key, value in vocab_ref.items():
            vocab_list.append({
                'word': value['word'],
                'definition': value['definition'],
                'examples': value['examples'],
                'notes': value['notes']
            })
        
        # 按單字字母順序排序
        return sorted(vocab_list, key=lambda x: x['word'])

    def delete_vocabulary(self, user_id: str, word: str) -> bool:
        """
        刪除用戶的單字
        
        Args:
            user_id (str): 用戶的唯一識別碼
            word (str): 要刪除的英文單字
            
        Returns:
            bool: 刪除成功返回 True，失敗返回 False
            
        功能說明：
        - 查找指定用戶的指定單字
        - 如果找到，從資料庫中刪除該單字記錄
        - 支援刪除多個同名單字（雖然正常情況下不應該存在）
        """
        vocab_ref = self.db.child('vocabulary').child(user_id)
        
        # 查找要刪除的單字
        vocab_items = vocab_ref.order_by_child('word').equal_to(word).get()
        
        if vocab_items:
            # 刪除所有匹配的單字記錄
            for key in vocab_items.keys():
                vocab_ref.child(key).delete()
            return True
        return False

    def create_chat_session(self, user_id: str, name: str, chat_id: str = None) -> str:
        """
        創建新的聊天會話
        
        Args:
            user_id (str): 用戶的唯一識別碼
            name (str): 聊天會話名稱
            chat_id (str, optional): 指定的聊天會話 ID. Defaults to None.
            
        Returns:
            str: 聊天會話的唯一識別碼
            
        功能說明：
        - 為指定用戶創建新的聊天會話
        - 可以指定聊天會話 ID，或由系統自動生成
        - 記錄創建時間戳
        """
        chats_ref = self.db.child('chats').child(user_id)
        
        # 建立新聊天會話資料結構
        new_chat = {
            'name': name,
            'created_at': str(datetime.now())
        }
        
        if chat_id:
            # 使用指定的聊天會話 ID
            chats_ref.child(chat_id).set(new_chat)
            return chat_id
        else:
            # 讓 Firebase 自動生成聊天會話 ID
            new_chat_ref = chats_ref.push()
            new_chat_ref.set(new_chat)
            return new_chat_ref.key

    def get_user_chats(self, user_id: str) -> List[dict]:
        """
        獲取用戶的所有聊天會話
        
        Args:
            user_id (str): 用戶的唯一識別碼
            
        Returns:
            List[dict]: 用戶的聊天會話列表，按創建時間倒序排列
            
        功能說明：
        - 獲取指定用戶的所有聊天會話
        - 整理成標準格式，包含 ID、名稱和創建時間
        - 按創建時間倒序排列（最新的在前面）
        """
        chats_ref = self.db.child('chats').child(user_id).get()
        if not chats_ref:
            return []
        
        chats = []
        # 遍歷用戶的所有聊天會話
        for chat_id, chat_data in chats_ref.items():
            chats.append({
                'id': chat_id,
                'name': chat_data['name'],
                'created_at': chat_data['created_at']
            })
        
        # 按創建時間倒序排列（最新的在前面）
        return sorted(chats, key=lambda x: x['created_at'], reverse=True)

    def add_chat_message(self, chat_id: str, role: str, content: str) -> None:
        """
        添加聊天訊息
        
        Args:
            chat_id (str): 聊天會話的唯一識別碼
            role (str): 訊息角色 ('user' 或 'assistant')
            content (str): 訊息內容
            
        功能說明：
        - 將新訊息添加到指定的聊天會話中
        - 記錄訊息角色（用戶或助手）
        - 記錄創建時間戳
        """
        messages_ref = self.db.child('messages').child(chat_id)
        
        # 建立新訊息資料結構
        new_message = {
            'role': role,
            'content': content,
            'created_at': str(datetime.now())
        }
        
        # 將新訊息儲存到資料庫
        messages_ref.push().set(new_message)

    def get_chat_messages(self, chat_id: str) -> List[dict]:
        """
        獲取聊天會話的所有訊息
        
        Args:
            chat_id (str): 聊天會話的唯一識別碼
            
        Returns:
            List[dict]: 聊天訊息列表，按創建時間順序排列
            
        功能說明：
        - 獲取指定聊天會話的所有訊息
        - 按創建時間順序排列（最早的在前面）
        - 返回包含角色、內容和創建時間的訊息列表
        """
        messages_ref = self.db.child('messages').child(chat_id).get()
        if not messages_ref:
            return []
        
        messages = []
        # 遍歷聊天會話的所有訊息
        for msg_data in messages_ref.values():
            messages.append({
                'role': msg_data['role'],
                'content': msg_data['content'],
                'created_at': msg_data['created_at']
            })
        
        # 按創建時間順序排列（最早的在前面）
        return sorted(messages, key=lambda x: x['created_at'])

    def delete_chat_session(self, chat_id: str) -> bool:
        """
        刪除聊天會話及其所有訊息
        
        Args:
            chat_id (str): 聊天會話的唯一識別碼
            
        Returns:
            bool: 刪除成功返回 True，失敗返回 False
            
        功能說明：
        - 刪除指定聊天會話的所有相關訊息
        - 從用戶的聊天會話列表中移除該會話
        - 使用異常處理確保操作的穩定性
        """
        try:
            # 刪除聊天會話的所有相關訊息
            self.db.child('messages').child(chat_id).delete()
            
            # 查找並刪除聊天會話記錄
            chats = self.db.child('chats').get()
            for user_id, user_chats in chats.items():
                if chat_id in user_chats:
                    # 從用戶的聊天會話列表中刪除該會話
                    self.db.child('chats').child(user_id).child(chat_id).delete()
                    return True
            return False
        except Exception:
            # 發生任何異常時返回 False
            return False

    def update_chat_name(self, chat_id: str, new_name: str) -> bool:
        """
        更新聊天會話名稱
        
        Args:
            chat_id (str): 聊天會話的唯一識別碼
            new_name (str): 新的聊天會話名稱
            
        Returns:
            bool: 更新成功返回 True，失敗返回 False
            
        功能說明：
        - 查找指定的聊天會話
        - 更新聊天會話的名稱
        - 保持其他資料不變
        - 使用異常處理確保操作的穩定性
        """
        try:
            # 查找並更新聊天會話名稱
            chats = self.db.child('chats').get()
            for user_id, user_chats in chats.items():
                if chat_id in user_chats:
                    # 獲取現有聊天會話資料
                    chat_ref = self.db.child('chats').child(user_id).child(chat_id)
                    chat_data = chat_ref.get()
                    
                    # 更新聊天會話名稱
                    chat_data['name'] = new_name
                    chat_ref.update(chat_data)
                    return True
            return False
        except Exception:
            # 發生任何異常時返回 False
            return False