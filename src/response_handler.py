from src import spreadsheet_handler
from src import embedding_handler
from src import document_handler
from src import memory_handler
from src import file_handler
from src import model_client
from src import utils
import threading
import time
thought_start = None
image = []
document = []
spreadsheet = []
context = ""

def handle_conversation(question):
    try:
        utils.clear_all()
        print (f"You: {question}\n\n-------------------------\n")
        model_client.embed_model = ""
        model_client.rerank_model = ""
        cached = memory_handler.read_from_caches(question)
        if cached:
            print (cached, "\n\n-------------------------\n\nDetected similar question in cache (match: {:.1f}%)\n\n-------------------------\n".format(memory_handler.match))
            return cached
        else:
            if question[0] == "$":  # Enable file reading
                utils.set_marker()
                file_handler.get_file()
            if question[0] == "@":  # Enable reasoning
                print ("Enabled reasoning! Please wait...\n\n-------------------------\n")
            get_response(question)
        utils.set_marker()

    except Exception as e:
        print(f'API Key invalid / An error occurred: {e}')

def get_response(question):
    global context
    if question[0] == "$":
        if image: file_handler.handle_image(image)
        context = ""
        if spreadsheet:
            context = spreadsheet_handler.handle_spreadsheets(spreadsheet)
            if context == "error!": return
        if document:
            pre_context = embedding_handler.embedding(question, document_handler.handle_document(document))
            if pre_context == "error!": return
            if spreadsheet: context += pre_context
            else: context = pre_context
            if question[1] == "@":  # Enable reasoning
                print ("Enabled reasoning! Please wait...\n\n-------------------------\n")
            else:
                print ("\n-------------------------\n")
    else:
        context = ""
    memory_handler.memorize_question(question)
    generate_response(question)
    if not file_handler.skip_gemini and not file_handler.skip_command:
        response = model_client.merged_response
        utils.clear_all()  # clears the warning about thought signature, since google did NOT explain in their docs how am i supposed to receive and resent it
        if model_client.embed_model and model_client.rerank_model:
            print (f"You: {question}\n\n-------------------------\n\n{model_client.merged_response}\n\n-------------------------\n\nThought for {model_client.gemini_merge_end_thinking} seconds in total, took {model_client.gemini_end_merging} seconds to merge the answers, generated {len(model_client.merged_response)} tokens.\nEmbedded using {model_client.embed_model}, reranked using {model_client.rerank_model}.\nGenerated response using model {model_client.gemini_model} and {model_client.command_model}, merged using {model_client.gemini_merge_model}.\n\n-------------------------\n")
        elif model_client.embed_model:
            print (f"You: {question}\n\n-------------------------\n\n{model_client.merged_response}\n\n-------------------------\n\nThought for {model_client.gemini_merge_end_thinking} seconds in total, took {model_client.gemini_end_merging} seconds to merge the answers, generated {len(model_client.merged_response)} tokens.\nEmbedded using {model_client.embed_model}.\nGenerated response using model {model_client.gemini_model} and {model_client.command_model}, merged using {model_client.gemini_merge_model}.\n\n-------------------------\n")
        else:
            print (f"You: {question}\n\n-------------------------\n\n{model_client.merged_response}\n\n-------------------------\n\nThought for {model_client.gemini_merge_end_thinking} seconds in total, took {model_client.gemini_end_merging} seconds to merge the answers, generated {len(model_client.merged_response)} tokens.\nGenerated response using model {model_client.gemini_model} and {model_client.command_model}, merged using {model_client.gemini_merge_model}.\n\n-------------------------\n")
        memory_handler.log_interaction(question, model_client.gemini_response, model_client.command_response, model_client.merged_response)
    elif file_handler.skip_command:
        response = model_client.gemini_response
        memory_handler.log_interaction(question, model_client.gemini_response, "(Skipped. Unsupported image type for this model.)", model_client.gemini_response)
    else:
        response = model_client.command_response
        memory_handler.log_interaction(question, "(Skipped. Unsupported image type for this model.)", model_client.command_response, model_client.command_response)
    memory_handler.write_to_caches(question, response)
    memory_handler.memorize_response()

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
        if model_client.embed_model and model_client.rerank_model:
            print(f"Gemini thought for {model_client.gemini_end_thinking} seconds, took {model_client.gemini_end_generating} seconds to generate the answer, generated {len(model_client.gemini_response)} tokens, using model {model_client.gemini_model}.\nCommand thought for {model_client.command_end_thinking} seconds, took {model_client.command_end_generating} seconds to generate the answer, generated {len(model_client.command_response)} tokens, using model {model_client.command_model}.\nEmbedded using {model_client.embed_model}, reranked using {model_client.rerank_model}.\n\n-------------------------\n\nGenerating full response...")
        elif model_client.embed_model:
            print(f"Gemini thought for {model_client.gemini_end_thinking} seconds, took {model_client.gemini_end_generating} seconds to generate the answer, generated {len(model_client.gemini_response)} tokens, using model {model_client.gemini_model}.\nCommand thought for {model_client.command_end_thinking} seconds, took {model_client.command_end_generating} seconds to generate the answer, generated {len(model_client.command_response)} tokens, using model {model_client.command_model}.\nEmbedded using {model_client.embed_model}.\n\n-------------------------\n\nGenerating full response...")
        else:
            print(f"Gemini thought for {model_client.gemini_end_thinking} seconds, took {model_client.gemini_end_generating} seconds to generate the answer, generated {len(model_client.gemini_response)} tokens, using model {model_client.gemini_model}.\nCommand thought for {model_client.command_end_thinking} seconds, took {model_client.command_end_generating} seconds to generate the answer, generated {len(model_client.command_response)} tokens, using model {model_client.command_model}.\n\n-------------------------\n\nGenerating full response...")
    if not file_handler.skip_gemini and file_handler.skip_command:
        if model_client.embed_model and model_client.rerank_model:
            print(f"Gemini thought for {model_client.gemini_end_thinking} seconds, took {model_client.gemini_end_generating} seconds to generate the answer, generated {len(model_client.gemini_response)} tokens.\nEmbedded using {model_client.embed_model}, reranked using {model_client.rerank_model}, generated response using model {model_client.gemini_model}.\n\n-------------------------\n")
        elif model_client.embed_model:
            print(f"Gemini thought for {model_client.gemini_end_thinking} seconds, took {model_client.gemini_end_generating} seconds to generate the answer, generated {len(model_client.gemini_response)} tokens.\nEmbedded using {model_client.embed_model}, generated response using model {model_client.gemini_model}.\n\n-------------------------\n")
        else:
            print(f"Gemini thought for {model_client.gemini_end_thinking} seconds, took {model_client.gemini_end_generating} seconds to generate the answer, generated {len(model_client.gemini_response)} tokens, using model {model_client.gemini_model}.\n\n-------------------------\n")
    if file_handler.skip_gemini and not file_handler.skip_command:
        if model_client.embed_model and model_client.rerank_model:
            print(f"Command thought for {model_client.command_end_thinking} seconds, took {model_client.command_end_generating} seconds to generate the answer, generated {len(model_client.command_response)} tokens.\nEmbedded using {model_client.embed_model}, reranked using {model_client.rerank_model}, generated response using model {model_client.command_model}.\n\n-------------------------\n")
        elif model_client.embed_model:
            print(f"Command thought for {model_client.command_end_thinking} seconds, took {model_client.command_end_generating} seconds to generate the answer, generated {len(model_client.command_response)} tokens.\nEmbedded using {model_client.embed_model}, generated response using model {model_client.command_model}.\n\n-------------------------\n")
        else:
            print(f"Command thought for {model_client.command_end_thinking} seconds, took {model_client.command_end_generating} seconds to generate the answer, generated {len(model_client.command_response)} tokens, using model {model_client.command_model}.\n\n-------------------------\n")
    if file_handler.skip_gemini and file_handler.skip_command: print(f"The image types you provided are partially unsupported by each model!\n\n-------------------------\n")
    if not file_handler.skip_gemini and not file_handler.skip_command:
        t3 = threading.Thread(target=model_client.merge_responses, args=(question,))
        t3.start()
        t3.join()