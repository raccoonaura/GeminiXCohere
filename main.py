from src import response_handler
from src import logging_handler
from src import caching_handler
from src import model_client
from src import utils

if __name__ == "__main__":
    logging_handler.reset_logs()
    caching_handler.reset_caches()

utils.clear_all()
model_client.initialize_gemini()
utils.clear_all()
model_client.initialize_cohere()
utils.clear_all()

question = input("Hello! How can I assist you today? ")
while question.strip() == "":
    utils.clear_all()
    question = input("Hello! How can I assist you today? ")

while True:
    response_handler.handle_conversation(question)
    question = input("Your turn: ")
    while question.strip() == "":
        utils.clear_screen()
        question = input("Your turn: ")