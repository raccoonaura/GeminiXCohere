from src.cli import spreadsheet_handler
from src.cli import embedding_handler
from src.cli import document_handler
from src.cli import memory_handler
from src.cli import file_handler
from src.cli import model_client
from src.cli import utils
import threading
import time
thought_start = None
image = []
document = []
spreadsheet = []
context = ""
previously_cached = False
previous_question = ""

def handle_conversation(question):
    global image, document, spreadsheet, context, thought_start, previously_cached, previous_question
    try:
        image = []
        document = []
        spreadsheet = []
        context = ""
        file_handler.skip_gemini = False
        file_handler.skip_mistral_n_command = False
        model_client.embed_model = ""
        model_client.rerank_model = ""
        utils.clear_all()
        print (f"You: {question}\n\n-------------------------\n")
        cached = memory_handler.read_from_caches(question)
        if cached and not previously_cached:
            previously_cached = True
            previous_question = question
            print (cached, '\n\n-------------------------\n\nDetected similar question in cache (match: {:.1f}%)\nType "resend" to resend the question\n\n-------------------------\n'.format(memory_handler.match))
            return cached
        elif previously_cached and question.strip() == "resend":
            question = previous_question
            previous_question = ""
            utils.clear_all()
            print (f"You: {question}\n\n-------------------------\n")
        previously_cached = False
        if question[0] == "@":
            print ("Enabled reasoning! Please wait...\n\n-------------------------\n")
        if question[0] == "$":
            utils.set_marker()
            if file_handler.get_file():
                pass
            else:
                return
            if image:
                error_check = file_handler.handle_image(image)
                if error_check == "error!":
                    return
                if question[1] == "@":
                    print ("Enabled reasoning! Please wait...\n\n-------------------------\n")
            if spreadsheet:
                context = spreadsheet_handler.handle_spreadsheets(spreadsheet)
                if context == "error!":
                    return
                if question[1] == "@":
                    print ("Enabled reasoning! Please wait...\n\n-------------------------\n")
            if document:
                pre_context = embedding_handler.embedding(question, document_handler.handle_document(document))
                if pre_context == "error!":
                    return
                if spreadsheet:
                    context += pre_context
                else:
                    context = pre_context
                if question[1] == "@":
                    print ("Enabled reasoning! Please wait...\n\n-------------------------\n")
                else:
                    print ("\n-------------------------\n")
        memory_handler.memorize_question(question)
        choose_gemini_model = threading.Thread(target=model_client.choose_gemini_model, args=(question,))
        choose_mistral_model = threading.Thread(target=model_client.choose_mistral_model, args=(question,))
        choose_command_model = threading.Thread(target=model_client.choose_command_model, args=(question,))
        thought_start = time.perf_counter()

        if not file_handler.skip_gemini:
            choose_gemini_model.start()
        if not file_handler.skip_mistral_n_command:
            choose_mistral_model.start()
            choose_command_model.start()
        
        if not file_handler.skip_gemini:
            choose_gemini_model.join()
        if not file_handler.skip_mistral_n_command:
            choose_mistral_model.join()
            choose_command_model.join()

        if not file_handler.skip_gemini and file_handler.skip_mistral_n_command:  # Gemini working here
            if model_client.embed_model and model_client.rerank_model:
                print(f"Gemini thought for {model_client.gemini_end_thinking} seconds, took {model_client.gemini_end_generating} seconds to generate the answer, generated {len(model_client.gemini_response)} characters.\nEmbedded using {model_client.embed_model}, reranked using {model_client.rerank_model}, generated response using model {model_client.gemini_model}.\n\n-------------------------\n")
            elif model_client.embed_model:
                print(f"Gemini thought for {model_client.gemini_end_thinking} seconds, took {model_client.gemini_end_generating} seconds to generate the answer, generated {len(model_client.gemini_response)} characters.\nEmbedded using {model_client.embed_model}, generated response using model {model_client.gemini_model}.\n\n-------------------------\n")
            else:
                print(f"Gemini thought for {model_client.gemini_end_thinking} seconds, took {model_client.gemini_end_generating} seconds to generate the answer, generated {len(model_client.gemini_response)} characters, using model {model_client.gemini_model}.\n\n-------------------------\n")
            response = model_client.gemini_response
            memory_handler.log_interaction(question, model_client.gemini_response, "(Skipped.)", "(Skipped.)", model_client.gemini_response)

        if file_handler.skip_gemini and not file_handler.skip_mistral_n_command:  # Mistral and Command working here
            if model_client.embed_model and model_client.rerank_model:
                print(f"Mistral thought for {model_client.mistral_end_thinking} seconds, took {model_client.mistral_end_generating} seconds to generate the answer, generated {len(model_client.mistral_response)} characters.\nCommand thought for {model_client.command_end_thinking} seconds, took {model_client.command_end_generating} seconds to generate the answer, generated {len(model_client.command_response)} characters.\nEmbedded using {model_client.embed_model}, reranked using {model_client.rerank_model}, generated response using model {model_client.mistral_model} and {model_client.command_model}.\n\n-------------------------\n\nGenerating full response...")
            elif model_client.embed_model:
                print(f"Mistral thought for {model_client.mistral_end_thinking} seconds, took {model_client.mistral_end_generating} seconds to generate the answer, generated {len(model_client.mistral_response)} characters.\nCommand thought for {model_client.command_end_thinking} seconds, took {model_client.command_end_generating} seconds to generate the answer, generated {len(model_client.command_response)} characters.\nEmbedded using {model_client.embed_model}, generated response using model {model_client.mistral_model} and {model_client.command_model}.\n\n-------------------------\n\nGenerating full response...")
            else:
                print(f"Mistral thought for {model_client.mistral_end_thinking} seconds, took {model_client.mistral_end_generating} seconds to generate the answer, generated {len(model_client.mistral_response)} characters.\nCommand thought for {model_client.command_end_thinking} seconds, took {model_client.command_end_generating} seconds to generate the answer, generated {len(model_client.command_response)} characters.\nUsing model {model_client.mistral_model} and {model_client.command_model}.\n\n-------------------------\n\nGenerating full response...")
            model_client.choose_merge_model(question)
            response = model_client.merged_response
            if model_client.embed_model and model_client.rerank_model:
                print (f"You: {question}\n\n-------------------------\n\n{model_client.merged_response}\n\n-------------------------\n\nThought for {model_client.gemini_merge_end_thinking} seconds in total, took {model_client.gemini_end_merging} seconds to merge the answers, generated {len(model_client.merged_response)} characters.\nEmbedded using {model_client.embed_model}, reranked using {model_client.rerank_model}.\nGenerated response using model {model_client.mistral_model} and {model_client.command_model}, merged using {model_client.gemini_merge_model}.\n\n-------------------------\n")
            elif model_client.embed_model:
                print (f"You: {question}\n\n-------------------------\n\n{model_client.merged_response}\n\n-------------------------\n\nThought for {model_client.gemini_merge_end_thinking} seconds in total, took {model_client.gemini_end_merging} seconds to merge the answers, generated {len(model_client.merged_response)} characters.\nEmbedded using {model_client.embed_model}.\nGenerated response using model {model_client.mistral_model} and {model_client.command_model}, merged using {model_client.gemini_merge_model}.\n\n-------------------------\n")
            else:
                print (f"You: {question}\n\n-------------------------\n\n{model_client.merged_response}\n\n-------------------------\n\nThought for {model_client.gemini_merge_end_thinking} seconds in total, took {model_client.gemini_end_merging} seconds to merge the answers, generated {len(model_client.merged_response)} characters.\nGenerated response using model {model_client.mistral_model} and {model_client.command_model}, merged using {model_client.gemini_merge_model}.\n\n-------------------------\n")
            memory_handler.log_interaction(question, "(Skipped.)", model_client.mistral_response, model_client.command_response, model_client.merged_response)

        if not file_handler.skip_gemini and not file_handler.skip_mistral_n_command:  # handling regularly
            if model_client.embed_model and model_client.rerank_model:
                print(f"Gemini thought for {model_client.gemini_end_thinking} seconds, took {model_client.gemini_end_generating} seconds to generate the answer, generated {len(model_client.gemini_response)} characters, using model {model_client.gemini_model}.\nMistral thought for {model_client.mistral_end_thinking} seconds, took {model_client.mistral_end_generating} seconds to generate the answer, generated {len(model_client.mistral_response)} characters, using model {model_client.mistral_model}.\nCommand thought for {model_client.command_end_thinking} seconds, took {model_client.command_end_generating} seconds to generate the answer, generated {len(model_client.command_response)} characters, using model {model_client.command_model}.\nEmbedded using {model_client.embed_model}, reranked using {model_client.rerank_model}.\n\n-------------------------\n\nGenerating full response...")
            elif model_client.embed_model:
                print(f"Gemini thought for {model_client.gemini_end_thinking} seconds, took {model_client.gemini_end_generating} seconds to generate the answer, generated {len(model_client.gemini_response)} characters, using model {model_client.gemini_model}.\nMistral thought for {model_client.mistral_end_thinking} seconds, took {model_client.mistral_end_generating} seconds to generate the answer, generated {len(model_client.mistral_response)} characters, using model {model_client.mistral_model}.\nCommand thought for {model_client.command_end_thinking} seconds, took {model_client.command_end_generating} seconds to generate the answer, generated {len(model_client.command_response)} characters, using model {model_client.command_model}.\nEmbedded using {model_client.embed_model}.\n\n-------------------------\n\nGenerating full response...")
            else:
                print(f"Gemini thought for {model_client.gemini_end_thinking} seconds, took {model_client.gemini_end_generating} seconds to generate the answer, generated {len(model_client.gemini_response)} characters, using model {model_client.gemini_model}.\nMistral thought for {model_client.mistral_end_thinking} seconds, took {model_client.mistral_end_generating} seconds to generate the answer, generated {len(model_client.mistral_response)} characters, using model {model_client.mistral_model}.\nCommand thought for {model_client.command_end_thinking} seconds, took {model_client.command_end_generating} seconds to generate the answer, generated {len(model_client.command_response)} characters, using model {model_client.command_model}.\n\n-------------------------\n\nGenerating full response...")
            model_client.choose_merge_model(question)
            response = model_client.merged_response
            if model_client.embed_model and model_client.rerank_model:
                print (f"You: {question}\n\n-------------------------\n\n{model_client.merged_response}\n\n-------------------------\n\nThought for {model_client.gemini_merge_end_thinking} seconds in total, took {model_client.gemini_end_merging} seconds to merge the answers, generated {len(model_client.merged_response)} characters.\nEmbedded using {model_client.embed_model}, reranked using {model_client.rerank_model}.\nGenerated response using model {model_client.gemini_model}, {model_client.mistral_model}, and {model_client.command_model}, merged using {model_client.gemini_merge_model}.\n\n-------------------------\n")
            elif model_client.embed_model:
                print (f"You: {question}\n\n-------------------------\n\n{model_client.merged_response}\n\n-------------------------\n\nThought for {model_client.gemini_merge_end_thinking} seconds in total, took {model_client.gemini_end_merging} seconds to merge the answers, generated {len(model_client.merged_response)} characters.\nEmbedded using {model_client.embed_model}.\nGenerated response using model {model_client.gemini_model}, {model_client.mistral_model}, and {model_client.command_model}, merged using {model_client.gemini_merge_model}.\n\n-------------------------\n")
            else:
                print (f"You: {question}\n\n-------------------------\n\n{model_client.merged_response}\n\n-------------------------\n\nThought for {model_client.gemini_merge_end_thinking} seconds in total, took {model_client.gemini_end_merging} seconds to merge the answers, generated {len(model_client.merged_response)} characters.\nGenerated response using model {model_client.gemini_model}, {model_client.mistral_model}, and {model_client.command_model}, merged using {model_client.gemini_merge_model}.\n\n-------------------------\n")
            memory_handler.log_interaction(question, model_client.gemini_response, model_client.mistral_response, model_client.command_response, model_client.merged_response)

        memory_handler.write_to_caches(question, response)
        memory_handler.memorize_response()

    except Exception as e:
        print(f'API Key invalid / An error occurred: {e}')
        memory_handler.log_errors(e)