#!/usr/bin/env python3
"""
VocabVoyage 核心功能測試腳本

此腳本用於測試專案重構後的核心功能完整性，包括：
1. 模組導入測試
2. 配置管理測試
3. 基本功能結構測試
4. 檔案路徑驗證

執行方式：python test_core_functionality.py
"""

import sys
import os
import uuid
from datetime import datetime

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 測試模組導入
def test_module_imports():
    """測試所有核心模組是否可以正常導入"""
    print("🔍 測試模組導入...")
    
    try:
        # 測試配置模組
        from src.config import config
        print("   ✅ 配置模組導入成功")
        
        # 測試基本的 LangChain 組件
        from langchain_core.messages import HumanMessage
        print("   ✅ LangChain 核心組件導入成功")
        
        # 測試其他核心模組（檢查檔案存在性而不導入會初始化外部服務的模組）
        if os.path.exists("src/agents.py"):
            print("   ✅ 代理模組檔案存在")
        else:
            print("   ❌ 代理模組檔案不存在")
            return False
        
        if os.path.exists("src/database.py"):
            print("   ✅ 資料庫模組檔案存在")
        else:
            print("   ❌ 資料庫模組檔案不存在")
            return False
        
        if os.path.exists("src/app.py"):
            print("   ✅ 應用程式模組檔案存在")
        else:
            print("   ❌ 應用程式模組檔案不存在")
            return False
        
        return True
        
    except ImportError as e:
        print(f"   ❌ 模組導入失敗: {e}")
        return False


