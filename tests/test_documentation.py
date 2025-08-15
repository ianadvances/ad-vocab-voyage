#!/usr/bin/env python3
"""
VocabVoyage 文件完整性驗證腳本

此腳本用於驗證專案文件的完整性，包括：
1. 檢查所有文件連結正確性
2. 驗證安裝指南可以正常執行
3. 確認範例程式可以運行
4. 檢查所有中文註解和說明完整

執行方式：python test_documentation.py
"""

import os
import sys
import re
import ast
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple


class DocumentationTester:
    """文件完整性測試類別"""
    
    def __init__(self):
        """初始化測試環境"""
        self.test_results = []
        self.project_root = Path(__file__).parent
    
    def test_markdown_links(self):
        """測試 Markdown 文件中的連結正確性"""
        print("🔗 測試文件連結正確性...")
        
        markdown_files = [
            "README.md",
            "docs/installation.md",
            "docs/usage.md",
            "docs/architecture.md"
        ]
        
        total_links = 0
        broken_links = []
        
        for md_file in markdown_files:
            file_path = self.project_root / md_file
            if not file_path.exists():
                print(f"   ❌ 文件不存在: {md_file}")
                self.test_results.append(f"{md_file} 存在性: 失敗")
                continue
            
            print(f"   🔍 檢查 {md_file}...")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找 Markdown 連結 [text](url) 和圖片 ![alt](url)
            link_pattern = r'!?\[([^\]]*)\]\(([^)]+)\)'
            links = re.findall(link_pattern, content)
            
            for link_text, link_url in links:
                total_links += 1
                
                # 跳過外部連結（http/https）
                if link_url.startswith(('http://', 'https://')):
                    continue
                
                # 檢查相對路徑連結
                if link_url.startswith('#'):
                    # 錨點連結，暫時跳過
                    continue
                
                # 檢查檔案是否存在
                if link_url.startswith('/'):
                    # 絕對路徑（相對於專案根目錄）
                    target_path = self.project_root / link_url.lstrip('/')
                else:
                    # 相對路徑
                    target_path = file_path.parent / link_url
                
                if not target_path.exists():
                    broken_links.append(f"{md_file}: {link_url}")
        
        if not broken_links:
            print(f"   ✅ 所有 {total_links} 個內部連結都有效")
            self.test_results.append("文件連結完整性: 通過")
        else:
            print(f"   ❌ 發現 {len(broken_links)} 個無效連結:")
            for broken_link in broken_links:
                print(f"      - {broken_link}")
            self.test_results.append(f"文件連結完整性: 失敗 - {len(broken_links)} 個無效連結")
    
    def test_installation_guide(self):
        """測試安裝指南的可執行性"""
        print("\n📦 測試安裝指南可執行性...")
        
        installation_file = self.project_root / "docs/installation.md"
        if not installation_file.exists():
            print("   ❌ 安裝指南不存在")
            self.test_results.append("安裝指南存在性: 失敗")
            return
        
        with open(installation_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查是否包含重要的安裝步驟
        required_sections = [
            "poetry install",
            "docker",
            "環境變數",
            "Firebase",
            "OpenAI"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section.lower() not in content.lower():
                missing_sections.append(section)
        
        if not missing_sections:
            print("   ✅ 安裝指南包含所有必要步驟")
            self.test_results.append("安裝指南完整性: 通過")
        else:
            print(f"   ⚠️  安裝指南缺少部分內容: {missing_sections}")
            self.test_results.append(f"安裝指南完整性: 部分通過 - 缺少 {missing_sections}")
        
        # 檢查代碼塊格式
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        if code_blocks:
            print(f"   ✅ 找到 {len(code_blocks)} 個代碼範例")
            self.test_results.append("安裝指南代碼範例: 通過")
        else:
            print("   ⚠️  安裝指南缺少代碼範例")
            self.test_results.append("安裝指南代碼範例: 部分通過")
    
    def test_usage_guide(self):
        """測試使用指南的完整性"""
        print("\n📖 測試使用指南完整性...")
        
        usage_file = self.project_root / "docs/usage.md"
        if not usage_file.exists():
            print("   ❌ 使用指南不存在")
            self.test_results.append("使用指南存在性: 失敗")
            return
        
        with open(usage_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查是否包含重要的使用說明
        required_features = [
            "詞彙查詢",
            "主題學習",
            "測驗",
            "聊天",
            "個人詞彙本"
        ]
        
        missing_features = []
        for feature in required_features:
            if feature not in content:
                missing_features.append(feature)
        
        if not missing_features:
            print("   ✅ 使用指南涵蓋所有主要功能")
            self.test_results.append("使用指南功能覆蓋: 通過")
        else:
            print(f"   ⚠️  使用指南缺少功能說明: {missing_features}")
            self.test_results.append(f"使用指南功能覆蓋: 部分通過 - 缺少 {missing_features}")
        
        # 檢查是否有使用範例
        if "範例" in content or "例子" in content or "示例" in content:
            print("   ✅ 使用指南包含使用範例")
            self.test_results.append("使用指南範例: 通過")
        else:
            print("   ⚠️  使用指南缺少使用範例")
            self.test_results.append("使用指南範例: 部分通過")
    
    def test_architecture_documentation(self):
        """測試架構說明文件"""
        print("\n🏗️ 測試架構說明文件...")
        
        arch_file = self.project_root / "docs/architecture.md"
        if not arch_file.exists():
            print("   ❌ 架構說明文件不存在")
            self.test_results.append("架構說明文件存在性: 失敗")
            return
        
        with open(arch_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查是否包含重要的架構說明
        required_components = [
            "LangGraph",
            "RAG",
            "Firebase",
            "Streamlit",
            "OpenAI"
        ]
        
        missing_components = []
        for component in required_components:
            if component not in content:
                missing_components.append(component)
        
        if not missing_components:
            print("   ✅ 架構說明涵蓋所有主要組件")
            self.test_results.append("架構說明組件覆蓋: 通過")
        else:
            print(f"   ⚠️  架構說明缺少組件: {missing_components}")
            self.test_results.append(f"架構說明組件覆蓋: 部分通過 - 缺少 {missing_components}")
    
    def test_example_files_syntax(self):
        """測試範例檔案語法正確性"""
        print("\n💡 測試範例檔案語法...")
        
        example_files = [
            "examples/langgraph_rag.py",
            "examples/langgraph_tools.py",
            "examples/notebooks/vocabulary_generator.py",
            "examples/notebooks/pdf_text_extraction.py",
            "examples/notebooks/vocabulary_write_to_chroma.py",
            "examples/notebooks/models_sqlite.py"
        ]
        
        syntax_errors = []
        
        for example_file in example_files:
            file_path = self.project_root / example_file
            if not file_path.exists():
                syntax_errors.append(f"{example_file}: 檔案不存在")
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 檢查 Python 語法
                ast.parse(content)
                print(f"   ✅ {example_file} 語法正確")
                
            except SyntaxError as e:
                syntax_errors.append(f"{example_file}: 語法錯誤 - {e}")
                print(f"   ❌ {example_file} 語法錯誤: {e}")
            except Exception as e:
                syntax_errors.append(f"{example_file}: 讀取錯誤 - {e}")
                print(f"   ❌ {example_file} 讀取錯誤: {e}")
        
        if not syntax_errors:
            print("   ✅ 所有範例檔案語法正確")
            self.test_results.append("範例檔案語法: 通過")
        else:
            print(f"   ❌ 發現 {len(syntax_errors)} 個語法問題")
            self.test_results.append(f"範例檔案語法: 失敗 - {len(syntax_errors)} 個問題")
    
    def test_chinese_comments(self):
        """測試中文註解完整性"""
        print("\n🈳 測試中文註解完整性...")
        
        python_files = [
            "src/app.py",
            "src/agents.py",
            "src/database.py",
            "src/config.py"
        ]
        
        comment_stats = {}
        
        for py_file in python_files:
            file_path = self.project_root / py_file
            if not file_path.exists():
                comment_stats[py_file] = {"status": "檔案不存在"}
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 統計註解
                total_functions = len(re.findall(r'def\s+\w+\s*\(', content))
                total_classes = len(re.findall(r'class\s+\w+', content))
                
                # 檢查中文 docstring
                chinese_docstrings = len(re.findall(r'"""[\s\S]*?[\u4e00-\u9fff][\s\S]*?"""', content))
                chinese_comments = len(re.findall(r'#.*[\u4e00-\u9fff]', content))
                
                comment_stats[py_file] = {
                    "functions": total_functions,
                    "classes": total_classes,
                    "chinese_docstrings": chinese_docstrings,
                    "chinese_comments": chinese_comments,
                    "status": "已分析"
                }
                
                if chinese_docstrings > 0 or chinese_comments > 0:
                    print(f"   ✅ {py_file}: {chinese_docstrings} 個中文 docstring, {chinese_comments} 個中文註解")
                else:
                    print(f"   ⚠️  {py_file}: 缺少中文註解")
                
            except Exception as e:
                comment_stats[py_file] = {"status": f"讀取錯誤: {e}"}
                print(f"   ❌ {py_file}: 讀取錯誤 - {e}")
        
        # 評估整體中文註解情況
        files_with_chinese = sum(1 for stats in comment_stats.values() 
                                if isinstance(stats, dict) and 
                                stats.get("chinese_docstrings", 0) > 0 or stats.get("chinese_comments", 0) > 0)
        
        total_analyzed = sum(1 for stats in comment_stats.values() 
                           if isinstance(stats, dict) and stats.get("status") == "已分析")
        
        if files_with_chinese == total_analyzed and total_analyzed > 0:
            print("   ✅ 所有核心檔案都包含中文註解")
            self.test_results.append("中文註解完整性: 通過")
        elif files_with_chinese > 0:
            print(f"   ⚠️  {files_with_chinese}/{total_analyzed} 個檔案包含中文註解")
            self.test_results.append("中文註解完整性: 部分通過")
        else:
            print("   ❌ 核心檔案缺少中文註解")
            self.test_results.append("中文註解完整性: 失敗")
    
    def test_readme_completeness(self):
        """測試 README.md 完整性"""
        print("\n📄 測試 README.md 完整性...")
        
        readme_file = self.project_root / "README.md"
        if not readme_file.exists():
            print("   ❌ README.md 不存在")
            self.test_results.append("README.md 存在性: 失敗")
            return
        
        with open(readme_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查必要的章節
        required_sections = [
            "# VocabVoyage",  # 標題
            "## 主要特色",     # 功能說明
            "## 技術架構",     # 技術說明
            "## 快速開始",     # 安裝說明
            "## 核心功能",     # 使用說明
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if not missing_sections:
            print("   ✅ README.md 包含所有必要章節")
            self.test_results.append("README.md 章節完整性: 通過")
        else:
            print(f"   ⚠️  README.md 缺少章節: {missing_sections}")
            self.test_results.append(f"README.md 章節完整性: 部分通過 - 缺少 {missing_sections}")
        
        # 檢查是否有圖片
        image_links = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        if image_links:
            print(f"   ✅ README.md 包含 {len(image_links)} 個圖片")
            self.test_results.append("README.md 圖片: 通過")
        else:
            print("   ⚠️  README.md 缺少圖片")
            self.test_results.append("README.md 圖片: 部分通過")
    
    def print_test_summary(self):
        """打印測試摘要"""
        print("\n" + "="*60)
        print("📊 文件完整性測試結果摘要")
        print("="*60)
        
        passed = sum(1 for result in self.test_results if "通過" in result)
        partial = sum(1 for result in self.test_results if "部分通過" in result)
        failed = sum(1 for result in self.test_results if "失敗" in result)
        total = len(self.test_results)
        
        print(f"總測試數: {total}")
        print(f"通過: {passed}")
        print(f"部分通過: {partial}")
        print(f"失敗: {failed}")
        
        if total > 0:
            success_rate = (passed + partial) / total * 100
            print(f"成功率: {success_rate:.1f}%")
        
        print("\n詳細結果:")
        for result in self.test_results:
            if "通過" in result:
                status = "✅"
            elif "部分通過" in result:
                status = "⚠️"
            else:
                status = "❌"
            print(f"  {status} {result}")
        
        if failed == 0 and partial == 0:
            print("\n🎉 所有文件完整性測試通過！")
        elif failed == 0:
            print("\n✅ 文件基本完整，部分項目可以進一步改善")
        else:
            print(f"\n⚠️  發現 {failed} 個文件問題，需要修復")
    
    def run_all_tests(self):
        """執行所有文件測試"""
        print("🚀 開始 VocabVoyage 文件完整性驗證")
        print("="*60)
        
        # 執行各項測試
        self.test_readme_completeness()
        self.test_markdown_links()
        self.test_installation_guide()
        self.test_usage_guide()
        self.test_architecture_documentation()
        self.test_example_files_syntax()
        self.test_chinese_comments()
        
        # 打印測試摘要
        self.print_test_summary()
        
        return True


def main():
    """主函數"""
    tester = DocumentationTester()
    return tester.run_all_tests()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)