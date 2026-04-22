from google.genai import Client
from mistralai.client import Mistral
from cohere import ClientV2
from src.cli import embedding_handler
from src.cli import response_handler
from src.cli import generate_handler
from src.cli import memory_handler
from src.cli import file_handler
from src.cli import utils
import numpy as np
import time
import os

gemini_client = None
mistral_client = None
cohere_client = None

gemini_messages = []
mistral_messages = []
command_messages = []
merged_messages = []
gemini_parts = []
merged_part = None
gemini_response = ""
mistral_response = ""
command_response = ""
merged_response = ""
gemini_cot = ""
mistral_cot = ""
command_cot = ""
gemini_thought = False
mistral_thought = False
command_thought = False
gemini_end_thinking = None
mistral_end_thinking = None
command_end_thinking = None
gemini_merge_end_thinking = None
gemini_start_generating = None
mistral_start_generating = None
command_start_generating = None
gemini_start_merging = None
gemini_end_generating = None
mistral_end_generating = None
command_end_generating = None
gemini_end_merging = None
gemini_model = ""
mistral_model = ""
command_model = ""
gemini_merge_model = ""
embed_model = ""
rerank_model = ""

def initialize_gemini():
    global gemini_client
    while not gemini_client:
        utils.clear_all()
        try:
            if os.environ["Gemini_API_Key"]:
                key = os.environ["Gemini_API_Key"]
            else:
                key = input("Enter Gemini API key: ").strip()
            if key == "":  # empty input check
                continue
            else:
                print("Checking if the key is valid... (1/3)")
                gemini_client = Client(api_key=key)
                gemini_client.models.list()
        except Exception as e:
            memory_handler.log_errors(e)
            gemini_client = None

def initialize_mistral():
    global mistral_client
    while not mistral_client:
        utils.clear_all()
        try:
            if os.environ["Mistral_API_Key"]:
                key = os.environ["Mistral_API_Key"]
            else:
                key = input("Enter Mistral API key: ").strip()
            if key == "":  # empty input check
                continue
            else:
                print("Checking if the key is valid... (2/3)")
                mistral_client = Mistral(api_key=key)
                mistral_client.models.list()
        except Exception as e:
            memory_handler.log_errors(e)
            mistral_client = None

def initialize_cohere():
    global cohere_client
    while not cohere_client:
        utils.clear_all()
        try:
            if os.environ["Cohere_API_Key"]:
                key = os.environ["Cohere_API_Key"]
            else:
                key = input("Enter Cohere API key: ").strip()
            if key == "":  # empty input check
                continue
            else:
                print("Checking if the key is valid... (3/3)")
                cohere_client = ClientV2(api_key=key)
                cohere_client.models.list()
        except Exception as e:
            memory_handler.log_errors(e)
            cohere_client = None

