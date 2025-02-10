import os
import shutil
from pathlib import Path
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import mobi

def convert_pdf_to_txt(input_path, output_path):
    converter = PdfConverter(artifact_dict=create_model_dict())
    rendered = converter(str(input_path))
    text, _, _ = text_from_rendered(rendered)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

def convert_epub_to_txt(input_path, output_path):
    try:
        try:
            # 尝试传入 ignore_ncx 参数
            book = epub.read_epub(str(input_path), ignore_ncx=True)
        except TypeError:
            print("ignore_ncx 参数不支持，使用默认参数读取 EPUB 文件")
            book = epub.read_epub(str(input_path))
        text = []
        
        # 处理每个文档项
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                try:
                    content = item.get_content()
                    if content:
                        # 使用更安全的解析方式
                        soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')
                        if soup and soup.body:
                            # 只获取body内容，避免处理头部元数据
                            content_text = soup.body.get_text(separator='\n', strip=True)
                            if content_text:
                                text.append(content_text)
                except Exception as e:
                    print(f"Warning: Error processing EPUB item: {str(e)}")
                    continue
        
        # 如果没有提取到任何文本，抛出异常
        if not text:
            raise ValueError("No text content found in EPUB file")
            
        # 写入文件，确保使用UTF-8编码
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(text))
            
    except Exception as e:
        print(f"Error in EPUB conversion: {str(e)}")
        raise

def convert_mobi_to_txt(input_path, output_path):
    book = mobi.Mobi(str(input_path))
    book.parse()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(book.get_text())

def main():
    input_dir = Path("input")
    output_dir = Path("output")
    
    # 创建输出目录（如果不存在）
    output_dir.mkdir(exist_ok=True)
    
    for file_path in input_dir.glob("*"):
        if not file_path.is_file():
            continue
            
        output_path = output_dir / (file_path.stem + ".txt")
        
        try:
            if file_path.suffix.lower() == '.pdf':
                convert_pdf_to_txt(file_path, output_path)
            elif file_path.suffix.lower() == '.epub':
                print(f"Processing EPUB file: {file_path.name}")
                convert_epub_to_txt(file_path, output_path)
            elif file_path.suffix.lower() == '.mobi':
                convert_mobi_to_txt(file_path, output_path)
            print(f"Successfully converted: {file_path.name}")
        except Exception as e:
            print(f"Error converting {file_path.name}: {str(e)}")
            # 如果转换失败，记录到错误日志文件
            with open("conversion_errors.log", "a", encoding="utf-8") as log:
                log.write(f"{file_path.name}: {str(e)}\n")

if __name__ == "__main__":
    main()
