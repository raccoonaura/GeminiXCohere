from src import file_handler
from src import utils
from ebooklib import epub
from pathlib import Path
import pdfplumber
import subprocess
import html2text
import ebooklib
import shutil
import os

TEMP_DIR = "embeds/temp"

handler = html2text.HTML2Text()
handler.ignore_links = True  # 避免連結把chunking搞砸 因為Gemini一次只能發100個chunks
handler.ignore_images = True  # 不保留圖片
handler.ignore_emphasis = False  # 保留斜體和粗體
handler.skip_internal_links = True  # 不保留傳送到HTML某一部分的連結
handler.bypass_tables = False  # 保留表格
handler.body_width = 0  # 不自動換行 保留HTML原本的換行

def reset_temp():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)

def handle_document(files):
    utils.set_marker()
    print("Converting...")
    text = []
    for file in files:
        path = "embeds/" + file
        # print(f'Converting {path}')  # debug
        name, ext = os.path.splitext(path)
        if ext.lower() in ["txt", ".md", ".markdown"]:
            with open(path, "r", encoding="utf-8") as f: text.append(f.read())
        elif ext.lower() in [".epub"]: text.append(epub_to_md(path))
        elif ext.lower() in [".pdf"]: text.append(pdf_to_md(path))
        elif ext.lower() in [".html", ".htm"]: text.append(html_to_md(path))
        elif ext.lower() in file_handler.doc_types: text.append(html_to_md(file_to_html(path)))
        if "error!" in text: return "error!"
    utils.clear_screen()
    print("Converting...Done!")
    # with open("debug_output.txt", "w", encoding="utf-8") as f: f.write("\n\n".join(text))  # debug
    return "\n\n".join(text)

def file_to_html(path):
    print("Might take a while if the file contains multiple images!")
    path = Path(path)
    reset_temp()
    candidates = [  # 一系列LibreOffice通常會有的名字/檔案位置
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        "soffice",  # for linux (probably, i dont really use use linux)
        "libreoffice",
    ]
    for c in candidates:  # 找到LibreOffice的位置
        if Path(c).exists():
            soffice = c
            break

    if soffice is None:  # 確認LibreOffice是否存在
        return RuntimeError("LibreOffice not found! Please install it before continuing!")
    cmd = [  # 指令
        soffice,
        "--headless",
        "--convert-to", "html",
        "--outdir", str(TEMP_DIR),
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)  # 跑上面的指令
    if result.returncode != 0:  # 如果成功的話 系統應回傳0
        return RuntimeError(
            f"Failed while converting files with LibreOffice! Please make sure you have it installed and is able to run {soffice} in cmd!\n"
            f"cmd: {' '.join(cmd)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    for f in Path(TEMP_DIR).glob("*"):
        if f.is_file() and f.suffix.lower() != ".html": f.unlink()  # 刪除HTML以外的東西 (通常是圖片)
    return TEMP_DIR + "/" + (path.stem + ".html")

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