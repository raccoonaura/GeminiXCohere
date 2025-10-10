import threading
from src import logging_handler
from src import caching_handler
from src import model_client
from src import utils
import time
tS = None  # Stands for thought start

def get_response(question):
    cached = caching_handler.read_from_caches(question)
    if cached:
        utils.clear_all()
        print ("You: ", question, "\n\n----------\n\n", cached, "\n\n----------\n\nDetected similar question in cache (match: {:.1f}%)\n\n----------\n".format(caching_handler.match))
        return cached
    generate_response(question)
    response = model_client.mRes
    utils.clear_all()
    print ("You: ", question, "\n\n----------\n\n", model_client.mRes, "\n\n----------\n\nThought for", model_client.mET, "seconds in total, took", model_client.mEG, "seconds to merge the answers, generated", len(model_client.mRes), "tokens.\n\n----------\n")
    caching_handler.write_to_caches(question, response)
    return response

def generate_response(question):
    global tS
    t1 = threading.Thread(target=model_client.ask_gemini, args=(question,))
    t2 = threading.Thread(target=model_client.ask_command, args=(question,))
    t1.start()
    t2.start()
    tS = time.perf_counter()
    t1.join()
    t2.join()
    t3 = threading.Thread(target=model_client.merge_responses, args=(question,))
    t3.start()
    print("Gemini thought for", model_client.gET, "seconds, took", model_client.gEG, "seconds to generate the answer, generated", len(model_client.gRes), "tokens.\nCommand thought for", model_client.cET, "seconds, took", model_client.cEG, "seconds to generate the answer, generated", len(model_client.cRes), "tokens.\n\n----------\n\nGenerating full response...")
    t3.join()

def handle_conversation(question):
    try:
        utils.clear_all()
        print ("You: ", question, "\n\n----------\n")

        model_client.memorize_question(question)
        if (question[0] == "@"):
            print ("Enabled reasoning! Please wait...\n\n----------\n")
        get_response(question)

        logging_handler.log_interaction(question, model_client.gRes, model_client.cRes, model_client.mRes)

        model_client.memorize_response()

        utils.set_marker()

    except Exception as e:
        print("API Key無效或發生錯誤: ", e)