def choose_gemini_model(question):
    global gemini_cot, gemini_thought, gemini_model
    gemini_cot = ""
    gemini_thought = False
    # for some reason, Gemini 2.0 is called 2.0, Gemini 3 is called 3???????
    try:  # Gemini 3.1 Pro, it doesn't support NO reasoning
        if response_handler.spreadsheet:
            raise utils.Error("Skipping Gemini 3 for TAG")
        # for some reason, at least for this project,
        # Gemini 3 tweaks when you tryna function call,
        # VERY LIKELY caused by thought signature,
        # since its REQUIRED (not optional) for function calling in Gemini 3
        # but all the fixes i tried, doesnt work, somehow
        if question[0] == "@":  # Reasoning
            gemini_model = "Gemini 3.1 Pro"
            generate_handler.gemini_generate("gemini-3.1-pro-preview", True)
        else:  # No reasoning
            raise utils.Error("Pro requires thinking")
    except Exception as e:
        memory_handler.log_errors(e)
        if not gemini_thought:
            try:  # Gemini 3 Flash, fallback if Pro is not available
                if response_handler.spreadsheet:
                    raise utils.Error("Skipping Gemini 3 for TAG")
                gemini_model = "Gemini 3 Flash"
                if question[0] == "@":  # Reasoning
                    generate_handler.gemini_generate("gemini-3-flash-preview", True)
                else:  # No reasoning
                    generate_handler.gemini_generate("gemini-3-flash-preview")
            except Exception as e:
                memory_handler.log_errors(e)
                if not gemini_thought:
                    try:  # Gemini 3.1 Flash Lite, fallback if Flash is not available
                        if response_handler.spreadsheet:
                            raise utils.Error("Skipping Gemini 3 for TAG")
                        gemini_model = "Gemini 3.1 Flash Lite"
                        if question[0] == "@":  # Reasoning
                            generate_handler.gemini_generate("gemini-3.1-flash-lite-preview", True)
                        else:  # No reasoning
                            generate_handler.gemini_generate("gemini-3.1-flash-lite-preview")
                    except Exception as e:
                        memory_handler.log_errors(e)
                        if not gemini_thought:
                            try:  # Gemini 2.5 Pro, it doesn't support NO reasoning
                                if question[0] == "@":  # Reasoning
                                    gemini_model = "Gemini 2.5 Pro"
                                    generate_handler.gemini_generate("gemini-2.5-pro", True)
                                else:  # No reasoning
                                    raise utils.Error("Pro requires thinking")
                            except Exception as e:
                                memory_handler.log_errors(e)
                                if not gemini_thought:
                                    try:  # Gemini 2.5 Flash, fallback if Pro is not available
                                        gemini_model = "Gemini 2.5 Flash"
                                        if question[0] == "@":  # Reasoning
                                            generate_handler.gemini_generate("gemini-2.5-flash", True)
                                        else:  # No reasoning
                                            generate_handler.gemini_generate("gemini-2.5-flash")
                                    except Exception as e:
                                        memory_handler.log_errors(e)
                                        if not gemini_thought:
                                            try:  # Gemini 2.5 Flash Lite, fallback if Flash is not available
                                                gemini_model = "Gemini 2.5 Flash Lite"
                                                if question[0] == "@":  # Reasoning
                                                    generate_handler.gemini_generate("gemini-2.5-flash-lite", True)
                                                else:  # No reasoning
                                                    generate_handler.gemini_generate("gemini-2.5-flash-lite")
                                            except Exception as e:
                                                memory_handler.log_errors(e)
                                                if not gemini_thought:
                                                    try:  # Gemini 2.0 Flash, fallback if 2.5 is not available
                                                        gemini_model = "Gemini 2.0 Flash"
                                                        if question[0] == "@":  # Reasoning
                                                            generate_handler.gemini_generate("gemini-2.0-flash", True)
                                                        else:  # No reasoning
                                                            generate_handler.gemini_generate("gemini-2.0-flash")
                                                    except Exception as e:
                                                        memory_handler.log_errors(e)
                                                        if not gemini_thought:
                                                            try:  # Gemini 2.0 Flash Lite, fallback if Flash is not available, doesn't support reasoning
                                                                gemini_model = "Gemini 2.0 Flash Lite"
                                                                generate_handler.gemini_generate("gemini-2.0-flash-lite")
                                                            except Exception as e:
                                                                memory_handler.log_errors(e)
                                                                print(f'Gemini API Key invalid / An error occurred: {e}')

def choose_mistral_model(question):
    global mistral_cot, mistral_response, mistral_thought, mistral_model
    mistral_cot = ""
    mistral_thought = False
    mistral_response = ""
    try:
        mistral_model = "Mistral Small 4"
        if question[0] == "@":  # Reasoning
            generate_handler.mistral_generate("mistral-small-2603", True)
        else:  # No reasoning
            generate_handler.mistral_generate("mistral-small-2603")
    except Exception as e:
        memory_handler.log_errors(e)
        if not mistral_thought:
            try:
                if question[0] == "@":  # Reasoning
                    mistral_model = "Magistral Medium 1.2"
                    generate_handler.mistral_generate("magistral-medium-2509")
                else:  # No reasoning
                    mistral_model = "Mistral Small 3.2"
                    generate_handler.mistral_generate("mistral-small-2506")
            except Exception as e:
                memory_handler.log_errors(e)
                if not mistral_thought:
                    try:
                        if question[0] == "@":  # Reasoning
                            mistral_model = "Mistral Large 3"
                            generate_handler.mistral_generate("mistral-large-2512")
                        else:  # No reasoning
                            mistral_model = "Ministral 3 14B"
                            generate_handler.mistral_generate("ministral-14b-2512")
                    except Exception as e:
                        memory_handler.log_errors(e)
                        if not mistral_thought:
                            try:
                                if question[0] == "@":  # Reasoning
                                    mistral_model = "Mistral Medium 3.1"
                                    generate_handler.mistral_generate("mistral-medium-2508")
                                else:  # No reasoning
                                    mistral_model = "Ministral 3 8B"
                                    generate_handler.mistral_generate("ministral-8b-2512")
                            except Exception as e:
                                memory_handler.log_errors(e)
                                if not mistral_thought:
                                    try:
                                        if question[0] == "@":  # Reasoning
                                            mistral_model = "Mistral Medium 3"
                                            generate_handler.mistral_generate("mistral-medium-2505")
                                        else:  # No reasoning
                                            if file_handler.mistral_n_command_image:
                                                raise utils.Error("Skipping Nemo for vision")
                                            mistral_model = "Mistral Nemo 12B"
                                            generate_handler.mistral_generate("open-mistral-nemo-2407")
                                    except Exception as e:
                                        memory_handler.log_errors(e)
                                        if not mistral_thought:
                                            try:
                                                if question[0] == "@":  # Reasoning
                                                    mistral_model = "Magistral Small 1.2"  # this model sucks just check the benchmarks
                                                    generate_handler.mistral_generate("magistral-small-2509")
                                                else:  # No reasoning
                                                    mistral_model = "Ministral 3 3B"
                                                    generate_handler.mistral_generate("ministral-3b-2512")
                                            except Exception as e:
                                                memory_handler.log_errors(e)
                                                print(f'Mistral API Key invalid / An error occurred: {e}')

