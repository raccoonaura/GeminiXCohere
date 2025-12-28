from src import file_handler
from src import utils
from ebooklib import epub
from pathlib import Path
import pdfplumber
import html2text
import ebooklib
import os

handler = html2text.HTML2Text()
handler.ignore_links = True  # 避免連結把chunking搞砸 因為Gemini一次只能發100個chunks
handler.ignore_images = True  # 不保留圖片
handler.ignore_emphasis = False  # 保留斜體和粗體
handler.skip_internal_links = True  # 不保留傳送到HTML某一部分的連結
handler.bypass_tables = False  # 保留表格
handler.body_width = 0  # 不自動換行 保留HTML原本的換行

def handle_document(files):
    utils.set_marker()
    print("Converting...")
    text = []
    for file in files:
        path = "embeds/" + file
        name, ext = os.path.splitext(path)
        if ext.lower() in [".txt", ".md", ".markdown"]:
            with open(path, "r", encoding="utf-8") as f: text.append(f.read())
        elif ext.lower() in [".epub"]: text.append(epub_to_md(path))
        elif ext.lower() in [".pdf"]: text.append(pdf_to_md(path))
        elif ext.lower() in [".html", ".htm"]: text.append(html_to_md(path))
        elif ext.lower() in file_handler.doc_types:
            print("Might take a while if the file contains multiple images!")
            text.append(html_to_md(file_handler.file_to_libreoffice(path, "html")))
        if "error!" in text: return "error!"
    utils.clear_screen()
    print("Converting...Done!")
    return "\n\n".join(text)

def html_to_md(path):
    if path is RuntimeError: return "error!"
    html = Path(path).read_text(encoding="utf-8", errors="ignore")
    return handler.handle(html)

def epub_to_md(path):
    book = epub.read_epub(path)  # 把書籍裡每一章取出
    list = []  # 轉換成Markdown後的每個章節會存入這個清單中
    for item in book.get_items():  # 一章一章處理
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            html = item.get_body_content().decode("utf-8", errors="ignore")  # 只取書籍內容 並轉換為HTML
            md = handler.handle(html)  # 從HTML轉換為Markdown
            list.append(md)  # 把目前這個章節存入清單中
    return "\n\n".join(list)  # 把清單內每個章節存入到一個字串中 每章用空行隔開

def pdf_to_md(path):
    list = []  # 轉換成Markdown後的每個頁面會存入這個清單中
    with pdfplumber.open(path) as pdf:  # 把檔案裡每一頁取出
        for page in pdf.pages:  # 一頁一頁處理
            page_text = page.extract_text() or ""  # 如果頁面是空的 就不加入任何東西
            list.append(page_text)  # 把目前這個頁面存入清單中
    return "\n\n".join(list)  # 把清單內每個頁面存入到一個字串中 每頁用空行隔開