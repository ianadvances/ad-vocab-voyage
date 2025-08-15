"""
PDF 文字提取範例程式

這個程式展示了兩種從 PDF 文件中提取文字的方法：
1. 直接文字提取 - 使用 pypdf 庫直接提取 PDF 中的文字內容
2. OCR 文字識別 - 使用 pdf2image 和 pytesseract 進行光學字符識別

適用場景：
- 處理包含文字的 PDF 文件
- 從掃描的 PDF 文件中提取文字
- 支援中英文混合內容的識別
- 教育資源的數位化處理

技術特點：
- 支援多頁 PDF 處理
- 提供兩種提取方法的比較
- 支援繁體中文和英文的 OCR 識別
- 逐頁處理和標記

注意事項：
- OCR 方法需要安裝 Tesseract OCR 引擎
- 對於圖片型 PDF，建議使用 OCR 方法
- 對於文字型 PDF，直接提取方法更快更準確

作者：VocabVoyage 團隊
日期：2024年
"""

import pypdf
from pdf2image import convert_from_path
import pytesseract
import os
import sys
from pathlib import Path
import time

# ============================================================================
# 配置和常數
# ============================================================================

# 預設的 PDF 文件路徑
DEFAULT_PDF_PATH = 'TOEIC.pdf'

# OCR 支援的語言設定（繁體中文 + 英文）
OCR_LANGUAGES = 'chi_tra+eng'

# 輸出文件的編碼
OUTPUT_ENCODING = 'utf-8'

# ============================================================================
# 直接文字提取功能
# ============================================================================

def extract_text_directly(pdf_path: str) -> str:
    """
    使用 pypdf 直接從 PDF 提取文字
    
    這種方法適用於包含可選擇文字的 PDF 文件。
    對於掃描的 PDF 或圖片型 PDF，這種方法可能無法提取到文字。
    
    Args:
        pdf_path (str): PDF 文件的路徑
        
    Returns:
        str: 提取的文字內容，如果失敗則返回空字符串
        
    Raises:
        FileNotFoundError: 當 PDF 文件不存在時
        Exception: 當讀取 PDF 時發生其他錯誤
    """
    try:
        print(f"📖 開始直接提取文字：{pdf_path}")
        
        # 檢查文件是否存在
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"找不到 PDF 文件：{pdf_path}")
        
        extracted_text = ""
        
        # 打開並讀取 PDF 文件
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            total_pages = len(reader.pages)
            
            print(f"📄 PDF 總頁數：{total_pages}")
            
            # 逐頁提取文字
            for i, page in enumerate(reader.pages):
                print(f"  正在處理第 {i+1}/{total_pages} 頁...")
                
                page_text = page.extract_text()
                
                if page_text.strip():
                    # 如果頁面有文字內容，添加頁面標記
                    extracted_text += f"\n\n{'='*20} 第 {i+1} 頁 {'='*20}\n"
                    extracted_text += page_text
                    print(f"    ✅ 提取到 {len(page_text)} 個字符")
                else:
                    # 如果頁面沒有文字內容
                    extracted_text += f"\n\n{'='*20} 第 {i+1} 頁 {'='*20}\n"
                    extracted_text += "[此頁面沒有可提取的文字內容]\n"
                    print(f"    ⚠️  此頁面沒有可提取的文字")
        
        print(f"✅ 直接提取完成，總共提取 {len(extracted_text)} 個字符")
        return extracted_text
        
    except FileNotFoundError as e:
        print(f"❌ 文件錯誤：{e}")
        return ""
    except Exception as e:
        print(f"❌ 直接提取時發生錯誤：{str(e)}")
        return ""

# ============================================================================
# OCR 文字識別功能
# ============================================================================