def choose_command_model(question):
    global command_cot, command_response, command_thought, command_model
    command_cot = ""
    command_thought = False
    command_response = ""
    original_error = ""
    try:  # Command A
        if question[0] == "@":  # Reasoning
            command_model = "Command A Reasoning"
            generate_handler.command_generate("command-a-reasoning-08-2025", "enabled")
        else:  # No reasoning
            if file_handler.mistral_n_command_image:
                command_model = "Command A Vision"
                generate_handler.command_generate("command-a-vision-07-2025")
            else:
                command_model = "Command A"
                generate_handler.command_generate("command-a-03-2025")
    except Exception as e:
        memory_handler.log_errors(e)
        original_error = e
        if not command_thought:
            try:
                if file_handler.mistral_n_command_image:
                    raise utils.Error("Skipping Command R for vision")
                command_model = "Command R+"
                generate_handler.command_generate("command-r-plus-08-2024")
            except Exception as e:
                memory_handler.log_errors(e)
                if not command_thought:
                    try:
                        if file_handler.mistral_n_command_image:
                            raise utils.Error("Skipping Command R for vision")
                        command_model = "Command R"
                        generate_handler.command_generate("command-r-08-2024")
                    except Exception as e:
                        memory_handler.log_errors(e)
                        if not command_thought:
                            try:
                                if file_handler.mistral_n_command_image:
                                    raise utils.Error("Skipping Command R for vision")
                                command_model = "Command R7B"
                                generate_handler.command_generate("command-r7b-12-2024")
                            except Exception as e:
                                memory_handler.log_errors(e)
                                if file_handler.mistral_n_command_image:
                                    e = original_error
                                print(f'Cohere API Key invalid / An error occurred: {e}')

def choose_merge_model(question):
    global merged_messages, gemini_start_merging, gemini_merge_model
    gemini_start_merging = time.perf_counter()
    merged_messages = [{"role": "user", "parts": [{"text": question}]}]
    try:  # Gemini 3.1 Pro, it doesn't support NO reasoning
        if question[0] == "@":  # Reasoning
            gemini_merge_model = "Gemini 3.1 Pro"
            generate_handler.gemini_merge("gemini-3.1-pro-preview", True)
        else:  # No reasoning
            raise utils.Error("Pro requires thinking")
        utils.clear_all()
    except Exception as e:
        memory_handler.log_errors(e)
        try:  # Gemini 3 Flash, fallback if Pro is not available
            gemini_merge_model = "Gemini 3 Flash"
            if question[0] == "@":  # Reasoning
                generate_handler.gemini_merge("gemini-3-flash-preview", True)
            else:  # No reasoning
                generate_handler.gemini_merge("gemini-3-flash-preview", False)
            utils.clear_all()
        except Exception as e:
            memory_handler.log_errors(e)
            try:  # Gemini 3.1 Flash Lite, fallback if Flash is not available
                gemini_merge_model = "Gemini 3.1 Flash Lite"
                if question[0] == "@":  # Reasoning
                    generate_handler.gemini_merge("gemini-3.1-flash-lite-preview", True)
                else:  # No reasoning
                    generate_handler.gemini_merge("gemini-3.1-flash-lite-preview", False)
                utils.clear_all()
            except Exception as e:
                memory_handler.log_errors(e)
                try:  # Gemini 2.5 Pro, it doesn't support NO reasoning
                    if question[0] == "@":  # Reasoning
                        gemini_merge_model = "Gemini 2.5 Pro"
                        generate_handler.gemini_merge("gemini-2.5-pro", True)
                    else:  # No reasoning
                        raise utils.Error("Pro requires thinking")
                    utils.clear_all()
                except Exception as e:
                    memory_handler.log_errors(e)
                    try:  # Gemini 2.5 Flash, fallback if Pro is not available
                        gemini_merge_model = "Gemini 2.5 Flash"
                        if question[0] == "@":  # Reasoning
                            generate_handler.gemini_merge("gemini-2.5-flash", True)
                        else:  # No reasoning
                            generate_handler.gemini_merge("gemini-2.5-flash", False)
                        utils.clear_all()
                    except Exception as e:
                        memory_handler.log_errors(e)
                        try:  # Gemini 2.5 Flash Lite, fallback if Flash is not available
                            gemini_merge_model = "Gemini 2.5 Flash Lite"
                            if question[0] == "@":  # Reasoning
                                generate_handler.gemini_merge("gemini-2.5-flash-lite", True)
                            else:  # No reasoning
                                generate_handler.gemini_merge("gemini-2.5-flash-lite", False)
                            utils.clear_all()
                        except Exception as e:
                            memory_handler.log_errors(e)
                            try:  # Gemini 2.0 Flash, fallback if 2.5 is not available
                                gemini_merge_model = "Gemini 2.0 Flash"
                                if question[0] == "@":  # Reasoning
                                    generate_handler.gemini_generate("gemini-2.0-flash", True)
                                else:  # No reasoning
                                    generate_handler.gemini_generate("gemini-2.0-flash", False)
                            except Exception as e:
                                memory_handler.log_errors(e)
                                try:  # Gemini 2.0 Flash Lite, fallback if Flash is not available, doesn't support reasoning
                                    gemini_merge_model = "Gemini 2.0 Flash Lite"
                                    generate_handler.gemini_generate("gemini-2.0-flash-lite", False)
                                except Exception as e:
                                    memory_handler.log_errors(e)
                                    print(f'Gemini API Key invalid / An error occurred: {e}')

