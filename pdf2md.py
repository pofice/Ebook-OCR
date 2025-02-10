import os
from pathlib import Path
import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_epub_to_pdf(input_path, output_path):
    try:
        # 使用 Calibre 的 ebook-convert 命令行工具
        cmd = ['ebook-convert', str(input_path), str(output_path)]
        
        # 执行转换命令
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 检查转换结果
        if process.returncode == 0:
            return True
        else:
            logger.error(f"Conversion error: {process.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error converting {input_path}: {str(e)}")
        return False

def main():
    # Create input and output directories if they don't exist
    input_dir = Path("input")
    output_dir = Path("output")
    
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    # Get all EPUB files from input directory
    epub_files = list(input_dir.glob("*.epub"))
    
    if not epub_files:
        logger.warning("No EPUB files found in input directory")
        return
        
    for epub_file in epub_files:
        # Create output PDF path with same name
        output_path = output_dir / f"{epub_file.stem}.pdf"
        
        logger.info(f"Converting: {epub_file.name}")
        if convert_epub_to_pdf(str(epub_file), str(output_path)):
            logger.info(f"Successfully converted to: {output_path.name}")
        else:
            logger.error(f"Failed to convert: {epub_file.name}")

if __name__ == "__main__":
    main()