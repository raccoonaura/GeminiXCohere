from google.genai import types
from src import embedding_handler
from src import model_client
from src import utils
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

def chunk_by_sentence(text, max_length, overlap):  # 我決定把每一句留下中文註解 因為我自己都快亂了:P
    """ max_length: 用字數計算, overlap: 用句數計算,
        sentences: 切斷後的本文, 含全部的句子, sentence: 本文切段後的一個句子,
        current_chunk: 一個段落, 好幾個句子, chunks: 切段並重新安排後的好幾個段落,
        tail: 上一個段落的尾端幾句, """

    sentences = re.split(r'(?<=[。！？.!?…])\s*', text)  # 遇到。！？.!?…這些符號之一就切成一句
    sentences = [s.strip() for s in sentences if s.strip()]  # 避免符號單獨一句

    chunks = []
    current_chunk = []
    current_length = 0
    i = 0
    while i < len(sentences):  # while現在確認的句數不超過全部句子的總數時
        sentence = sentences[i]  # 現在這句就是全部句子中的第i個

        if sentence.lstrip().startswith("#"):  # 如果這句是以#開頭
            if current_chunk:  # 如果current_chunk不是空的
                chunks.append(" ".join(current_chunk))  # 把current_chunk加入chunks裡
            current_chunk = [sentence]  # 全新的current_chunk加入含#的那句
            current_length = len(sentence)  # 把這句的字數設為總長度
            i += 1  # 換下一句
            continue

        if current_length + len(sentence) > max_length:  # 如果current_chunk新的總長度加上現在這句的字數"會"超過上限
            if current_chunk:  # 如果current_chunk不是空的
                chunks.append(" ".join(current_chunk))  # 把current_chunk加入chunks裡

                if len(current_chunk) > overlap:  # 如果現在的current_chunk包含的句數比overlap所保留的句數還多的時候
                    tail = current_chunk[-overlap:]  # 從尾部取出overlap所保留的句數, 保留起來
                else:  # 如果現在的current_chunk包含的句數跟overlap所保留的句數一樣多或更少的時候
                    tail = current_chunk[:]  # 把整段current_chunk全部保留下來

                while tail:  # 當tail存在時
                    tail_length = sum(len(s) for s in tail)  # 算出tail裡每一句的字數加總
                    if tail_length + len(sentence) <= max_length:  # 如果總字數加上這句的字數不會超過上限
                        break  # 離開這個迴圈
                    tail.pop(0)  # 把tail的第一句刪了, 然後回到這個迴圈的開頭再確認一次會不會超過次數

                current_chunk = tail  # 全新的current_chunk加入overlap的部分
                current_length = sum(len(s) for s in tail)  # 算字數

            if current_length + len(sentence) <= max_length:  # 如果current_chunk新的總長度加上現在這句的字數"不會"超過上限
                current_chunk.append(sentence)  # 把這句加入current_chunk
                current_length += len(sentence)  # 把這句的字數加入總長度
                i += 1
                continue

            else:  # 如果還是超過的話
                if current_chunk:  # 如果current_chunk不是空的
                    chunks.append(" ".join(current_chunk))  # 把current_chunk加入chunks裡
                current_chunk = [sentence]  # 全新的current_chunk加入這句
                current_length = len(sentence)  # 把這句的字數設為總長度
                i += 1
                continue

        else:  # 句子不是用#開頭 且字數沒有超過上限
            current_chunk.append(sentence)  # 把這句加入current_chunk
            current_length += len(sentence)  # 把這句的字數加入總長度
            i += 1  # 換下一句
    if current_chunk:  # 如果current_chunk不是空的
        chunks.append(" ".join(current_chunk))  # 保存跑完全部後的最後一個current_chunk
    return chunks

def embedding(question, text):
    if text == "error!": return "error!"
    question = question[1:]
    utils.set_marker()
    print("Chunking...")
    letters = 300
    chunks = chunk_by_sentence(text, letters, 2)
    allchunks = [question] + chunks
    while len(allchunks) > 100 and letters <= 700:
        letters += 100
        chunks = chunk_by_sentence(text, letters, 2)
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