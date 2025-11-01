from google.genai import types
from src import model_client
from src import file_handler
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
# import json
# vector_store = []

def ge_embed(question):  # gemini-embedding-001
    chunks = file_handler.chunk_by_sentence(500, 2)
    allchunks = [question] + chunks

    response = [
        np.array(e.values) for e in model_client.client.models.embed_content(
            model="gemini-embedding-001",
            contents=allchunks,
            config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")).embeddings
    ]
    embeddings = np.array(response)
    query_embedding = embeddings[0:1]
    doc_embeddings = embeddings[1:]

    similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
    top_k_indices = np.argsort(similarities)[::-1][:3]
    context_parts = []
    for rank, idx in enumerate(top_k_indices, 1):
        context_parts.append(f"[參考資料 {rank}] (相似度: {similarities[idx]:.2f})\n{allchunks[idx]}")

    context = "\n\n".join(context_parts)
    context = "Reference materials and contexts:\n\n" + context
    return context

def e4_embed():  # embed-v4.0
    """empty"""
def e3_embed():  # embed-multilingual-v3.0
    """empty"""
def el3_embed():  # embed-multilingual-light-v3.0
    """empty"""
def ge_embed_merge():  # gemini-embedding-001
    """empty"""