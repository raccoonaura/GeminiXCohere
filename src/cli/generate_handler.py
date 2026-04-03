from google.genai import types
from src.cli import spreadsheet_handler
from src.cli import response_handler
from src.cli import file_handler
from src.cli import model_client
from src.cli import utils
import time
import ast
import re

def gemini_generate(model, boolean=False):
    utils.set_marker()
    model_client.gemini_parts = []
    if model.startswith("gemini-3"):
        if response_handler.context:
            config = types.GenerateContentConfig(
                thinking_config = types.ThinkingConfig(
                    thinking_level = "high" if boolean else "medium",
                    # 3.1 Pro supports "high", "medium", "low"
                    # 3 Flash and Flash Lite supports "high", "medium", "low", "minimal"
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
        if response_handler.context:
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
                    # UPDATE UPDATE: we p2w nowadays
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

    for chunk in model_client.gemini_client.models.generate_content_stream(
        model = model,
        contents = model_client.gemini_messages,
        config = config
    ):
        for part in chunk.candidates[0].content.parts:
            model_client.gemini_parts.append(part)
            if not part.text:
                continue
            elif part.thought:
                print(part.text)
                model_client.gemini_cot += part.text
            else:
                if model_client.gemini_thought is False:
                    if boolean:
                        utils.clear_screen()
                    model_client.gemini_thought = True
                    model_client.gemini_end_thinking = f"{time.perf_counter() - response_handler.thought_start:.3f}"
                    model_client.gemini_start_generating = time.perf_counter()
                print(part.text, end="")  # Real-time printing since the merged response can take a while
                model_client.gemini_response += part.text
    model_client.gemini_end_generating = f"{time.perf_counter() - model_client.gemini_start_generating:.3f}"
    print ("\n\n-------------------------\n")

def mistral_generate(model, boolean=False):
    if boolean and model=="mistral-small-2603":
        if response_handler.context:
            res = model_client.mistral_client.chat.stream(
                model = model,
                messages = model_client.mistral_messages + [{"role": "system", "content": response_handler.context}],
                reasoning_effort="high"
            )
        else:
            res = model_client.mistral_client.chat.stream(
                model = model,
                messages = model_client.mistral_messages,
                reasoning_effort="high"
            )
    else:
        if response_handler.context:
            res = model_client.mistral_client.chat.stream(
                model = model,
                messages = model_client.mistral_messages + [{"role": "system", "content": response_handler.context}]
            )
        else:
            res = model_client.mistral_client.chat.stream(
                model = model,
                messages = model_client.mistral_messages
            )

    for chunk in res:
        match = None
        if isinstance(chunk.data.choices[0].delta.content, str):  # cot returns str or list
            if "thinking=[]" in chunk.data.choices[0].delta.content:  # sometimes returns empty for some reason
                continue
            if re.search(r"text='([^']*)'", chunk.data.choices[0].delta.content):  # it switches between ' and "
                match = re.search(r"text='([^']*)'", chunk.data.choices[0].delta.content)
            elif re.search(r'text="([^"]*)"', chunk.data.choices[0].delta.content):
                match = re.search(r'text="([^"]*)"', chunk.data.choices[0].delta.content)
        elif isinstance(chunk.data.choices[0].delta.content, list):
            if "thinking=[]" in str(chunk.data.choices[0].delta.content[0]):
                continue
            if re.search(r"text='([^']*)'", str(chunk.data.choices[0].delta.content[0])):
                match = re.search(r"text='([^']*)'", str(chunk.data.choices[0].delta.content[0]))
            elif re.search(r'text="([^"]*)"', str(chunk.data.choices[0].delta.content[0])):
                match = re.search(r'text="([^"]*)"', str(chunk.data.choices[0].delta.content[0]))
        if match:
            if file_handler.skip_gemini:
                print(ast.literal_eval(f"'''{match.group(1)}'''"), end="")
            model_client.mistral_cot += ast.literal_eval(f"'''{match.group(1)}'''")  # literal bulletproof (probably)
        else:
            if model_client.mistral_thought is False:
                if file_handler.skip_gemini:
                    utils.clear_all
                model_client.mistral_thought = True
                model_client.mistral_end_thinking = f"{time.perf_counter() - response_handler.thought_start:.3f}"
                model_client.mistral_start_generating = time.perf_counter()
            if file_handler.skip_gemini:
                print(chunk.data.choices[0].delta.content, end="")
            model_client.mistral_response += chunk.data.choices[0].delta.content
    model_client.mistral_end_generating = f"{time.perf_counter() - model_client.mistral_start_generating:.3f}"
    if file_handler.skip_gemini:
        print ("\n\n-------------------------\n")

def command_generate(model, value="disabled"):
    if response_handler.context:
        res = model_client.cohere_client.chat_stream(
            model = model,
            messages = model_client.command_messages + [{"role": "system", "content": response_handler.context}],
            thinking = {"type": value},
        )
    else:
        res = model_client.cohere_client.chat_stream(
            model = model,
            messages = model_client.command_messages,
            thinking = {"type": value},
        )
    for event in res:
        if event.type == "content-delta":
            if event.delta.message.content.thinking:
                # print(event.delta.message.content.thinking, end = "")
                model_client.command_cot += event.delta.message.content.thinking
            elif event.delta.message.content.text:
                if model_client.command_thought is False:
                    model_client.command_thought = True
                    model_client.command_end_thinking = f"{time.perf_counter() - response_handler.thought_start:.3f}"
                    model_client.command_start_generating = time.perf_counter()
                # print(event.delta.message.content.text, end = "")
                model_client.command_response += event.delta.message.content.text
    model_client.command_end_generating = f"{time.perf_counter() - model_client.command_start_generating:.3f}"

def gemini_merge(model, boolean):
    instruction = f"""
You're a helpful assistant for merging three model's responses
Merge all responses into one comprehensive answer
1. Use response 1 as the foundation
2. Integrate unique points from the other responses
3. Add relevant insights these three responses missed
4. Do not include any preamble, headers, or concluding remarks
5. Start the response immediately with the integrated content

Response 1:
{model_client.gemini_response}

Response 2:
{model_client.mistral_response}

Response 3:
{model_client.command_response}

{response_handler.context}
""" if file_handler.skip_mistral_n_command else f"""
You're a helpful assistant for merging two model's responses
Merge both responses into one comprehensive answer
1. Use response 1 as the foundation
2. Integrate unique points from the other response
3. Add relevant insights both responses missed
4. Do not include any preamble, headers, or concluding remarks
5. Start the response immediately with the integrated content

Response 1:
{model_client.mistral_response}

Response 2:
{model_client.command_response}

{response_handler.context}
"""
    if model.startswith("gemini-3"):
        config = types.GenerateContentConfig(
            thinking_config = types.ThinkingConfig(thinking_level = "high" if boolean else "medium"),
            system_instruction = instruction
        )
    else:
        config = types.GenerateContentConfig(
            thinking_config = types.ThinkingConfig(thinking_budget=-1 if boolean else 0),
            system_instruction = instruction
        )
    response = model_client.gemini_client.models.generate_content(
        model = model,
        contents = model_client.merged_messages,
        config = config,
    )
    model_client.gemini_merge_end_thinking = f"{time.perf_counter() - response_handler.thought_start:.3f}"
    model_client.gemini_end_merging = f"{time.perf_counter() - model_client.gemini_start_merging:.3f}"
    model_client.merged_part = response
    model_client.merged_response = response.text