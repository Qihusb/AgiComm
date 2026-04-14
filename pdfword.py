import os
from pdf2docx import Converter

def pdf_to_word(pdf_path, word_path):
    """
    将 PDF 转换为 Word，特别优化了表格识别
    """
    try:
        # 初始化转换器
        cv = Converter(pdf_path)
        
        # multi_processing=True 开启多进程加速 (适用于大文件)
        # start=0, end=None 表示转换所有页面
        cv.convert(word_path, start=0, end=None)
        
        # 关闭转换器
        cv.close()
        print(f"转换成功: {word_path}")
        
    except Exception as e:
        print(f"转换失败: {e}")

if __name__ == "__main__":
    # 执行转换
    pdf_to_word(r"C:\Users\86176\Desktop\01.pdf", r"C:\Users\86176\Desktop\output.docx")