def extract_text_with_ocr(pdf_path: str) -> str:
    """
    使用 OCR 技術從 PDF 提取文字
    
    這種方法將 PDF 轉換為圖片，然後使用 Tesseract OCR 引擎識別文字。
    適用於掃描的 PDF 文件或包含圖片文字的文件。
    
    Args:
        pdf_path (str): PDF 文件的路徑
        
    Returns:
        str: 識別的文字內容，如果失敗則返回空字符串
        
    Raises:
        FileNotFoundError: 當 PDF 文件不存在時
        Exception: 當 OCR 處理時發生錯誤
    """
    try:
        print(f"🔍 開始 OCR 文字識別：{pdf_path}")
        
        # 檢查文件是否存在
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"找不到 PDF 文件：{pdf_path}")
        
        # 檢查 Tesseract 是否可用
        try:
            pytesseract.get_tesseract_version()
        except Exception:
            print("❌ Tesseract OCR 引擎未安裝或無法訪問")
            print("請安裝 Tesseract OCR：https://github.com/tesseract-ocr/tesseract")
            return ""
        
        print("🖼️  正在將 PDF 轉換為圖片...")
        start_time = time.time()
        
        # 將 PDF 轉換為圖片
        images = convert_from_path(pdf_path)
        
        conversion_time = time.time() - start_time
        print(f"✅ 轉換完成，共 {len(images)} 頁，耗時 {conversion_time:.2f} 秒")
        
        extracted_text = ""
        
        # 對每個圖片頁面進行 OCR 識別
        for i, image in enumerate(images):
            print(f"  正在識別第 {i+1}/{len(images)} 頁...")
            
            try:
                # 使用 Tesseract 進行文字識別
                page_text = pytesseract.image_to_string(
                    image, 
                    lang=OCR_LANGUAGES,
                    config='--psm 6'  # 假設統一的文字塊
                )
                
                # 添加頁面標記
                extracted_text += f"\n\n{'='*20} 第 {i+1} 頁 (OCR) {'='*20}\n"
                
                if page_text.strip():
                    extracted_text += page_text
                    print(f"    ✅ 識別到 {len(page_text)} 個字符")
                else:
                    extracted_text += "[此頁面沒有識別到文字內容]\n"
                    print(f"    ⚠️  此頁面沒有識別到文字")
                    
            except Exception as e:
                print(f"    ❌ 第 {i+1} 頁 OCR 識別失敗：{str(e)}")
                extracted_text += f"[第 {i+1} 頁 OCR 識別失敗]\n"
        
        print(f"✅ OCR 識別完成，總共識別 {len(extracted_text)} 個字符")
        return extracted_text
        
    except FileNotFoundError as e:
        print(f"❌ 文件錯誤：{e}")
        return ""
    except Exception as e:
        print(f"❌ OCR 處理時發生錯誤：{str(e)}")
        return ""

# ============================================================================
# 文字保存功能
# ============================================================================

