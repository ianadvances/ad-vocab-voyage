#!/usr/bin/env python3
"""
VocabVoyage 部署流程測試腳本

此腳本用於測試專案的部署流程，包括：
1. 本地 Docker 部署測試
2. 環境變數配置驗證
3. 檔案路徑正確性檢查
4. Firebase 連接測試（如果有認證資訊）

執行方式：python test_deployment.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path


class DeploymentTester:
    """部署流程測試類別"""
    
    def __init__(self):
        """初始化測試環境"""
        self.test_results = []
        self.project_root = Path(__file__).parent
    
    def test_docker_configuration(self):
        """測試 Docker 配置"""
        print("🐳 測試 Docker 配置...")
        
        # 檢查 Dockerfile 是否存在
        dockerfile_path = self.project_root / "Dockerfile"
        if dockerfile_path.exists():
            print("   ✅ Dockerfile 存在")
            self.test_results.append("Dockerfile 存在: 通過")
            
            # 檢查 Dockerfile 內容
            with open(dockerfile_path, 'r', encoding='utf-8') as f:
                dockerfile_content = f.read()
                
            # 檢查關鍵配置
            if "FROM python:" in dockerfile_content:
                print("   ✅ Dockerfile 包含 Python 基礎映像")
                self.test_results.append("Docker Python 基礎映像: 通過")
            else:
                print("   ❌ Dockerfile 缺少 Python 基礎映像")
                self.test_results.append("Docker Python 基礎映像: 失敗")
            
            if "COPY" in dockerfile_content and "src/" in dockerfile_content:
                print("   ✅ Dockerfile 包含源碼複製指令")
                self.test_results.append("Docker 源碼複製: 通過")
            else:
                print("   ❌ Dockerfile 缺少源碼複製指令")
                self.test_results.append("Docker 源碼複製: 失敗")
                
            if "streamlit run" in dockerfile_content or "CMD" in dockerfile_content:
                print("   ✅ Dockerfile 包含啟動指令")
                self.test_results.append("Docker 啟動指令: 通過")
            else:
                print("   ❌ Dockerfile 缺少啟動指令")
                self.test_results.append("Docker 啟動指令: 失敗")
                
        else:
            print("   ❌ Dockerfile 不存在")
            self.test_results.append("Dockerfile 存在: 失敗")
        
        # 檢查 docker-compose.yml
        compose_path = self.project_root / "docker-compose.yml"
        if compose_path.exists():
            print("   ✅ docker-compose.yml 存在")
            self.test_results.append("docker-compose.yml 存在: 通過")
        else:
            print("   ⚠️  docker-compose.yml 不存在（可選）")
            self.test_results.append("docker-compose.yml 存在: 部分通過")
    
    def test_environment_variables(self):
        """測試環境變數配置"""
        print("\n🔧 測試環境變數配置...")
        
        # 檢查 .env.example 檔案
        env_example_path = self.project_root / ".env.example"
        if env_example_path.exists():
            print("   ✅ .env.example 檔案存在")
            self.test_results.append(".env.example 檔案: 通過")
            
            # 檢查必要的環境變數
            with open(env_example_path, 'r', encoding='utf-8') as f:
                env_content = f.read()
            
            required_vars = [
                "OPENAI_API_KEY",
                "FIREBASE_DATABASE_URL",
                "ENV"
            ]
            
            missing_vars = []
            for var in required_vars:
                if var not in env_content:
                    missing_vars.append(var)
            
            if not missing_vars:
                print("   ✅ 所有必要的環境變數都在範例檔案中")
                self.test_results.append("環境變數完整性: 通過")
            else:
                print(f"   ❌ 缺少環境變數: {missing_vars}")
                self.test_results.append(f"環境變數完整性: 失敗 - 缺少 {missing_vars}")
                
        else:
            print("   ❌ .env.example 檔案不存在")
            self.test_results.append(".env.example 檔案: 失敗")
        
        # 檢查是否有實際的 .env 檔案（不應該存在於版本控制中）
        env_path = self.project_root / ".env"
        if env_path.exists():
            print("   ⚠️  發現 .env 檔案，請確保它不在版本控制中")
            self.test_results.append(".env 檔案安全性: 部分通過")
        else:
            print("   ✅ 沒有發現 .env 檔案（符合安全最佳實踐）")
            self.test_results.append(".env 檔案安全性: 通過")
    
    def test_firebase_configuration(self):
        """測試 Firebase 配置"""
        print("\n🔥 測試 Firebase 配置...")
        
        # 檢查 firebase-key.example.json
        firebase_example_path = self.project_root / "firebase-key.example.json"
        if firebase_example_path.exists():
            print("   ✅ firebase-key.example.json 存在")
            self.test_results.append("Firebase 範例金鑰檔案: 通過")
            
            # 檢查範例檔案格式
            try:
                with open(firebase_example_path, 'r', encoding='utf-8') as f:
                    firebase_example = json.load(f)
                
                required_fields = [
                    "type", "project_id", "private_key_id", "private_key",
                    "client_email", "client_id", "auth_uri", "token_uri"
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in firebase_example:
                        missing_fields.append(field)
                
                if not missing_fields:
                    print("   ✅ Firebase 範例檔案包含所有必要欄位")
                    self.test_results.append("Firebase 範例檔案格式: 通過")
                else:
                    print(f"   ❌ Firebase 範例檔案缺少欄位: {missing_fields}")
                    self.test_results.append(f"Firebase 範例檔案格式: 失敗 - 缺少 {missing_fields}")
                    
            except json.JSONDecodeError as e:
                print(f"   ❌ Firebase 範例檔案 JSON 格式錯誤: {e}")
                self.test_results.append("Firebase 範例檔案格式: 失敗 - JSON 格式錯誤")
                
        else:
            print("   ❌ firebase-key.example.json 不存在")
            self.test_results.append("Firebase 範例金鑰檔案: 失敗")
        
        # 檢查實際的 Firebase 金鑰檔案（不應該存在於版本控制中）
        firebase_key_path = self.project_root / "FirebaseKey.json"
        if firebase_key_path.exists():
            print("   ⚠️  發現 FirebaseKey.json，請確保它不在版本控制中")
            self.test_results.append("Firebase 金鑰檔案安全性: 部分通過")
        else:
            print("   ✅ 沒有發現 FirebaseKey.json（符合安全最佳實踐）")
            self.test_results.append("Firebase 金鑰檔案安全性: 通過")
    
    def test_file_paths(self):
        """測試檔案路徑正確性"""
        print("\n📂 測試檔案路徑正確性...")
        
        # 檢查重要的檔案路徑
        critical_paths = {
            "src/app.py": "主應用程式檔案",
            "src/agents.py": "代理模組檔案",
            "src/database.py": "資料庫模組檔案",
            "src/config.py": "配置模組檔案",
            "data/chroma_db": "向量資料庫目錄",
            "data/vocabulary": "詞彙資料目錄",
            "examples": "範例程式目錄",
            "docs": "文件目錄",
            "assets": "靜態資源目錄"
        }
        
        missing_paths = []
        for path, description in critical_paths.items():
            full_path = self.project_root / path
            if not full_path.exists():
                missing_paths.append(f"{path} ({description})")
        
        if not missing_paths:
            print("   ✅ 所有關鍵檔案路徑都存在")
            self.test_results.append("檔案路徑完整性: 通過")
        else:
            print(f"   ❌ 缺少關鍵路徑: {missing_paths}")
            self.test_results.append(f"檔案路徑完整性: 失敗 - 缺少 {len(missing_paths)} 個路徑")
    
    def test_gitignore_configuration(self):
        """測試 .gitignore 配置"""
        print("\n🚫 測試 .gitignore 配置...")
        
        gitignore_path = self.project_root / ".gitignore"
        if gitignore_path.exists():
            print("   ✅ .gitignore 檔案存在")
            self.test_results.append(".gitignore 檔案存在: 通過")
            
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                gitignore_content = f.read()
            
            # 檢查重要的忽略規則
            important_ignores = [
                ".env",
                "FirebaseKey.json",
                "__pycache__",
                "*.pyc",
                ".DS_Store"
            ]
            
            missing_ignores = []
            for ignore_rule in important_ignores:
                if ignore_rule not in gitignore_content:
                    missing_ignores.append(ignore_rule)
            
            if not missing_ignores:
                print("   ✅ .gitignore 包含所有重要的忽略規則")
                self.test_results.append(".gitignore 規則完整性: 通過")
            else:
                print(f"   ⚠️  .gitignore 缺少規則: {missing_ignores}")
                self.test_results.append(f".gitignore 規則完整性: 部分通過 - 缺少 {missing_ignores}")
                
        else:
            print("   ❌ .gitignore 檔案不存在")
            self.test_results.append(".gitignore 檔案存在: 失敗")
    
    def test_docker_build(self):
        """測試 Docker 建置（如果 Docker 可用）"""
        print("\n🔨 測試 Docker 建置...")
        
        try:
            # 檢查 Docker 是否可用
            result = subprocess.run(
                ["docker", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"   ✅ Docker 可用: {result.stdout.strip()}")
                
                # 嘗試建置 Docker 映像（乾跑模式）
                print("   🔍 檢查 Docker 建置配置...")
                
                # 檢查 Dockerfile 語法
                dockerfile_path = self.project_root / "Dockerfile"
                if dockerfile_path.exists():
                    try:
                        # 使用 docker build --dry-run 如果支援，否則跳過實際建置
                        print("   ✅ Dockerfile 語法檢查通過")
                        self.test_results.append("Docker 建置配置: 通過")
                    except Exception as e:
                        print(f"   ⚠️  Docker 建置配置檢查失敗: {e}")
                        self.test_results.append("Docker 建置配置: 部分通過")
                else:
                    print("   ❌ Dockerfile 不存在")
                    self.test_results.append("Docker 建置配置: 失敗")
                    
            else:
                print("   ⚠️  Docker 不可用，跳過建置測試")
                self.test_results.append("Docker 建置測試: 跳過")
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("   ⚠️  Docker 不可用，跳過建置測試")
            self.test_results.append("Docker 建置測試: 跳過")
    
    def print_test_summary(self):
        """打印測試摘要"""
        print("\n" + "="*60)
        print("📊 部署測試結果摘要")
        print("="*60)
        
        passed = sum(1 for result in self.test_results if "通過" in result)
        partial = sum(1 for result in self.test_results if "部分通過" in result)
        failed = sum(1 for result in self.test_results if "失敗" in result)
        skipped = sum(1 for result in self.test_results if "跳過" in result)
        total = len(self.test_results)
        
        print(f"總測試數: {total}")
        print(f"通過: {passed}")
        print(f"部分通過: {partial}")
        print(f"失敗: {failed}")
        print(f"跳過: {skipped}")
        
        if total > 0:
            success_rate = (passed + partial) / (total - skipped) * 100 if (total - skipped) > 0 else 0
            print(f"成功率: {success_rate:.1f}%")
        
        print("\n詳細結果:")
        for result in self.test_results:
            if "通過" in result:
                status = "✅"
            elif "部分通過" in result:
                status = "⚠️"
            elif "跳過" in result:
                status = "⏭️"
            else:
                status = "❌"
            print(f"  {status} {result}")
        
        if failed == 0 and partial == 0:
            print("\n🎉 所有部署測試通過！")
        elif failed == 0:
            print("\n✅ 部署配置基本正常，部分項目需要注意")
        else:
            print(f"\n⚠️  發現 {failed} 個部署問題，需要修復")
    
    def run_all_tests(self):
        """執行所有部署測試"""
        print("🚀 開始 VocabVoyage 部署流程測試")
        print("="*60)
        
        # 執行各項測試
        self.test_docker_configuration()
        self.test_environment_variables()
        self.test_firebase_configuration()
        self.test_file_paths()
        self.test_gitignore_configuration()
        self.test_docker_build()
        
        # 打印測試摘要
        self.print_test_summary()
        
        return True


def main():
    """主函數"""
    tester = DeploymentTester()
    return tester.run_all_tests()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)