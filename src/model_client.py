from google.genai import Client
from cohere import ClientV2
from sklearn.metrics.pairwise import cosine_similarity
from src import response_handler
from src import generate_handler
from src import embedding_handler
from src import file_handler
from src import utils
import numpy as np
import time

client = None  # Gemini client
co = None  # Cohere client
# vs code kept asking me to add the previous two lines (WHY) even tho the whole thing works without them

gemini_messages = []
command_messages = []
merged_messages = []
full_response = []
gemini_response = ""
command_response = ""
merged_response = ""
gemini_thought = False
command_thought = False
gemini_end_thinking = None
command_end_thinking = None
gemini_merge_end_thinking = None
gemini_start_generating = None
command_start_generating = None
gemini_start_merging = None
gemini_end_generating = None
command_end_generating = None
gemini_end_merging = None
gemini_model = ""
command_model = ""
gemini_merge_model = ""
embed_model = ""
rerank_model = ""

def initialize_gemini():
    global client
    while not client:
        utils.clear_all()
        try:
            key = input("Enter Gemini API Key: ").strip()
            if key == "":  # empty input check
                continue
            else:
                client = Client(api_key=key)
        except: client = None  # KeyboardInterrupt check

def initialize_cohere():
    global co
    while not co:
        utils.clear_all()
        try:
            key = input("Enter Cohere API Key: ").strip()
            if key == "":  # empty input check
                continue
            else:
                co = ClientV2(api_key=key)
        except: co = None  # KeyboardInterrupt check

def memorize_question(question):
    if question[0] == "$": question = question[1:]
    if question[0] == "@": question = question[1:]
    if file_handler.gemini_image:
        gemini_messages.append({"role": "user","parts": [{"text": question},{"inline_data": file_handler.gemini_image}]})
    else:
        gemini_messages.append({"role": "user", "parts": [{"text": question}]})
    if file_handler.command_image:
        command_messages.append({"role": "user", "content": [{"type": "text","text": question},{"type": "image_url","image_url": {"url": file_handler.command_image,"detail": "high"}}]})
    else:
        command_messages.append({"role": "user", "content": question})

def memorize_response():
    gemini_messages.append({"role": "model", "parts": [{"text": merged_response}]})
    command_messages.append({"role": "assistant", "content": merged_response})

def embedding(question):
    global embed_model, rerank_model
    question = question[1:]
    utils.set_marker()
    print("Chunking...")
    chunks = file_handler.chunk_by_sentence(500, 2)
    allchunks = [question] + chunks
    if len(allchunks) > 100:
        print("The document is too long!")
        return "error!"
    utils.clear_screen()
    print("Chunking... Done!")
    utils.set_marker()
    print("Embedding...")
    try:
        embed_model = "Gemini Embedding 001"
        query_embedding, doc_embeddings = embedding_handler.gemini_embed("gemini-embedding-001", allchunks)
    except:
        try:
            embed_model = "Embed v4.0"
            query_embedding, doc_embeddings = embedding_handler.embed_embed("embed-v4.0", allchunks)
            query_embedding = np.array(query_embedding)
            doc_embeddings = np.array(doc_embeddings)
        except:
            try:
                embed_model = "Embed Multilingual v3.0"
                query_embedding, doc_embeddings = embedding_handler.embed_embed("embed-multilingual-v3.0", allchunks)
                query_embedding = np.array(query_embedding)
                doc_embeddings = np.array(doc_embeddings)
            except:
                try:
                    embed_model = "Embed Multilingual Light v3.0"
                    query_embedding, doc_embeddings = embedding_handler.embed_embed("embed-multilingual-light-v3.0", allchunks)
                    query_embedding = np.array(query_embedding)
                    doc_embeddings = np.array(doc_embeddings)
                except Exception as e:
                    embed_model = ""
                    print("An error occurred while embedding: ", e)
                    return "error!"
    if query_embedding.size == 0 or doc_embeddings.size == 0:
        print("An error occurred while embedding! The rate limit might be reached!")
        return "error!"
    utils.clear_screen()
    print("Embedding... Done!")
    utils.set_marker()
    print("Calculating...")

    similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
    if len(allchunks) >= 10: top_ks = 10
    else: top_ks = len(allchunks)
    top_k_indices = np.argsort(similarities)[::-1][:top_ks]
    top_k_results = [chunks[i] for i in top_k_indices]
    utils.clear_screen()
    print("Calculating... Done!")
    utils.set_marker()
    print("Reranking...")
    try:
        rerank_model = "Rerank v3.5"
        context_parts = embedding_handler.rerank_rerank("rerank-v3.5", top_k_results, question)
        utils.clear_screen()
        print("Reranking... Done!")
    except:
        try:
            rerank_model = "Rerank Multilingual v3.0"
            context_parts = embedding_handler.rerank_rerank("rerank-multilingual-v3.0", top_k_results, question)
            utils.clear_screen()
            print("Reranking... Done!")
        except:
            rerank_model = ""
            top_k_indices = np.argsort(similarities)[::-1][:3]
            context_parts = []
            for rank, idx in enumerate(top_k_indices, 1):
                context_parts.append(f"[參考資料 {rank}] (相似度: {similarities[idx]:.2f})\n{allchunks[idx]}")
            utils.clear_screen()
            print("Reranking... Skipped! The rate limit might be reached!")
    context = "\n\n".join(context_parts)
    context = "Reference materials and contexts:\n\n" + context + "\n\nDo not refer to the provided information as 'snippets,' 'sections,' 'parts,' or by any implied numerical order."
    return context

