from src import response_handler
from src import file_handler
from src import utils
from pathlib import Path
import subprocess
import mimetypes
import shutil
import base64
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = "embeds/temp"

path = os.path.join(BASE_DIR, "embeds", "note.txt")
gemini_image = []
command_image = []
skip_gemini = False
skip_command = False

def reset_temp():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)

doc_types = [".rtf",  # ik this is more of a text file but hey its libreoffice handling it
             ".odt", ".ott", ".fodt",
             ".odp", ".otp", ".fodp",
             ".odm", ".oth",
             ".sxw", ".stw", ".sxg",
             ".sxi", ".sti",
             ".docx", ".dotx",
             ".docm", ".dotm",
             ".doc", ".dot",
             ".pptx", ".potx",
             ".pptm", ".potm",
             ".ppt", ".pot"]
             # all these file types are supposed to be supported as theyre all listed in libreoffices own docs
             # if theyre not, its their fault (at least very likely, unless im tweaking)

sheet_types = [".xlsx", ".xltx", ".xlsb",
               ".xlsm", ".xltm",
               ".xls", ".xlt",
               ".ods", ".ots",
               ".fods", ".odf",  # untested: xlsb xltm odf, but supposed to be working
               ".csv", ".tsv",  # not working: tsv, or my tsv testing file is broken
               ".json", ".xml", ".yaml"]

def get_file():
    files = os.listdir("embeds")
    files = [f for f in files if not f.startswith('.') and os.path.isfile(os.path.join("embeds", f))]
    if not files:
        print(f"Error! There's no file in the embeds folder!")
        return None

    files = [f for f in files
            if os.path.isfile(os.path.join("embeds", f))
            and any(f.endswith(ext) for ext in doc_types + sheet_types + [".txt", ".md", ".markdown",
                                                                          ".html", ".htm", ".epub", ".pdf",
                                                                          ".png", ".jpg", ".jpeg", ".webp",
                                                                          ".heic", ".heif", ".gif"])]
    if not files:
        print(f"Error! None of the files in the embeds folder are supported!")
        return None

    utils.set_marker()

    image = []
    document = []
    spreadsheet = []

    while True:
        try:
            print("Available files:\n")
            for i, filename in enumerate(files, 1):
                print(f"└ {i}. {filename}")

            print(f'\nImage: {"(Not selected)" if image == [] else ", ".join(image)}\nDocument: {"(Not selected)" if document == [] else ", ".join(document)}\nSpreadsheet: {"(Not selected)" if spreadsheet == [] else ", ".join(spreadsheet)}\n(Type "done" to finish selecting.)')
            choice = input(f'\nSelect the desired file (1~{len(files)}): ').strip()
            if choice == "done":
                utils.clear_screen()
                response_handler.document = document
                response_handler.image = image
                response_handler.spreadsheet = spreadsheet
                return
            choice = int(choice)
            name, ext = os.path.splitext(files[choice - 1])
            if 1 <= choice <= len(files):
                if ext.lower() in [".png", ".jpg", ".jpeg", ".webp", ".heic", ".heif", ".gif"]:
                    if files[choice - 1] in image:
                        image.remove(files[choice - 1])
                    else:
                        image.append(files[choice - 1])
                elif ext.lower() in sheet_types:
                    if files[choice - 1] in spreadsheet:
                        spreadsheet.remove(files[choice - 1])
                    else:
                        spreadsheet.append(files[choice - 1])
                else:
                    if files[choice - 1] in document:
                        document.remove(files[choice - 1])
                    else:
                        document.append(files[choice - 1])
                utils.clear_screen()
            else:
                utils.clear_screen()
        except:
            utils.clear_screen()
            continue

def file_to_libreoffice(path, type):
    path = Path(path)
    file_handler.reset_temp()
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
        "--convert-to", type,
        "--outdir", str(file_handler.TEMP_DIR),
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)  # 跑上面的指令
    if result.returncode != 0:  # 如果成功的話 系統應回傳0
        return RuntimeError(
            f"Failed while converting files with LibreOffice! Please make sure you have it installed and is able to run {soffice} in cmd!\n"
            f"cmd: {' '.join(cmd)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    for f in Path(file_handler.TEMP_DIR).glob("*"):
        if f.is_file() and f.suffix.lower() != "." + type: f.unlink()  # 刪除指定檔案類型以外的東西 (通常是圖片)
    return file_handler.TEMP_DIR + "/" + (path.stem + "." + type)

def handle_image(files):
    global gemini_image, command_image, skip_gemini, skip_command
    skip_gemini = False
    skip_command = False
    for file in files:
        path = "embeds/" + file
        mime_type, _ = mimetypes.guess_type(path)
        with open(path, 'rb') as f: image_bytes = f.read()
        encoded_string = base64.b64encode(image_bytes).decode("utf-8")
        name, ext = os.path.splitext(file)
        if ext.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
            gemini_image.append({"mime_type":mime_type, "data": image_bytes})
            command_image.append(f"data:{mime_type};base64,{encoded_string}")
        elif ext.lower() in [".heic", ".heif"]:
            gemini_image.append({"mime_type":mime_type, "data": image_bytes})
            skip_command = True
        elif ext.lower() in ".gif":
            command_image.append(f"data:{mime_type};base64,{encoded_string}")
            skip_gemini = True