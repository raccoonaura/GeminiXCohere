import os
import shutil

LOGS_DIR = "logs"  # Logs are meant to be read by the user

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

def log_interaction(question, gRes, cRes, mRes):
    if question[0] == "$":  # Reasoning
        question = question[1:]
    if question[0] == "@":  # Reasoning
        question = question[1:]
    with open("logs/gemini_log.md", "a", encoding="utf-8") as file:
        file.write("User:\n\n" + question + "\n\n====================================================================================================\n\n" + "Model:\n\n" + gRes + "\n\n====================================================================================================\n\n")
    with open("logs/command_log.md", "a", encoding="utf-8") as file:
        file.write("User:\n\n" + question + "\n\n====================================================================================================\n\n" + "Model:\n\n" + cRes + "\n\n====================================================================================================\n\n")
    with open("logs/merged_log.md", "a", encoding="utf-8") as file:
        file.write("User:\n\n" + question + "\n\n====================================================================================================\n\n" + "Model:\n\n" + mRes + "\n\n====================================================================================================\n\n")