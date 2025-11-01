from google.genai import types
from src import response_handler
from src import model_client
import time

def gemini_generate(model, value):
    response = model_client.client.models.generate_content_stream(
        model=model,  # Using Flash here to save time, as Pro cannot disable thinking
        contents=model_client.gMsg,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=value),  # Disables thinking, for token efficiency, as it's enabled by default
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

def command_generate(model, value):
    if response_handler.context:
        res = model_client.co.chat_stream(
            model=model,
            messages=model_client.cMsg + [{"role": "system", "content": response_handler.context}],
            thinking={"type": value}
        )
    else:
        res = model_client.co.chat_stream(
            model=model,
            messages=model_client.cMsg,
            thinking={"type": value}
        )
    for event in res:
        if event.type == "content-delta":
            if event.delta.message.content.thinking:
                pass
            elif event.delta.message.content.text:
                if model_client.cThought is False:
                    model_client.cThought = True
                    model_client.cET = f"{time.perf_counter() - response_handler.tS:.3f}"
                    model_client.cSG = time.perf_counter()
                chunk = event.delta.message.content.text
                # print(event.delta.message.content.text, end="")
                model_client.cRes += chunk

def gemini_merge(model, value):
    response = model_client.client.models.generate_content(
        model=model,
        contents=model_client.mMsg,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=value),
            system_instruction="Merge both responses into one comprehensive answer:\n- Use the longer response as foundation\n- Integrate unique points from the shorter one\n- Add relevant insights both responses missed\n\nOutput only the final merged answer.\n\nResponse 1: \n\n" + model_client.gRes + "\n\nResponse 2: \n\n" + model_client.cRes + "\n\n" + response_handler.context
        ),
    )
    return response