def ask_gemini(question):
    global gemini_messages, gemini_response, full_response, gemini_thought, gemini_end_thinking, gemini_start_generating, gemini_end_generating, gemini_model
    gemini_thought = False
    full_response.clear()
    try:  # Gemini 2.5 Pro, it doesn't support NO reasoning
        if question[0] == "@":  # Reasoning
            gemini_model = "Gemini 2.5 Pro"
            generate_handler.gemini_generate("gemini-2.5-pro", True)
        else:  # No reasoning
            gemini_model = "Gemini 2.5 Flash"
            generate_handler.gemini_generate("gemini-2.5-flash", False)
    except:
        try:  # Gemini 2.5 Flash, fallback if Pro is not available
            gemini_model = "Gemini 2.5 Flash"
            if question[0] == "@":  # Reasoning
                generate_handler.gemini_generate("gemini-2.5-flash", True)
            else:  # No reasoning
                generate_handler.gemini_generate("gemini-2.5-flash", False)
        except:
            try:  # Gemini 2.5 Flash Lite, fallback if Flash is not available, although you'll barely reach this point
                gemini_model = "Gemini 2.5 Flash Lite"
                if question[0] == "@":  # Reasoning
                    generate_handler.gemini_generate("gemini-2.5-flash-lite", True)
                else:  # No reasoning
                    generate_handler.gemini_generate("gemini-2.5-flash-lite", False)
            except Exception as e:  # Erm... you are probably doing something wrong!
                print("Gemini API Key invalid / An error occurred: ", e)
    gemini_response = ''.join(full_response)  # Join all chunks into a single string for logging and further processing
    gemini_end_generating = f"{time.perf_counter() - gemini_start_generating:.3f}"
    print ("\n\n-------------------------\n")

def ask_command(question):
    global command_messages, command_response, command_thought, command_end_thinking, command_start_generating, command_end_generating, command_model
    command_thought = False
    command_response = ""
    try:  # Command A
        command_model = "Command A"
        if question[0] == "@":  # Reasoning
            generate_handler.command_generate("command-a-reasoning-08-2025", "enabled")
        else:  # No reasoning
            if file_handler.command_image: generate_handler.command_generate("command-a-vision-07-2025", "disabled")
            else: generate_handler.command_generate("command-a-03-2025", "disabled")
    except Exception as e:
        print(e)
        try:  # Command R+, fallback if A is not available, it doesn't support reasoning
            command_model = "Command R+"
            generate_handler.command_generate("command-r-plus-08-2024", "disabled")
        except:
            try:  # Command R, fallback if R+ is not available, although you'll barely reach this point, R doesn't support reasoning
                command_model = "Command R"
                generate_handler.command_generate("command-r-08-2024", "disabled")
            except Exception as e:  # Erm... you are probably doing something wrong!
                print("Cohere API Key invalid / An error occurred: ", e)
    command_end_generating = f"{time.perf_counter() - command_start_generating:.3f}"
    if file_handler.skip_gemini: print ("\n\n-------------------------\n")

def merge_responses(question):
    global gemini_response, command_response, merged_messages, merged_response, gemini_merge_end_thinking, gemini_start_merging, gemini_end_merging, gemini_merge_model, error
    gemini_start_merging = time.perf_counter()
    merged_messages = [{"role": "user", "parts": [{"text": question}]}]

    try:  # Gemini 2.5 Pro, it doesn't support NO reasoning
        if question[0] == "@":  # Reasoning
            gemini_merge_model = "Gemini 2.5 Pro"
            response = generate_handler.gemini_merge("gemini-2.5-pro", True)
        else:  # No reasoning
            gemini_merge_model = "Gemini 2.5 Flash"
            response = generate_handler.gemini_merge("gemini-2.5-flash", False)
        utils.clear_all()
    except:
        try:  # Gemini 2.5 Flash, fallback if Pro is not available
            if question[0] == "@":  # Reasoning
                gemini_merge_model = "Gemini 2.5 Flash"
                response = generate_handler.gemini_merge("gemini-2.5-flash", True)
            else:  # No reasoning
                gemini_merge_model = "Gemini 2.5 Flash"
                response = generate_handler.gemini_merge("gemini-2.5-flash", False)
            utils.clear_all()
        except:
            try:  # Gemini 2.5 Flash Lite, fallback if Flash is not available, although you'll barely reach this point
                if question[0] == "@":  # Reasoning
                    gemini_merge_model = "Gemini 2.5 Flash Lite"
                    response = generate_handler.gemini_merge("gemini-2.5-flash-lite", True)
                else:  # No reasoning
                    gemini_merge_model = "Gemini 2.5 Flash Lite"
                    response = generate_handler.gemini_merge("gemini-2.5-flash-lite", False)
                utils.clear_all()
            except Exception as e:  # Erm... you are probably doing something wrong!
                print("Gemini API Key invalid / An error occurred: ", e)
    gemini_merge_end_thinking = f"{time.perf_counter() - response_handler.thought_start:.3f}"
    gemini_end_merging = f"{time.perf_counter() - gemini_start_merging:.3f}"
    merged_response = response.text