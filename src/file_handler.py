from src import response_handler
from src import embedding_handler
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(BASE_DIR, "embeds", "note.txt")

def load_text_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def chunk_by_paragraph(max_length):
    paragraphs = load_text_file("embeds/" + response_handler.fN).split("\n\n")
    chunks = []
    cur_chunk = ""

    for paragraph in paragraphs:
        if len(cur_chunk) + len(paragraph) <= max_length:
            cur_chunk += paragraph + "\n\n"
        else:
            chunks.append(cur_chunk.strip())
            cur_chunk = paragraph + "\n\n"

    if cur_chunk.strip():
        chunks.append(cur_chunk.strip())

    return chunks

"""
def retrieve_relevant_chunks(question, top_k):
    similarities = []
    for item in embedding_handler.vector_store:
        score = cosine_similarity(question, item["vector"])
        similarities.append((score, item["chunk"]))

    similarities.sort(reverse=True, key=lambda x: x[0])
    return similarities[:top_k]
"""