import threading
from src import logging_handler
from src import model_client
from src import utils

def generate_response(question):
    '''
    t1 = threading.Thread(target=model_client.ask_gemini, args=(question,))
    t2 = threading.Thread(target=model_client.ask_cohere, args=(question,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    '''

    # Add this and quotes around the below lines to make both models think at the same time for faster generations,
    # but you gotta disable one of their real-time printing

    # '''
    t1 = threading.Thread(target=model_client.ask_gemini, args=(question,))
    t1.start()
    t1.join()
    t2 = threading.Thread(target=model_client.ask_cohere, args=(question,))
    t2.start()
    t2.join()
    # '''
    t3 = threading.Thread(target=model_client.merge_responses, args=(question,))
    t3.start()
    t3.join()

def handle_conversation(question):
    try:
        utils.clear_all()
        print ("You: ", question, "\n\n----------\n")

        model_client.memorize_question(question)
        if (question[0] == "@"):
            print ("Enabled reasoning! Please wait...\n\n----------\n")
        generate_response(question)

        # print("\n----------\n\nGemini:\n\n", gRes, "\n\n----------\n\nCohere:\n\n", cRes, "\n\n----------\n\nMerged:\n\n", mRes, "\n\n----------\n")
        utils.clear_all()
        print ("You: ", question, "\n\n----------\n\n", model_client.mRes, "\n\n----------\n")

        logging_handler.log_interaction(question, model_client.gRes, model_client.cRes, model_client.mRes)

        model_client.memorize_response()

        utils.set_marker()

    except Exception as e:
        print("API Key無效或發生錯誤: ", e)