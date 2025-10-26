from google.genai import types
from src import model_client
from src import file_handler
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
# import json
# vector_store = []

def ge_embed(question):  # gemini-embedding-001
    chunks = file_handler.chunk_by_paragraph(500)

    allchunks = [question] + chunks
    
    response = [
        np.array(e.values) for e in model_client.client.models.embed_content(
            model="gemini-embedding-001",
            contents=[allchunks],
            config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")).embeddings
    ]

    embeddings = np.array(response)
    query_embedding = embeddings[0:1]
    doc_embeddings = embeddings[1:]

    similarities = cosine_similarity(query_embedding, doc_embeddings)[0]

    for i, chunk in enumerate(chunks):
        print(f"Similarity: {similarities[i]:.4f} - {chunk}")

    """
    results = list(zip(chunks, similarities))
    results.sort(key=lambda x: x[1], reverse=True)

    print(f"Query: '{question}'\n")
    for i, score in results:
        print(f"Similarity: {score:.4f} - {i}")
    """

    """
    for i, chunk in enumerate(chunks):
        print(f"=== Chunk {i} ===")
        print(chunk)
        print()
    for i, chunk in enumerate(chunks):
        print(f"=== Chunk {i} ===")
        print(chunk)
        print()

    for chunk in chunks:
        response = model_client.client.models.embed_content(
            model="gemini-embedding-001",
            contents=[chunk],
            config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
        )
        vector = response.embeddings
        for vec in vector:
            vector_store.append({
                "chunk": chunk,
                "vector": vec
            })
    print(file_handler.retrieve_relevant_chunks(question, 3))
    """

def e4_embed():  # embed-v4.0
    """empty"""
def e3_embed():  # embed-multilingual-v3.0
    """empty"""
def el3_embed():  # embed-multilingual-light-v3.0
    """empty"""
def ge_embed_merge():  # gemini-embedding-001
    """empty"""