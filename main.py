from src import response_handler
from src import document_handler
from src import memory_handler
from src import model_client
from src import utils

question = ""

if __name__ == "__main__":
    memory_handler.reset_logs()
    memory_handler.reset_caches()
    document_handler.reset_temp()
model_client.initialize_gemini()
model_client.initialize_cohere()
utils.clear_all()

memory_handler.choose_history()

while question.strip() == "":
    utils.clear_all()
    try: question = input("Hello! How can I assist you today? ")
    except: continue

while True:
    response_handler.handle_conversation(question)
    question = ""
    utils.set_marker()
    while question.strip() == "":
        utils.clear_screen()
        try: question = input("Your turn: ")
        except: continue