from src import file_handler
from src import model_client
from src import utils
from rapidfuzz import fuzz
import os
import shutil
import hashlib
import json
import datetime

LOGS_DIR = "logs"  # reading purposes
CACHES_DIR = "caches"  # to detect similar / same prompt
HISTORIES_DIR = "histories"  # for chat histories
threshold = 90
match = None
current_history = ""
gemini_histories = []
command_histories = []

def memorize_question(question):
    if question[0] == "$": question = question[1:]
    if question[0] == "@": question = question[1:]
    gemini_histories.append({"role": "user", "parts": [{"text": question}]})
    command_histories.append({"role": "user", "content": question})
    if file_handler.gemini_image:
        model_client.gemini_messages.append({"role": "user","parts": [{"text": question},{"inline_data": file_handler.gemini_image}]})
    else:
        model_client.gemini_messages.append({"role": "user", "parts": [{"text": question}]})
    if file_handler.command_image:
        model_client.command_messages.append({"role": "user", "content": [{"type": "text","text": question},{"type": "image_url","image_url": {"url": file_handler.command_image,"detail": "high"}}]})
    else:
        model_client.command_messages.append({"role": "user", "content": question})

def memorize_response():
    global current_history
    gemini_histories.append({"role": "model", "parts": [{"text": model_client.merged_response}]})
    command_histories.append({"role": "assistant", "content": model_client.merged_response})
    model_client.gemini_messages.append({"role": "model", "parts": [{"text": model_client.merged_response}]})
    model_client.command_messages.append({"role": "assistant", "content": model_client.merged_response})
    if not current_history:
        data = {'gemini': gemini_histories, 'command': command_histories}
        dt = datetime.datetime.now()
        now = dt.strftime('%Y-%m-%d-%H-%M-%S')
        current_history = f'{now}.json'
        with open("histories/" + current_history, 'w', encoding="utf8") as f: json.dump(data, f, ensure_ascii=False)
    else:
        data = {'gemini': model_client.gemini_messages, 'command': model_client.command_messages}
        with open("histories/" + current_history, 'w', encoding="utf8") as f: json.dump(data, f, ensure_ascii=False)

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

def choose_history():
    global current_history
    if os.path.exists(HISTORIES_DIR): pass
    else: os.makedirs(HISTORIES_DIR)
    filename = "(Not selected)"
    utils.set_marker()
    new_chat_number = len(os.listdir(HISTORIES_DIR)) + 1
    if new_chat_number == 1:
        utils.clear_screen()
        return
    while True:
        try:
            print("Choose a chat history:\n")
            for i, file in enumerate(os.listdir(HISTORIES_DIR), 1):
                print(f"└ {i}. {file}")
            print(f"└ {new_chat_number}. *Create a new chat*")
            print(f'Selected: {filename}\n(Type "done" to finish selecting.)')
            choice = input(f'\nSelect the desired chat history (1~{new_chat_number}): ').strip()
            if choice == "":
                utils.clear_screen()
                continue
            if choice == "done":
                if filename == "(Not selected)": continue
                utils.clear_screen()
                current_history = filename
                with open("histories/" + filename, 'r', encoding="utf8") as f:
                    data = json.load(f)
                    model_client.gemini_messages = data['gemini']
                    model_client.command_messages = data['command']
                    return
            choice = int(choice)
            if 1 <= choice <= new_chat_number:
                if choice == new_chat_number:
                    utils.clear_screen()
                    return
                else:
                    filename = os.listdir(HISTORIES_DIR)[choice - 1]
                utils.clear_screen()
            else:
                utils.clear_screen()
        except Exception as e:
            utils.clear_screen()
            print(e)
            continue