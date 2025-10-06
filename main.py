from src import response_handler
from src import logging_handler
from src import utils

logging_handler.create_log_files()

utils.clear_all()
response_handler.initialize_gemini()
utils.clear_all()
response_handler.initialize_cohere()
utils.clear_all()

question = input("Hello! How can I assist you today? ")
while question.strip() == "":
    utils.clear_all()
    question = input("Hello! How can I assist you today? ")

while True:  # There could be a better way to do this, but this works for now
    response_handler.handle_conversation(question)
    question = input("Your turn: ")  # This is (basically) required for updating the question
    while question.strip() == "":
        utils.clear_screen()
        question = input("Your turn: ")