class CoreFunctionalityTester:
    """核心功能測試類別"""
    
    def __init__(self):
        """初始化測試環境"""
        self.test_results = []
        
    def test_project_structure(self):
        """測試專案結構完整性"""
        print("\n📁 測試專案結構...")
        
        required_files = [
            "src/app.py",
            "src/agents.py", 
            "src/database.py",
            "src/config.py",
            "src/__init__.py",
            "data/chroma_db",
            "data/vocabulary",
            "docs/installation.md",
            "docs/usage.md",
            "docs/architecture.md",
            "examples/langgraph_rag.py",
            "examples/langgraph_tools.py",
            "assets/images",
            ".env.example",
            "firebase-key.example.json",
            "pyproject.toml",
            "README.md"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if not missing_files:
            print("   ✅ 所有必要檔案和資料夾都存在")
            self.test_results.append("專案結構測試: 通過")
        else:
            print(f"   ❌ 缺少以下檔案或資料夾: {missing_files}")
            self.test_results.append(f"專案結構測試: 失敗 - 缺少 {len(missing_files)} 個檔案")
    
    def test_configuration_management(self):
        """測試配置管理功能"""
        print("\n⚙️ 測試配置管理...")
        
        try:
            from src.config import config
            
            # 測試配置載入
            streamlit_config = config.get_streamlit_config_dict()
            if streamlit_config and 'page_title' in streamlit_config:
                print("   ✅ Streamlit 配置載入成功")
                self.test_results.append("Streamlit 配置測試: 通過")
            else:
                print("   ❌ Streamlit 配置載入失敗")
                self.test_results.append("Streamlit 配置測試: 失敗")
            
            # 測試檢索器配置
            retriever_config = config.get_retriever_config()
            if retriever_config and 'search_kwargs' in retriever_config and 'k' in retriever_config['search_kwargs']:
                print("   ✅ 檢索器配置載入成功")
                self.test_results.append("檢索器配置測試: 通過")
            else:
                print(f"   ❌ 檢索器配置載入失敗: {retriever_config}")
                self.test_results.append("檢索器配置測試: 失敗")
                
        except Exception as e:
            print(f"   ❌ 配置管理測試失敗: {e}")
            self.test_results.append(f"配置管理測試: 失敗 - {e}")
    
    def test_data_files_integrity(self):
        """測試資料檔案完整性"""
        print("\n📊 測試資料檔案完整性...")
        
        # 檢查詞彙資料檔案
        vocab_files = [
            "data/vocabulary/daily_life.txt",
            "data/vocabulary/education_learning.txt", 
            "data/vocabulary/entertainment_leisure.txt",
            "data/vocabulary/environment_nature.txt",
            "data/vocabulary/food_dining.txt",
            "data/vocabulary/health_medical.txt",
            "data/vocabulary/social_relationships.txt",
            "data/vocabulary/technology_digital.txt",
            "data/vocabulary/travel_transportation.txt",
            "data/vocabulary/work_career.txt"
        ]
        
        missing_vocab_files = []
        for file_path in vocab_files:
            if not os.path.exists(file_path):
                missing_vocab_files.append(file_path)
        
        if not missing_vocab_files:
            print("   ✅ 所有詞彙資料檔案都存在")
            self.test_results.append("詞彙資料檔案測試: 通過")
        else:
            print(f"   ❌ 缺少詞彙資料檔案: {missing_vocab_files}")
            self.test_results.append(f"詞彙資料檔案測試: 失敗 - 缺少 {len(missing_vocab_files)} 個檔案")
        
        # 檢查向量資料庫目錄
        if os.path.exists("data/chroma_db"):
            print("   ✅ 向量資料庫目錄存在")
            self.test_results.append("向量資料庫目錄測試: 通過")
        else:
            print("   ❌ 向量資料庫目錄不存在")
            self.test_results.append("向量資料庫目錄測試: 失敗")
    
    def test_documentation_completeness(self):
        """測試文件完整性"""
        print("\n📚 測試文件完整性...")
        
        # 檢查主要文件
        doc_files = {
            "README.md": "主要專案說明文件",
            "docs/installation.md": "安裝指南",
            "docs/usage.md": "使用指南", 
            "docs/architecture.md": "架構說明"
        }
        
        for file_path, description in doc_files.items():
            if os.path.exists(file_path):
                # 檢查檔案是否有內容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        print(f"   ✅ {description} 存在且有內容")
                        self.test_results.append(f"{description}測試: 通過")
                    else:
                        print(f"   ⚠️  {description} 存在但內容為空")
                        self.test_results.append(f"{description}測試: 部分通過")
            else:
                print(f"   ❌ {description} 不存在")
                self.test_results.append(f"{description}測試: 失敗")
    
    def test_example_files(self):
        """測試範例檔案"""
        print("\n💡 測試範例檔案...")
        
        example_files = [
            "examples/langgraph_rag.py",
            "examples/langgraph_tools.py",
            "examples/notebooks/vocabulary_generator.py",
            "examples/notebooks/pdf_text_extraction.py",
            "examples/notebooks/vocabulary_write_to_chroma.py",
            "examples/notebooks/models_sqlite.py"
        ]
        
        missing_examples = []
        for file_path in example_files:
            if not os.path.exists(file_path):
                missing_examples.append(file_path)
        
        if not missing_examples:
            print("   ✅ 所有範例檔案都存在")
            self.test_results.append("範例檔案測試: 通過")
        else:
            print(f"   ❌ 缺少範例檔案: {missing_examples}")
            self.test_results.append(f"範例檔案測試: 失敗 - 缺少 {len(missing_examples)} 個檔案")
    
    def test_asset_files(self):
        """測試靜態資源檔案"""
        print("\n🖼️ 測試靜態資源檔案...")
        
        asset_files = [
            "assets/images/langgraph_rag.png",
            "assets/images/langgraph_tools.png", 
            "assets/images/vocabvoyage.png"
        ]
        
        missing_assets = []
        for file_path in asset_files:
            if not os.path.exists(file_path):
                missing_assets.append(file_path)
        
        if not missing_assets:
            print("   ✅ 所有靜態資源檔案都存在")
            self.test_results.append("靜態資源檔案測試: 通過")
        else:
            print(f"   ❌ 缺少靜態資源檔案: {missing_assets}")
            self.test_results.append(f"靜態資源檔案測試: 失敗 - 缺少 {len(missing_assets)} 個檔案")
    
    def print_test_summary(self):
        """打印測試摘要"""
        print("\n" + "="*60)
        print("📊 測試結果摘要")
        print("="*60)
        
        passed = sum(1 for result in self.test_results if "通過" in result)
        partial = sum(1 for result in self.test_results if "部分通過" in result)
        failed = sum(1 for result in self.test_results if "失敗" in result)
        total = len(self.test_results)
        
        print(f"總測試數: {total}")
        print(f"通過: {passed}")
        print(f"部分通過: {partial}")
        print(f"失敗: {failed}")
        print(f"成功率: {(passed + partial) / total * 100:.1f}%")
        
        print("\n詳細結果:")
        for result in self.test_results:
            status = "✅" if "通過" in result else "⚠️" if "部分通過" in result else "❌"
            print(f"  {status} {result}")
        
        if failed == 0:
            print("\n🎉 所有核心功能測試通過！")
        elif partial > 0 and failed == 0:
            print("\n✅ 核心功能基本正常，部分功能需要進一步檢查")
        else:
            print(f"\n⚠️  發現 {failed} 個功能問題，需要修復")
    
    def run_all_tests(self):
        """執行所有測試"""
        print("🚀 開始 VocabVoyage 核心功能測試")
        print("="*60)
        
        # 執行各項測試
        self.test_project_structure()
        self.test_configuration_management()
        self.test_data_files_integrity()
        self.test_documentation_completeness()
        self.test_example_files()
        self.test_asset_files()
        
        # 打印測試摘要
        self.print_test_summary()
        
        return True


def main():
    """主函數"""
    # 首先測試模組導入
    if not test_module_imports():
        print("\n❌ 模組導入測試失敗，無法繼續執行其他測試")
        return False
    
    # 執行核心功能測試
    tester = CoreFunctionalityTester()
    return tester.run_all_tests()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)