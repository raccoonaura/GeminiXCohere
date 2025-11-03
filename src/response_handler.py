from src import logging_handler
from src import caching_handler
from src import file_handler
from src import model_client
from src import utils
import threading
import time
thought_start = None
image = ""
document = ""
context = ""

def get_response(question):
    global context
    if question[0] == "$":
        if image: file_handler.check_for_image(image)
        if document:
            context = model_client.embedding(question)
            if context == "error!":
                return
            if question[1] == "@":  # Enable reasoning
                print ("Enabled reasoning! Please wait...\n\n-------------------------\n")
            else:
                print ("\n-------------------------\n")
    else:
        context = ""
    model_client.memorize_question(question)
    generate_response(question)
    if not file_handler.skip_gemini and not file_handler.skip_command:
        response = model_client.merged_response
        print (f"You: {question}\n\n-------------------------\n\n{model_client.merged_response}\n\n-------------------------\n\nThought for {model_client.gemini_merge_end_thinking} seconds in total, took {model_client.gemini_end_merging} seconds to merge the answers, generated {len(model_client.merged_response)} tokens.\nUsed model {model_client.gemini_model} and {model_client.command_model}, merged using {model_client.gemini_merge_model}.\n\n-------------------------\n")
        logging_handler.log_interaction(question, model_client.gemini_response, model_client.command_response, model_client.merged_response)
    elif file_handler.skip_command:
        response = model_client.gemini_response
        logging_handler.log_interaction(question, model_client.gemini_response, "(Skipped. Unsupported image type for this model.)", model_client.gemini_response)
    else:
        response = model_client.command_response
        logging_handler.log_interaction(question, "(Skipped. Unsupported image type for this model.)", model_client.command_response, model_client.command_response)
    caching_handler.write_to_caches(question, response)
    model_client.memorize_response()

def generate_response(question):
    global thought_start
    t1 = threading.Thread(target=model_client.ask_gemini, args=(question,))
    t2 = threading.Thread(target=model_client.ask_command, args=(question,))
    if not file_handler.skip_gemini:
        t1.start()
    if not file_handler.skip_command:
        t2.start()
    thought_start = time.perf_counter()
    if not file_handler.skip_gemini:
        t1.join()
    if not file_handler.skip_command:
        t2.join()
    if not file_handler.skip_gemini and not file_handler.skip_command:
        print(f"Gemini thought for {model_client.gemini_end_thinking} seconds, took {model_client.gemini_end_generating} seconds to generate the answer, generated {len(model_client.gemini_response)} tokens, using model {model_client.gemini_model}.\nCommand thought for {model_client.command_end_thinking} seconds, took {model_client.command_end_generating} seconds to generate the answer, generated {len(model_client.command_response)} tokens, using model {model_client.command_model}.\n\n-------------------------\n\nGenerating full response...")
    if not file_handler.skip_gemini and file_handler.skip_command:
        print(f"Gemini thought for {model_client.gemini_end_thinking} seconds, took {model_client.gemini_end_generating} seconds to generate the answer, generated {len(model_client.gemini_response)} tokens, using model {model_client.gemini_model}.\n\n-------------------------\n")
    if file_handler.skip_gemini and not file_handler.skip_command:
        print(f"Command thought for {model_client.command_end_thinking} seconds, took {model_client.command_end_generating} seconds to generate the answer, generated {len(model_client.command_response)} tokens, using model {model_client.command_model}.\n\n-------------------------\n")
    # exit() # to test if the program works before merging
    if not file_handler.skip_gemini and not file_handler.skip_command:
        t3 = threading.Thread(target=model_client.merge_responses, args=(question,))
        t3.start()
        t3.join()

def handle_conversation(question):
    global image, document
    try:
        utils.clear_all()
        print (f"You: {question}\n\n-------------------------\n")
        cached = caching_handler.read_from_caches(question)
        if cached:
            print (cached, "\n\n-------------------------\n\nDetected similar question in cache (match: {:.1f}%)\n\n-------------------------\n".format(caching_handler.match))
            return cached
        else:
            if question[0] == "$":  # Enable file reading
                utils.set_marker()
                image, document = file_handler.get_file()
            if question[0] == "@":  # Enable reasoning
                print ("Enabled reasoning! Please wait...\n\n-------------------------\n")
            get_response(question)
        utils.set_marker()

    except Exception as e:
        print("API Key invalid / An error occurred: ", e)