from google.genai import types
from src import spreadsheet_handler
from src import response_handler
from src import file_handler
from src import model_client
from src import utils
import time

def gemini_generate(model, boolean):
    utils.set_marker()
    model_client.gemini_parts = []
    full_response = []
    full_thought = []
    if model == "gemini-3.0-pro" or model == "gemini-3.0-flash":
        if response_handler.spreadsheet:
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
                system_instruction = response_handler.context,
                tools = [spreadsheet_handler.sql_query]
            )
        else:
            config = types.GenerateContentConfig(
                thinking_config = types.ThinkingConfig(
                    thinking_level = "high" if boolean else "medium",
                    include_thoughts = boolean
                )
            )
    else:
        if response_handler.spreadsheet:
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
                system_instruction = response_handler.context,
                tools = [spreadsheet_handler.sql_query]
            )
        else:
            config = types.GenerateContentConfig(
                thinking_config = types.ThinkingConfig(
                    thinking_budget = -1 if boolean else 0,
                    include_thoughts = boolean
                )
            )

    for chunk in model_client.client.models.generate_content_stream(
        model = model,
        contents = model_client.gemini_messages,
        config = config
    ):
        for part in chunk.candidates[0].content.parts:
            model_client.gemini_parts.append(part)
            if not part.text:
                continue
            elif part.thought:
                if boolean:
                    utils.clear_screen()
                    print(part.text)
                    full_thought.append(part.text)
            else:
                if model_client.gemini_thought is False:
                    if boolean: utils.clear_screen()
                    model_client.gemini_thought = True
                    model_client.gemini_end_thinking = f"{time.perf_counter() - response_handler.thought_start:.3f}"
                    model_client.gemini_start_generating = time.perf_counter()
                print(part.text, end="")  # Real-time printing since the merged response can take a while
                full_response.append(part.text)
    model_client.gemini_cot = '\n'.join(full_thought)
    model_client.gemini_response = ''.join(full_response)  # Join all chunks into a single string for logging and further processing
    model_client.gemini_end_generating = f"{time.perf_counter() - model_client.gemini_start_generating:.3f}"
    print ("\n\n-------------------------\n")

def command_generate(model, value):
    if response_handler.context:
        res = model_client.co.chat_stream(
            model = model,
            messages = model_client.command_messages,# + [{"role": "system", "content": response_handler.context}],
            thinking = {"type": value},
        )
    else:
        res = model_client.co.chat_stream(
            model = model,
            messages = model_client.command_messages,
            thinking = {"type": value},
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
    model_client.command_end_generating = f"{time.perf_counter() - model_client.command_start_generating:.3f}"
    if file_handler.skip_gemini: print ("\n\n-------------------------\n")

def gemini_merge(model, boolean):
    instruction = f"""
You're a helpful assistant for merging two LLM's responses
Merge both responses into one comprehensive answer
1. Use the longer response as foundation
2. Integrate unique points from the shorter one
3. Add relevant insights both responses missed
4. Do not include any preamble, headers, or concluding remarks
5. Start the response immediately with the integrated content

Response 1:
{model_client.gemini_response}

Response 2:
{model_client.command_response}

{response_handler.context}
"""
    if model == "gemini-3.0-pro" or model == "gemini-3.0-flash":
        config = types.GenerateContentConfig(
                    thinking_level = "high" if boolean else "medium",
                    system_instruction = instruction
        )
    else:
        config = types.GenerateContentConfig(
                    thinking_config = types.ThinkingConfig(thinking_budget=-1 if boolean else 0),
                    system_instruction = instruction
        )
    response = model_client.client.models.generate_content(
        model = model,
        contents = model_client.merged_messages,
        config = config,
    )
    model_client.gemini_merge_end_thinking = f"{time.perf_counter() - response_handler.thought_start:.3f}"
    model_client.gemini_end_merging = f"{time.perf_counter() - model_client.gemini_start_merging:.3f}"
    model_client.merged_response = response.text