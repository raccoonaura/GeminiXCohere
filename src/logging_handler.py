import os
import shutil

LOGS_DIR = "logs"  # Logs are meant to be read by the user

def reset_logs():
    if os.path.exists(LOGS_DIR):
        shutil.rmtree(LOGS_DIR)
    os.makedirs(LOGS_DIR)
    with open("logs/gemini_log.txt", "w", encoding="utf-8") as file:
        pass
    with open("logs/command.txt", "w", encoding="utf-8") as file:
        pass
    with open("logs/merged_log.txt", "w", encoding="utf-8") as file:
        pass

def log_interaction(question, gRes, cRes, mRes):
    with open("logs/gemini_log.txt", "a", encoding="utf-8") as file:
        file.write("User:" + question + "\n\n" + "Model:" + gRes + "\n\n")
    with open("logs/command.txt", "a", encoding="utf-8") as file:
        file.write("User:" + question + "\n\n" + "Model:" + cRes + "\n\n")
    with open("logs/merged_log.txt", "a", encoding="utf-8") as file:
        file.write("User:" + question + "\n\n" + "Model:" + mRes + "\n\n")