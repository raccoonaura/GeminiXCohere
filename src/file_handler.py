from src import response_handler
from src import utils
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(BASE_DIR, "embeds", "note.txt")

def get_file():

    files = os.listdir("embeds")
    files = [f for f in files if not f.startswith('.') and os.path.isfile(os.path.join("embeds", f))]
    if not files:
        print(f"Error! There's no file in the embeds folder!")
        return None

    files = [f for f in files 
            if os.path.isfile(os.path.join("embeds", f)) 
            and any(f.endswith(ext) for ext in [".txt", ".md"])]
    """
    planned file types to support:

    General text files: txt, md, rtf
    General document files: pdf
    ODF text files: odt, ott
    ODF presentation files: odp, otp
    Word files: docx, dotx,
    Macro Word files: docm, dotm
    Legacy Word files: doc, dot
    PowerPoint files: pptx, ppsx, potx
    Macro PowerPoint files: pptm, potm, ppsm
    Legacy PowerPoint files: ppt, pps, pot
    Excel files: xlsx, xltx
    Macro Excel files: xlsm, xltm
    Legacy Excel files: xls, xlt
    Tabular data files: csv, tsv
    Structured data files: json, xml, yaml
    Web content files: html
    E-books files: epub

    probably will use tools like pandoc and libreoffice
    """
    if not files:
        print(f"Error! None of the files in the embeds folder are supported!")
        return None

    print("Available files:\n")
    for i, filename in enumerate(files, 1):
        print(f"└ {i}. {filename}")

    utils.set_marker()

    while True:
        try:
            choice = input(f"\nPlease select the desired file (1~{len(files)}): ").strip()
            choice = int(choice)
            
            if 1 <= choice <= len(files):
                selected = files[choice - 1]
                print(f"\nSelected: {selected}")
                return selected
            else:
                utils.clear_screen()
        
        except ValueError:
            utils.clear_screen()
            continue
        except KeyboardInterrupt:
            utils.clear_screen()
            continue

def load_text_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def chunk_by_sentence(max_length, overlap):  # 我決定把每一句留下中文註解 因為我自己都快亂了:P
    """ max_length: 用字數計算, overlap: 用句數計算,
        sentences: 切斷後的本文, 含全部的句子, sentence: 本文切段後的一個句子,
        current_chunk: 一個段落, 好幾個句子, chunks: 切段並重新安排後的好幾個段落,
        tail: 上一個段落的尾端幾句, """
    text = load_text_file("embeds/" + response_handler.fN)

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

"""  # doesn't work when the tail is longer than max_length
            if len(current_chunk) > overlap:  # 如果現在的current_chunk包含的句數比overlap所保留的句數還多的時候 (通常是這樣)
                tail = current_chunk[-overlap:]  # 從尾部取出overlap所保留的句數, 保留起來
            else:  # 如果現在的current_chunk包含的句數跟overlap所保留的句數一樣多或更少的時候
                tail = current_chunk  # 把整段current_chunk全部保留下來

            current_chunk = tail  # 全新的current_chunk加入overlap的部分
            current_length = sum(len(s) for s in current_chunk)  # 算字數
            # 不用換句 直接繼續check新的current_chunk就好
"""

"""  # doesn't work, i don't really remember why though
    for sentence in sentences:

        if len(current_chunk.strip()) + len(sentence) <= max_length and not sentence.lstrip().startswith("#"):
            current_chunk = add_current_line(current_chunk,sentence)

        else:
            if sentence.lstrip().startswith("#"):
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = sentence + "\n"

            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                tail = current_chunk[-overlap:]
                current_chunk = tail + sentence + "\n"

    if current_chunk:
        chunks.append(" ".join(current_chunk))
"""

"""  # not necessary anymore
from src import embedding_handler
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def retrieve_relevant_chunks(question, top_k):
    similarities = []
    for item in embedding_handler.vector_store:
        score = cosine_similarity(question, item["vector"])
        similarities.append((score, item["chunk"]))

    similarities.sort(reverse=True, key=lambda x: x[0])
    return similarities[:top_k]
"""