from google.genai import types
from src import response_handler
from src import file_handler
from src import model_client
from src import utils
import time

def gemini_generate(model, boolean):
    utils.set_marker()
    if model == "gemini-3.0-pro" or model == "gemini-3.0-flash":
        config = types.GenerateContentConfig(
            thinking_config = types.ThinkingConfig(
                thinking_level = "high" if boolean else "medium",
                # 3.0 Pro supports "high", "low"
                # 3.0 Flash supports "high", "medium", "low", "minimal"
                # if thinking is true then "high", otherwise "medium"
                # this works (supposed to) even when Pro doesnt support medium
                # bcz Pro will only be used when thinking is enabled
                # so if boolean is false, its gotta be Flash, always will be
                # in that case, "medium" will work
                include_thoughts = boolean
            ),
            system_instruction = response_handler.context
        )
    else:
        config = types.GenerateContentConfig(
            thinking_config = types.ThinkingConfig(
                thinking_budget = -1 if boolean else 0,
                # somehow breaks 2.5 Pro?
                # UPDATE: i highly assume google is tweaking
                # 2.5 Pro is supposed to be free
                # (fact checked from their docs)
                # but im getting quota exceeded error
                # even tho i havent used 2.5 Pro in 2 weeks
                # and theres no usuage displaying
                # regarding 2.5 Pro in google ai studio
                include_thoughts = boolean
            ),
            system_instruction = response_handler.context
        )
    for chunk in model_client.client.models.generate_content_stream(
        model = model,
        contents = model_client.gemini_messages,
        config = config
    ):
        for part in chunk.candidates[0].content.parts:
            if not part.text:
                continue
            elif part.thought:
                if boolean:
                    utils.clear_screen()
                    print(part.text)
            else:
                if model_client.gemini_thought is False:
                    if boolean:
                        utils.clear_screen()
                    model_client.gemini_thought = True
                    model_client.gemini_end_thinking = f"{time.perf_counter() - response_handler.thought_start:.3f}"
                    model_client.gemini_start_generating = time.perf_counter()
                print(part.text, end="")  # Real-time printing since the merged response can take a while
                model_client.full_response.append(part.text)

def command_generate(model, value):
    if response_handler.context:
        res = model_client.co.chat_stream(
            model = model,
            messages = model_client.command_messages + [{"role": "system", "content": response_handler.context}],
            thinking = {"type": value}
        )
    else:
        res = model_client.co.chat_stream(
            model = model,
            messages = model_client.command_messages,
            thinking = {"type": value}
        )
    for event in res:
        if event.type == "content-delta":
            if event.delta.message.content.thinking and model_client.gemini_thought is False:
                # print(event.delta.message.content.thinking, end = "")
                pass
            elif event.delta.message.content.text:
                if model_client.command_thought is False:
                    model_client.command_thought = True
                    model_client.command_end_thinking = f"{time.perf_counter() - response_handler.thought_start:.3f}"
                    model_client.command_start_generating = time.perf_counter()
                chunk = event.delta.message.content.text
                if file_handler.skip_gemini:
                    print(event.delta.message.content.text, end = "")
                model_client.command_response += chunk

def gemini_merge(model, boolean):
    if model == "gemini-3.0-pro" or model == "gemini-3.0-flash":
        config = types.GenerateContentConfig(
                    thinking_level="high" if boolean else "medium",
                    system_instruction="Merge both responses into one comprehensive answer:\n- Use the longer response as foundation\n- Integrate unique points from the shorter one\n- Add relevant insights both responses missed\n\nOutput only the final merged answer.\n\nResponse 1: \n\n" + model_client.gemini_response + "\n\nResponse 2: \n\n" + model_client.command_response + "\n\n" + response_handler.context
                )
    else:
        config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=-1 if boolean else 0),
                    system_instruction="Merge both responses into one comprehensive answer:\n- Use the longer response as foundation\n- Integrate unique points from the shorter one\n- Add relevant insights both responses missed\n\nOutput only the final merged answer.\n\nResponse 1: \n\n" + model_client.gemini_response + "\n\nResponse 2: \n\n" + model_client.command_response + "\n\n" + response_handler.context
                )
    response = model_client.client.models.generate_content(
        model = model,
        contents = model_client.merged_messages,
        config = config,
    )
    return response