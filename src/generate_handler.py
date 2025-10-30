from google.genai import types
from src import model_client
from src import response_handler
import time

def gf_generate():
    response = model_client.client.models.generate_content_stream(
        model="gemini-2.5-flash",  # Using Flash here to save time, as Pro cannot disable thinking
        contents=model_client.gMsg,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disables thinking, for token efficiency, as it's enabled by default
            system_instruction=response_handler.context
        ),
    )
    for chunk in response:
        if chunk.text is None:
            continue
        else:
            if model_client.gThought is False:
                model_client.gThought = True
                model_client.gET = f"{time.perf_counter() - response_handler.tS:.3f}"
                model_client.gSG = time.perf_counter()
            print(chunk.text, end="")  # Real-time printing since the merged response can take a while
            model_client.fullR.append(chunk.text)

def gfl_generate():
    response = model_client.client.models.generate_content_stream(
        model="gemini-2.5-flash-lite",
        contents=model_client.gMsg,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disables thinking, for token efficiency, as it's enabled by default
            system_instruction=response_handler.context
        ),
    )
    for chunk in response:
        if chunk.text is None:
            continue
        else:
            if model_client.gThought is False:
                model_client.gThought = True
                model_client.gET = f"{time.perf_counter() - response_handler.tS:.3f}"
                model_client.gSG = time.perf_counter()
            print(chunk.text, end="")  # Real-time printing since the merged response can take a while
            model_client.fullR.append(chunk.text)

def ca_generate():
    res = model_client.co.chat_stream(
        model="command-a-03-2025",
        messages=model_client.cMsg + [{"role": "system", "content": response_handler.context}],
    )
    for event in res:
        if event:
            if event.type == "content-delta":
                if event.delta.message.content.text:
                    if model_client.cThought is False:
                        model_client.cThought = True
                        model_client.cET = f"{time.perf_counter() - response_handler.tS:.3f}"
                        model_client.cSG = time.perf_counter()
                    chunk = event.delta.message.content.text
                    # print(event.delta.message.content.text, end="")
                    model_client.cRes += chunk

def crp_generate():
    res = model_client.co.chat_stream(
        model="command-r-plus-08-2024",
           messages=model_client.cMsg + [{"role": "system", "content": response_handler.context}],
    )
    for event in res:
        if event:
            if event.type == "content-delta":
                if event.delta.message.content.text:
                    if model_client.cThought is False:
                        model_client.cThought = True
                        model_client.cET = f"{time.perf_counter() - response_handler.tS:.3f}"
                        model_client.cSG = time.perf_counter()
                    chunk = event.delta.message.content.text
                    # print(event.delta.message.content.text, end="")
                    model_client.cRes += chunk

def cr_generate():
    res = model_client.co.chat_stream(
        model="command-r-08-2024",
           messages=model_client.cMsg + [{"role": "system", "content": response_handler.context}],
    )
    for event in res:
        if event:
            if event.type == "content-delta":
                if event.delta.message.content.text:
                    if model_client.cThought is False:
                        model_client.cThought = True
                        model_client.cET = f"{time.perf_counter() - response_handler.tS:.3f}"
                        model_client.cSG = time.perf_counter()
                    chunk = event.delta.message.content.text
                    # print(event.delta.message.content.text, end="")
                    model_client.cRes += chunk

def gf_merge():
    response = model_client.client.models.generate_content(
        model="gemini-2.5-flash",
        contents=model_client.mMsg,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disables thinking, for token efficiency, as it's enabled by default
            system_instruction=response_handler.context
        ),
    )
    return response

def gfl_merge():
    response = model_client.client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=model_client.mMsg,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),  # Disables thinking, for token efficiency, as it's enabled by default
            system_instruction=response_handler.context
        ),
    )
    return response