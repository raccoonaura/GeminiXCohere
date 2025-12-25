from src import response_handler
from src import utils
import mimetypes
import base64
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(BASE_DIR, "embeds", "note.txt")
gemini_image = []
command_image = []
skip_gemini = False
skip_command = False
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

def get_file():
    files = os.listdir("embeds")
    files = [f for f in files if not f.startswith('.') and os.path.isfile(os.path.join("embeds", f))]
    if not files:
        print(f"Error! There's no file in the embeds folder!")
        return None

    files = [f for f in files
            if os.path.isfile(os.path.join("embeds", f))
            and any(f.endswith(ext) for ext in doc_types + [".txt", ".md", ".markdown",
                                                            ".html", ".htm", ".epub", ".pdf",
                                                            ".png", ".jpg", ".jpeg", ".webp",
                                                            ".heic", ".heif", ".gif"])]
    if not files:
        print(f"Error! None of the files in the embeds folder are supported!")
        return None

    utils.set_marker()

    image = []
    document = []

    while True:
        try:
            print("Available files:\n")
            for i, filename in enumerate(files, 1):
                print(f"└ {i}. {filename}")

            print(f'\nImage: {"(Not selected)" if image == [] else ", ".join(image)}, Document: {"(Not selected)" if document == [] else ", ".join(document)}\n(Type "done" to finish selecting.)')
            choice = input(f'\nSelect the desired file (1~{len(files)}): ').strip()
            if choice == "done":
                utils.clear_screen()
                response_handler.document = document
                response_handler.image = image
                return
            choice = int(choice)
            name, ext = os.path.splitext(files[choice - 1])
            if 1 <= choice <= len(files):
                if ext.lower() in [".png", ".jpg", ".jpeg", ".webp", ".heic", ".heif", ".gif"]:
                    if files[choice - 1] in image:
                        image.remove(files[choice - 1])
                    else:
                        image.append(files[choice - 1])
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

def chunk_by_sentence(text, max_length, overlap):  # 我決定把每一句留下中文註解 因為我自己都快亂了:P
    """ max_length: 用字數計算, overlap: 用句數計算,
        sentences: 切斷後的本文, 含全部的句子, sentence: 本文切段後的一個句子,
        current_chunk: 一個段落, 好幾個句子, chunks: 切段並重新安排後的好幾個段落,
        tail: 上一個段落的尾端幾句, """

    sentences = re.split(r'(?<=[。！？.!?…])\s*', text)  # 遇到。！？.!?…這些符號之一就切成一句
    sentences = [s.strip() for s in sentences if s.strip()]  # 避免符號單獨一句

    chunks = []
    current_chunk = []
    current_length = 0
    i = 0
    while i < len(sentences):  # while現在確認的句數不超過全部句子的總數時
        sentence = sentences[i]  # 現在這句就是全部句子中的第i個

        if sentence.lstrip().startswith("#"):  # 如果這句是以#開頭
            if current_chunk:  # 如果current_chunk不是空的
                chunks.append(" ".join(current_chunk))  # 把current_chunk加入chunks裡
            current_chunk = [sentence]  # 全新的current_chunk加入含#的那句
            current_length = len(sentence)  # 把這句的字數設為總長度
            i += 1  # 換下一句
            continue

        if current_length + len(sentence) > max_length:  # 如果current_chunk新的總長度加上現在這句的字數"會"超過上限
            if current_chunk:  # 如果current_chunk不是空的
                chunks.append(" ".join(current_chunk))  # 把current_chunk加入chunks裡

                if len(current_chunk) > overlap:  # 如果現在的current_chunk包含的句數比overlap所保留的句數還多的時候
                    tail = current_chunk[-overlap:]  # 從尾部取出overlap所保留的句數, 保留起來
                else:  # 如果現在的current_chunk包含的句數跟overlap所保留的句數一樣多或更少的時候
                    tail = current_chunk[:]  # 把整段current_chunk全部保留下來

                while tail:  # 當tail存在時
                    tail_length = sum(len(s) for s in tail)  # 算出tail裡每一句的字數加總
                    if tail_length + len(sentence) <= max_length:  # 如果總字數加上這句的字數不會超過上限
                        break  # 離開這個迴圈
                    tail.pop(0)  # 把tail的第一句刪了, 然後回到這個迴圈的開頭再確認一次會不會超過次數

                current_chunk = tail  # 全新的current_chunk加入overlap的部分
                current_length = sum(len(s) for s in tail)  # 算字數

            if current_length + len(sentence) <= max_length:  # 如果current_chunk新的總長度加上現在這句的字數"不會"超過上限
                current_chunk.append(sentence)  # 把這句加入current_chunk
                current_length += len(sentence)  # 把這句的字數加入總長度
                i += 1
                continue

            else:  # 如果還是超過的話
                if current_chunk:  # 如果current_chunk不是空的
                    chunks.append(" ".join(current_chunk))  # 把current_chunk加入chunks裡
                current_chunk = [sentence]  # 全新的current_chunk加入這句
                current_length = len(sentence)  # 把這句的字數設為總長度
                i += 1
                continue

        else:  # 句子不是用#開頭 且字數沒有超過上限
            current_chunk.append(sentence)  # 把這句加入current_chunk
            current_length += len(sentence)  # 把這句的字數加入總長度
            i += 1  # 換下一句
    if current_chunk:  # 如果current_chunk不是空的
        chunks.append(" ".join(current_chunk))  # 保存跑完全部後的最後一個current_chunk
    return chunks