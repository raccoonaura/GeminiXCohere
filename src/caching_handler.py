from rapidfuzz import fuzz
import os
import shutil
import hashlib

CACHES_DIR = "caches"  # Caches are meant to be read by the program
threshold = 90
match = None

def reset_caches():
    if os.path.exists(CACHES_DIR):
        shutil.rmtree(CACHES_DIR)
    os.makedirs(CACHES_DIR)

def get_caches_path(question: str) -> str:
    file_hash = hashlib.md5(question.encode('utf-8')).hexdigest()
    return os.path.join(CACHES_DIR, f"{file_hash}.txt")

def read_from_caches(question: str) -> str | None:
    global match
    if not os.path.exists(CACHES_DIR):
        return None
    for filename in os.listdir(CACHES_DIR):
        file_path = os.path.join(CACHES_DIR, filename)
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if not lines:
                    continue
                cached_question = lines[0].strip()
                if fuzz.ratio(question, cached_question) >= threshold:
                    match = fuzz.ratio(question, cached_question)
                    # 回傳除了第一行以外的內容
                    return "".join(lines[1:])
    return None

def write_to_caches(question: str, response: str):
    path = get_caches_path(question)
    with open(path, "w", encoding="utf-8") as f:
        f.write(question + "\n")
        f.write(response)