from src import file_handler
from src import model_client
from rapidfuzz import fuzz
import os
import shutil
import hashlib

LOGS_DIR = "logs"  # reading purposes
CACHES_DIR = "caches"  # to detect similar / same prompt
HISTORIES_DIR = "histories"  # for chat histories (WIP)
threshold = 90
match = None

def memorize_question(question):
    if question[0] == "$": question = question[1:]
    if question[0] == "@": question = question[1:]
    if file_handler.gemini_image:
        model_client.gemini_messages.append({"role": "user","parts": [{"text": question},{"inline_data": file_handler.gemini_image}]})
    else:
        model_client.gemini_messages.append({"role": "user", "parts": [{"text": question}]})
    if file_handler.command_image:
        model_client.command_messages.append({"role": "user", "content": [{"type": "text","text": question},{"type": "image_url","image_url": {"url": file_handler.command_image,"detail": "high"}}]})
    else:
        model_client.command_messages.append({"role": "user", "content": question})

def memorize_response():
    model_client.gemini_messages.append({"role": "model", "parts": [{"text": model_client.merged_response}]})
    model_client.command_messages.append({"role": "assistant", "content": model_client.merged_response})

def reset_logs():
    if os.path.exists(LOGS_DIR):
        shutil.rmtree(LOGS_DIR)
    os.makedirs(LOGS_DIR)
    with open("logs/gemini_log.md", "w", encoding="utf-8") as file:
        pass
    with open("logs/command_log.md", "w", encoding="utf-8") as file:
        pass
    with open("logs/merged_log.md", "w", encoding="utf-8") as file:
        pass

def log_interaction(question, gemini_response, command_response, merged_response):
    if question[0] == "$":  # Reasoning
        question = question[1:]
    if question[0] == "@":  # Reasoning
        question = question[1:]
    with open("logs/gemini_log.md", "a", encoding="utf-8") as file:
        file.write("User:\n\n" + question + "\n\n====================================================================================================\n\n" + "Model:\n\n" + gemini_response + "\n\n====================================================================================================\n\n")
    with open("logs/command_log.md", "a", encoding="utf-8") as file:
        file.write("User:\n\n" + question + "\n\n====================================================================================================\n\n" + "Model:\n\n" + command_response + "\n\n====================================================================================================\n\n")
    with open("logs/merged_log.md", "a", encoding="utf-8") as file:
        file.write("User:\n\n" + question + "\n\n====================================================================================================\n\n" + "Model:\n\n" + merged_response + "\n\n====================================================================================================\n\n")

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