def choose_embed_model(allchunks):
    global embed_model
    try:
        embed_model = "Embed 4"
        query_embedding, doc_embeddings = embedding_handler.embed_embed("embed-v4.0", allchunks)
    except Exception as e:
        memory_handler.log_errors(e)
        try:
            embed_model = "Gemini Embedding 2"
            query_embedding, doc_embeddings = embedding_handler.gemini_embed("gemini-embedding-2-preview", allchunks)
        except Exception as e:
            memory_handler.log_errors(e)
            try:
                embed_model = "Gemini Embedding"
                query_embedding, doc_embeddings = embedding_handler.gemini_embed("gemini-embedding-001", allchunks)
            except Exception as e:
                memory_handler.log_errors(e)
                try:
                    embed_model = "Embed 3"
                    query_embedding, doc_embeddings = embedding_handler.embed_embed("embed-multilingual-v3.0", allchunks)
                except Exception as e:
                    memory_handler.log_errors(e)
                    try:
                        embed_model = "Embed Light 3"
                        query_embedding, doc_embeddings = embedding_handler.embed_embed("embed-multilingual-light-v3.0", allchunks)
                    except Exception as e:
                        memory_handler.log_errors(e)
                        try:
                            embed_model = "Mistral Embed"  # insanely slow and reaches the rate-limit easily, not really an option for real-time rag
                            query_embedding, doc_embeddings = embedding_handler.mistral_embed("mistral-embed-2312", allchunks)
                        except Exception as e:
                            memory_handler.log_errors(e)
                            embed_model = ""
                            print("An error occurred while embedding: ", e)
                            return "error!", "error!"
    return query_embedding, doc_embeddings

def choose_rerank_model(similarities, top_k_results, question, allchunks):
    global rerank_model
    try:
        rerank_model = "Rerank 4 Pro"
        context_parts = embedding_handler.rerank_rerank("rerank-v4.0-pro", top_k_results, question)
        utils.clear_screen()
        print("Reranking... Done!")
    except Exception as e:
        memory_handler.log_errors(e)
        try:
            rerank_model = "Rerank 4 Fast"
            context_parts = embedding_handler.rerank_rerank("rerank-v4.0-fast", top_k_results, question)
            utils.clear_screen()
            print("Reranking... Done!")
        except Exception as e:
            memory_handler.log_errors(e)
            try:
                rerank_model = "Rerank 3.5"
                context_parts = embedding_handler.rerank_rerank("rerank-v3.5", top_k_results, question)
                utils.clear_screen()
                print("Reranking... Done!")
            except Exception as e:
                memory_handler.log_errors(e)
                try:
                    rerank_model = "Rerank 3"
                    context_parts = embedding_handler.rerank_rerank("rerank-multilingual-v3.0", top_k_results, question)
                    utils.clear_screen()
                    print("Reranking... Done!")
                except Exception as e:
                    memory_handler.log_errors(e)
                    rerank_model = ""
                    top_k_indices = np.argsort(similarities)[::-1][:3]
                    context_parts = []
                    for rank, idx in enumerate(top_k_indices, 1):
                        context_parts.append(f"[Reference material {rank}] (Similarity: {similarities[idx]:.2f})\n{allchunks[idx]}")
                    utils.clear_screen()
                    print("Reranking... Skipped! The rate limit might be reached!")
    return context_parts