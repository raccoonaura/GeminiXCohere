def create_log_files():
    with open("gemini_log.txt", "w", encoding="utf-8") as file:
        pass
    with open("cohere_log.txt", "w", encoding="utf-8") as file:
        pass
    with open("merged_log.txt", "w", encoding="utf-8") as file:
        pass

def log_interaction(question, gRes, cRes, mRes):
    with open("gemini_log.txt", "a", encoding="utf-8") as file:
        file.write("User:" + question + "\n\n" + "Model:" + gRes + "\n\n")
    with open("cohere_log.txt", "a", encoding="utf-8") as file:
        file.write("User:" + question + "\n\n" + "Model:" + cRes + "\n\n")
    with open("merged_log.txt", "a", encoding="utf-8") as file:
        file.write("User:" + question + "\n\n" + "Model:" + mRes + "\n\n")