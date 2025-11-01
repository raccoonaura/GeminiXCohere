from src import response_handler
from src import logging_handler
from src import caching_handler
from src import model_client
from src import utils

question = ""

if __name__ == "__main__":
    logging_handler.reset_logs()
    caching_handler.reset_caches()

model_client.initialize_gemini()
model_client.initialize_cohere()

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