def save_extracted_text(text: str, output_path: str, method: str = ""):
    """
    將提取的文字保存到文件
    
    Args:
        text (str): 要保存的文字內容
        output_path (str): 輸出文件路徑
        method (str): 提取方法標識
    """
    try:
        # 確保輸出目錄存在
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 寫入文件
        with open(output_path, 'w', encoding=OUTPUT_ENCODING) as f:
            if method:
                f.write(f"提取方法：{method}\n")
                f.write(f"提取時間：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
            f.write(text)
        
        print(f"💾 文字已保存到：{output_path}")
        
    except Exception as e:
        print(f"❌ 保存文件時發生錯誤：{str(e)}")

# ============================================================================
# 比較和分析功能
# ============================================================================

def compare_extraction_methods(pdf_path: str):
    """
    比較兩種提取方法的結果
    
    Args:
        pdf_path (str): PDF 文件路徑
    """
    print("🔄 開始比較兩種提取方法...")
    print("=" * 60)
    
    # 方法1：直接提取
    print("\n📖 方法1：直接文字提取")
    print("-" * 30)
    direct_text = extract_text_directly(pdf_path)
    direct_length = len(direct_text.strip())
    
    # 方法2：OCR 識別
    print("\n🔍 方法2：OCR 文字識別")
    print("-" * 30)
    ocr_text = extract_text_with_ocr(pdf_path)
    ocr_length = len(ocr_text.strip())
    
    # 結果比較
    print("\n📊 提取結果比較")
    print("=" * 60)
    print(f"直接提取字符數：{direct_length:,}")
    print(f"OCR 識別字符數：{ocr_length:,}")
    
    if direct_length > 0 and ocr_length > 0:
        ratio = ocr_length / direct_length
        print(f"OCR/直接提取比率：{ratio:.2f}")
        
        if ratio > 1.2:
            print("💡 建議：OCR 識別到更多內容，可能包含圖片中的文字")
        elif ratio < 0.8:
            print("💡 建議：直接提取更準確，PDF 包含可選擇的文字")
        else:
            print("💡 建議：兩種方法結果相近，可選擇更快的直接提取")
    elif direct_length > 0:
        print("💡 建議：使用直接提取方法，PDF 包含可選擇的文字")
    elif ocr_length > 0:
        print("💡 建議：使用 OCR 方法，PDF 可能是掃描文件")
    else:
        print("⚠️  兩種方法都沒有提取到文字內容")
    
    # 保存結果
    if direct_text:
        save_extracted_text(
            direct_text, 
            f"extracted_text_direct.txt", 
            "直接文字提取"
        )
    
    if ocr_text:
        save_extracted_text(
            ocr_text, 
            f"extracted_text_ocr.txt", 
            "OCR 文字識別"
        )

# ============================================================================
# 主程式和命令列介面
# ============================================================================

def main():
    """主程式函數"""
    print("VocabVoyage PDF 文字提取工具")
    print("=" * 60)
    
    # 檢查命令列參數
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = DEFAULT_PDF_PATH
    
    print(f"📁 目標 PDF 文件：{pdf_path}")
    
    # 檢查文件是否存在
    if not os.path.exists(pdf_path):
        print(f"❌ 錯誤：找不到文件 {pdf_path}")
        print("\n使用方法：")
        print(f"  python {sys.argv[0]} [PDF文件路徑]")
        print(f"  例如：python {sys.argv[0]} document.pdf")
        return
    
    # 詢問用戶選擇提取方法
    print("\n請選擇提取方法：")
    print("1. 直接文字提取（適用於文字型 PDF）")
    print("2. OCR 文字識別（適用於掃描型 PDF）")
    print("3. 比較兩種方法")
    
    try:
        choice = input("\n請輸入選項 (1/2/3): ").strip()
        
        if choice == "1":
            print("\n" + "="*60)
            text = extract_text_directly(pdf_path)
            if text:
                save_extracted_text(text, "extracted_text_direct.txt", "直接文字提取")
            
        elif choice == "2":
            print("\n" + "="*60)
            text = extract_text_with_ocr(pdf_path)
            if text:
                save_extracted_text(text, "extracted_text_ocr.txt", "OCR 文字識別")
            
        elif choice == "3":
            print("\n" + "="*60)
            compare_extraction_methods(pdf_path)
            
        else:
            print("❌ 無效的選項")
            return
        
        print("\n✅ 處理完成！")
        
    except KeyboardInterrupt:
        print("\n\n👋 程式已中斷")
    except Exception as e:
        print(f"\n❌ 程式執行時發生錯誤：{str(e)}")

def show_help():
    """顯示幫助資訊"""
    print("VocabVoyage PDF 文字提取工具")
    print("=" * 60)
    print("\n功能說明：")
    print("  這個工具提供兩種方法從 PDF 文件中提取文字：")
    print("  1. 直接提取 - 適用於包含可選擇文字的 PDF")
    print("  2. OCR 識別 - 適用於掃描的 PDF 或圖片型 PDF")
    print("\n使用方法：")
    print(f"  python {sys.argv[0]} [PDF文件路徑]")
    print(f"  python {sys.argv[0]} --help")
    print("\n範例：")
    print(f"  python {sys.argv[0]} document.pdf")
    print(f"  python {sys.argv[0]} /path/to/scanned.pdf")
    print("\n依賴套件：")
    print("  - pypdf: PDF 直接文字提取")
    print("  - pdf2image: PDF 轉圖片")
    print("  - pytesseract: OCR 文字識別")
    print("  - Tesseract OCR 引擎（系統級安裝）")

# ============================================================================
# 程式入口點
# ============================================================================

if __name__ == "__main__":
    # 檢查是否請求幫助
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        show_help()
    else:
        main()