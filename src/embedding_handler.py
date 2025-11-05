from google.genai import types
from src import model_client
import numpy as np


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