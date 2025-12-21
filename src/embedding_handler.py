from google.genai import types
from src import embedding_handler
from src import file_handler
from src import model_client
from src import utils
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def embedding(question, text):
    if text == "error!": return "error!"
    question = question[1:]
    utils.set_marker()
    print("Chunking...")
    chunks = file_handler.chunk_by_sentence(text, 500, 2)
    allchunks = [question] + chunks
    if len(allchunks) > 100:
        print("The document is too long!")
        return "error!"
    utils.clear_screen()
    print("Chunking... Done!")
    utils.set_marker()
    print("Embedding...")
    try:
        model_client.embed_model = "Gemini Embedding 001"
        query_embedding, doc_embeddings = embedding_handler.gemini_embed("gemini-embedding-001", allchunks)
    except:
        try:
            model_client.embed_model = "Embed v4.0"
            query_embedding, doc_embeddings = embedding_handler.embed_embed("embed-v4.0", allchunks)
            query_embedding = np.array(query_embedding)
            doc_embeddings = np.array(doc_embeddings)
        except:
            try:
                model_client.embed_model = "Embed Multilingual v3.0"
                query_embedding, doc_embeddings = embedding_handler.embed_embed("embed-multilingual-v3.0", allchunks)
                query_embedding = np.array(query_embedding)
                doc_embeddings = np.array(doc_embeddings)
            except:
                try:
                    model_client.embed_model = "Embed Multilingual Light v3.0"
                    query_embedding, doc_embeddings = embedding_handler.embed_embed("embed-multilingual-light-v3.0", allchunks)
                    query_embedding = np.array(query_embedding)
                    doc_embeddings = np.array(doc_embeddings)
                except Exception as e:
                    model_client.embed_model = ""
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
        model_client.rerank_model = "Rerank v3.5"
        context_parts = embedding_handler.rerank_rerank("rerank-v3.5", top_k_results, question)
        utils.clear_screen()
        print("Reranking... Done!")
    except:
        try:
            model_client.rerank_model = "Rerank Multilingual v3.0"
            context_parts = embedding_handler.rerank_rerank("rerank-multilingual-v3.0", top_k_results, question)
            utils.clear_screen()
            print("Reranking... Done!")
        except:
            model_client.rerank_model = ""
            top_k_indices = np.argsort(similarities)[::-1][:3]
            context_parts = []
            for rank, idx in enumerate(top_k_indices, 1):
                context_parts.append(f"[參考資料 {rank}] (相似度: {similarities[idx]:.2f})\n{allchunks[idx]}")
            utils.clear_screen()
            print("Reranking... Skipped! The rate limit might be reached!")
    context = "\n\n".join(context_parts)
    context = "Reference materials and contexts:\n\n" + context + "\n\nDo not refer to the provided information as 'snippets,' 'sections,' 'parts,' or by any implied numerical order."
    return context

def gemini_embed(model, allchunks):
    response = [
        np.array(e.values) for e in model_client.client.models.embed_content(
            model=model,
            contents=allchunks,
            config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")).embeddings
    ]
    embeddings = np.array(response)
    query_embedding = embeddings[0:1]
    doc_embeddings = embeddings[1:]
    return query_embedding, doc_embeddings

def embed_embed(model, allchunks):  # like, thats the name of cohere's embed model, what can i say
    co = model_client.co
    query = allchunks[0:1]
    chunks = allchunks[1:]

    query_res = co.embed(
        texts=query,
        model=model,
        input_type="search_query",
        embedding_types=["float"]
    )
    chunks_res = co.embed(
        texts=chunks,
        model=model,
        input_type="search_document",
        embedding_types=["float"]
    )
    query_embedding = query_res.embeddings.float
    doc_embeddings = chunks_res.embeddings.float
    return query_embedding, doc_embeddings

def rerank_rerank(model, top_k_results, question):  # yes, thats the name of cohere's rerank model
    co = model_client.co
    results = co.rerank(
        model=model,
        query=question,
        documents=top_k_results,
        top_n=3,
    )
    context_parts = []
    for idx, result in enumerate(results.results):
        context_parts.append(f"[參考資料 {idx+1}] (相似度: {result.relevance_score:.2f})\n{top_k_results[result.index]}")
    return context_parts