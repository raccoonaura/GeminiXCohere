from google.genai import types
from src import model_client
import numpy as np

def ge_embed(allchunks):  # gemini-embedding-001
    response = [
        np.array(e.values) for e in model_client.client.models.embed_content(
            model="gemini-embedding-001",
            contents=allchunks,
            config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")).embeddings
    ]
    embeddings = np.array(response)
    return embeddings

def e4_embed():  # embed-v4.0
    """empty"""
def e3_embed():  # embed-multilingual-v3.0
    """empty"""
def el3_embed():  # embed-multilingual-light-v3.0
    """empty"""