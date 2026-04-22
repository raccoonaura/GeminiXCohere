from src.app import memory_handler
from src.app import model_client
from concurrent.futures import ThreadPoolExecutor
import gradio as gr
import threading
import time

def handle_conversation(question, reasoning, gemini_state, cohere_state):
    yield (gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gemini_state, gr.update(), cohere_state, gr.update())
    try:
        # state["image"] = []
        # state["document"] = []
        # state["spreadsheet"] = []
        # state["context"] = ""
        # file_handler.skip_gemini = False
        # file_handler.skip_mistral_n_command = False
        # utils.clear_all()
        # print (f"You: {question}\n\n-------------------------\n")
        # state["embed_model"] = ""
        # state["rerank_model"] = ""
        # if question[0] == "@": print ("Enabled reasoning! Please wait...\n\n-------------------------\n")
        # if question[0] == "$":
        #     #utils.set_marker()
        #     if file_handler.get_file(): pass
        #     else: return
        #     if state["image"]:
        #         file_handler.handle_image(state["image"])
        #         if question[1] == "@": print ("Enabled reasoning! Please wait...\n\n-------------------------\n")
        #     if state["spreadsheet"]:
        #         state["context"] = spreadsheet_handler.handle_spreadsheets(state["spreadsheet"])
        #         if state["context"] == "error!": return
        #         if question[1] == "@": print ("Enabled reasoning! Please wait...\n\n-------------------------\n")
        #     if state["document"]:
        #         pre_context = embedding_handler.embedding(question, document_handler.handle_document(state["document"]))
        #         if pre_context == "error!": return
        #         if state["spreadsheet"]: state["context"] += pre_context
        #         else: state["context"] = pre_context
        #         if question[1] == "@": print ("Enabled reasoning! Please wait...\n\n-------------------------\n")
        #         else: print ("\n-------------------------\n")
        gemini_state, cohere_state = memory_handler.memorize_question(question, gemini_state, cohere_state)
        yield from model_client.choose_gemini_model(reasoning, gemini_state)
        yield from model_client.choose_command_model(reasoning, cohere_state)

        # t1 = threading.Thread(target=model_client.choose_gemini_model, args=(reasoning, gemini_state))
        # t2 = threading.Thread(target=model_client.choose_command_model, args=(reasoning, cohere_state))
        # t1.start()
        # t2.start()
        # gemini_state["thought_start"] = time.perf_counter()
        # cohere_state["thought_start"] = time.perf_counter()
        # t1.join()
        # t2.join()
        # with ThreadPoolExecutor(max_workers=2) as executor:
        #     choose_gemini_model = executor.submit(model_client.choose_gemini_model, reasoning, gemini_state)
        #     choose_command_model = executor.submit(model_client.choose_command_model, reasoning, cohere_state)
        #     gemini_state["thought_start"] = time.perf_counter()
        #     cohere_state["thought_start"] = time.perf_counter()
        #     gemini_state, gemini_textbox = choose_gemini_model.result()
        #     command_state, command_textbox = choose_command_model.result()

        # if not file_handler.skip_gemini:
        #     choose_gemini_model.start()
        #     choose_gemini_model.join()
        # if not file_handler.skip_mistral_n_command:
        #     choose_command_model.start()
        #     choose_command_model.join()

        # if not file_handler.skip_gemini and file_handler.skip_mistral_n_command:
        # if state["embed_model"] and state["rerank_model"]: print(f"Gemini thought for {state["gemini_end_thinking"]} seconds, took {state["gemini_end_generating"]} seconds to generate the answer, generated {len(state["gemini_response"])} tokens.\nEmbedded using {state["embed_model"]}, reranked using {state["rerank_model"]}, generated response using model {state["gemini_model"]}.\n\n-------------------------\n")
        # elif state["embed_model"]: print(f"Gemini thought for {state["gemini_end_thinking"]} seconds, took {state["gemini_end_generating"]} seconds to generate the answer, generated {len(state["gemini_response"])} tokens.\nEmbedded using {state["embed_model"]}, generated response using model {state["gemini_model"]}.\n\n-------------------------\n")
        # else:
        # TODO: MOVE THESE TO MODEL_CLIENT
        # gr.Info(f"Gemini thought for {gemini_state["gemini_end_thinking"]} seconds.\nTook {gemini_state["gemini_end_generating"]} seconds to generate the answer.\nGenerated {len(gemini_state["gemini_response"])} tokens.\nUsing model {gemini_state["gemini_model"]}.")
        # memory_handler.log_interaction(question, state["gemini_response"], "(Skipped.)", state["gemini_response"])

        # if file_handler.skip_gemini and not file_handler.skip_mistral_n_command:
        # if state["embed_model"] and state["rerank_model"]: print(f"Command thought for {state["command_end_thinking"]} seconds, took {state["command_end_generating"]} seconds to generate the answer, generated {len(state["command_response"])} tokens.\nEmbedded using {state["embed_model"]}, reranked using {state["rerank_model"]}, generated response using model {state["command_model"]}.\n\n-------------------------\n")
        # elif state["embed_model"]: print(f"Command thought for {state["command_end_thinking"]} seconds, took {state["command_end_generating"]} seconds to generate the answer, generated {len(state["command_response"])} tokens.\nEmbedded using {state["embed_model"]}, generated response using model {state["command_model"]}.\n\n-------------------------\n")
        # else:
        # TODO: MOVE THESE TO MODEL_CLIENT
        # gr.Info(f"Command thought for {cohere_state["command_end_thinking"]} seconds.\nTook {cohere_state["command_end_generating"]} seconds to generate the answer.\nGenerated {len(cohere_state["command_response"])} tokens.\nUsing model {cohere_state["command_model"]}.")
        # memory_handler.log_interaction(question, "(Skipped.)", state["command_response"], state["command_response"])

        # if file_handler.skip_gemini and file_handler.skip_mistral_n_command: print("The image types you provided are partially unsupported by each model!\n\n-------------------------\n")

        # if not file_handler.skip_gemini and not file_handler.skip_mistral_n_command:  # handling regularly
        # if state["embed_model"] and state["rerank_model"]: print(f"Gemini thought for {state["gemini_end_thinking"]} seconds, took {state["gemini_end_generating"]} seconds to generate the answer, generated {len(state["gemini_response"])} tokens, using model {state["gemini_model"]}.\nCommand thought for {state["command_end_thinking"]} seconds, took {state["command_end_generating"]} seconds to generate the answer, generated {len(state["command_response"])} tokens, using model {state["command_model"]}.\nEmbedded using {state["embed_model"]}, reranked using {state["rerank_model"]}.\n\n-------------------------\n\nGenerating full response...")
        # elif state["embed_model"]: print(f"Gemini thought for {state["gemini_end_thinking"]} seconds, took {state["gemini_end_generating"]} seconds to generate the answer, generated {len(state["gemini_response"])} tokens, using model {state["gemini_model"]}.\nCommand thought for {state["command_end_thinking"]} seconds, took {state["command_end_generating"]} seconds to generate the answer, generated {len(state["command_response"])} tokens, using model {state["command_model"]}.\nEmbedded using {state["embed_model"]}.\n\n-------------------------\n\nGenerating full response...")
        # else:
        # print(f"Gemini thought for {state["gemini_end_thinking"]} seconds, took {state["gemini_end_generating"]} seconds to generate the answer, generated {len(state["gemini_response"])} tokens, using model {state["gemini_model"]}.\nCommand thought for {state["command_end_thinking"]} seconds, took {state["command_end_generating"]} seconds to generate the answer, generated {len(state["command_response"])} tokens, using model {state["command_model"]}.\n\n-------------------------\n\nGenerating full response...")
        # t3 = threading.Thread(target=state["choose_merge_model"], args=(question,))
        # t3.start()
        # t3.join()
        # if state["embed_model"] and state["rerank_model"]: print (f"You: {question}\n\n-------------------------\n\n{state["merged_response"]}\n\n-------------------------\n\nThought for {state["gemini_merge_end_thinking"]} seconds in total, took {state["gemini_end_merging"]} seconds to merge the answers, generated {len(state["merged_response"])} tokens.\nEmbedded using {state["embed_model"]}, reranked using {state["rerank_model"]}.\nGenerated response using model {state["gemini_model"]} and {state["command_model"]}, merged using {state["gemini_merge_model"]}.\n\n-------------------------\n")
        # elif state["embed_model"]: print (f"You: {question}\n\n-------------------------\n\n{state["merged_response"]}\n\n-------------------------\n\nThought for {state["gemini_merge_end_thinking"]} seconds in total, took {state["gemini_end_merging"]} seconds to merge the answers, generated {len(state["merged_response"])} tokens.\nEmbedded using {state["embed_model"]}.\nGenerated response using model {state["gemini_model"]} and {state["command_model"]}, merged using {state["gemini_merge_model"]}.\n\n-------------------------\n")
        # else:
        # print (f"You: {question}\n\n-------------------------\n\n{state["merged_response"]}\n\n-------------------------\n\nThought for {state["gemini_merge_end_thinking"]} seconds in total, took {state["gemini_end_merging"]} seconds to merge the answers, generated {len(state["merged_response"])} tokens.\nGenerated response using model {state["gemini_model"]} and {state["command_model"]}, merged using {state["gemini_merge_model"]}.\n\n-------------------------\n")

        # memory_handler.memorize_response()
        # utils.set_marker()

    except Exception as e:
        gr.Warning(f'API Key invalid / An error occurred: {e}')
    return (gr.update(value="", visible=True), gr.update(visible=True), gr.update(visible=True), gemini_state, gr.update(), cohere_state, gr.update())