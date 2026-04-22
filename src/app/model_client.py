from google.genai import Client
from cohere import ClientV2
from src.app import generate_handler
import gradio as gr
import time

def initialize_gemini(gemini_key_input, state):
    try:
        if str(gemini_key_input).strip():
            key = str(gemini_key_input).strip()
        else:
            gr.Warning("Empty input detected!", 3)
            return (gr.update(value=""), gr.update(), gr.update(), gr.update(), state)
        gr.Info("Checking if the key is valid...", 3)
        state["gemini_client"] = Client(api_key=key)
        state["gemini_client"].models.list()
        gr.Info("Key is valid!", 3)
        return (gr.update(value="", visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=True), state)
    except Exception as e:
        state["gemini_client"] = None
        gr.Warning(f"Key is invalid! {e}", 3)
        return (gr.update(value=""), gr.update(), gr.update(), gr.update(), state)

def initialize_cohere(cohere_key_input, state):
    try:
        if str(cohere_key_input).strip():
            key = str(cohere_key_input).strip()
        else:
            gr.Warning("Empty input detected!", 3)
            return (gr.update(value=""), gr.update(), gr.update(), gr.update(), gr.update(), state, gr.update(), gr.update())
        gr.Info("Checking if the key is valid...", 3)
        state["cohere_client"] = ClientV2(api_key=key)
        state["cohere_client"].models.list()
        gr.Info("Key is valid!", 3)
        return (gr.update(value="", visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True), state, gr.update(visible=True), gr.update(visible=True))
    except Exception as e:
        state["cohere_client"] = None
        gr.Warning(f"Key is invalid! {e}", 3)
        return (gr.update(value=""), gr.update(), gr.update(), gr.update(), gr.update(), state, gr.update(), gr.update())
    
def choose_gemini_model(reasoning, state):
    state["gemini_cot"] = ""
    state["gemini_start"] = False
    state["gemini_end"] = False
    try:
        # if response_handler.spreadsheet: raise utils.Error("Skipping Gemini 3 for TAG")
        state["gemini_model"] = "Gemini 3 Pro" if reasoning else "Gemini 3 Flash"
        yield from generate_handler.gemini_generate("gemini-3-pro-preview", reasoning, state)
    except Exception as e:
        if state["gemini_start"]: return (gr.update(), gr.update(), gr.update(), state, gr.update(), gr.update(), gr.update())
        try:  # Gemini 3 Flash, fallback if Pro is not available
            # if response_handler.spreadsheet: raise utils.Error("Skipping Gemini 3 for TAG")
            state["gemini_model"] = "Gemini 3 Flash"
            yield from generate_handler.gemini_generate("gemini-3-flash-preview", reasoning, state)
        except Exception as e:
            if state["gemini_start"]: return (gr.update(), gr.update(), gr.update(), state, gr.update(), gr.update(), gr.update())
            try:  # Gemini 2.5 Pro, it doesn't support NO reasoning
                state["gemini_model"] = "Gemini 2.5 Pro" if reasoning else "Gemini 2.5 Flash"
                yield from generate_handler.gemini_generate("gemini-2.5-pro", reasoning, state)
            except Exception as e:
                if state["gemini_start"]: return (gr.update(), gr.update(), gr.update(), state, gr.update(), gr.update(), gr.update())
                try:  # Gemini 2.5 Flash, fallback if Pro is not available
                    state["gemini_model"] = "Gemini 2.5 Flash"
                    yield from generate_handler.gemini_generate("gemini-2.5-flash", reasoning, state)
                except Exception as e:
                    if state["gemini_start"]: return (gr.update(), gr.update(), gr.update(), state, gr.update(), gr.update(), gr.update())
                    try:  # Gemini 2.5 Flash Lite, fallback if Flash is not available
                        state["gemini_model"] = "Gemini 2.5 Flash Lite"
                        yield from generate_handler.gemini_generate("gemini-2.5-flash-lite", reasoning, state)
                    except Exception as e:
                        if state["gemini_start"]: return (gr.update(), gr.update(), gr.update(), state, gr.update(), gr.update(), gr.update())
                        try:  # Gemini 2.0 Flash, fallback if 2.5 is not available
                            state["gemini_model"] = "Gemini 2.0 Flash"
                            yield from generate_handler.gemini_generate("gemini-2.0-flash", reasoning, state)
                        except Exception as e:
                            if state["gemini_start"]: return (gr.update(), gr.update(), gr.update(), state, gr.update(), gr.update(), gr.update())
                            try:  # Gemini 2.0 Flash Lite, fallback if Flash is not available, doesn't support reasoning
                                state["gemini_model"] = "Gemini 2.0 Flash Lite"
                                yield from generate_handler.gemini_generate("gemini-2.0-flash-lite", False)
                            except Exception as e: gr.Warning(f"Gemini API Key invalid / An error occurred: {e}")
    if state["gemini_end"]: gr.Info(f"Gemini thought for {state["gemini_end_thinking"]} seconds.\nTook {state["gemini_end_generating"]} seconds to generate the answer.\nGenerated {len(state["gemini_response"])} tokens.\nUsing model {state["gemini_model"]}.")
    return (gr.update(), gr.update(), gr.update(), state, gr.update(), gr.update(), gr.update())

def choose_command_model(reasoning, state):
    state["command_cot"] = ""
    state["command_start"] = False
    state["command_end"] = False
    state["command_response"] = ""
    try:  # Command A
        state["command_model"] = "Command A Reasoning" if reasoning else "Command A"
        yield from generate_handler.command_generate("command-a-reasoning-08-2025" if reasoning else "command-a-03-2025", "enabled" if reasoning else "disabled", state)
        # state["command_model"] = "Command A Reasoning" if reasoning else ("Command A Vision" if file_handler.mistral_n_command_image else "Command A")
        # yield from generate_handler.command_generate("command-a-reasoning-08-2025" if reasoning else ("command-a-vision-07-2025" if file_handler.mistral_n_command_image else "command-a-03-2025"), "enabled" if reasoning else "disabled")
    except Exception as e:
        if state["command_start"]: return (gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), state, gr.update())
        try:  # Command R+, fallback if A is not available, doesn't support reasoning and image reading
            state["command_model"] = "Command R+"
            yield from generate_handler.command_generate("command-r-plus-08-2024", "disabled", state)
        except Exception as e:
            if state["command_start"]: return (gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), state, gr.update())
            try:  # Command R, fallback if R+ is not available, doesn't support reasoning
                state["command_model"] = "Command R"
                yield from generate_handler.command_generate("command-r-08-2024", "disabled",state)
            except Exception as e: gr.Warning(f"Cohere API Key invalid / An error occurred: {e}")
    if state["command_end"]: gr.Info(f"Command thought for {state["command_end_thinking"]} seconds.\nTook {state["command_end_generating"]} seconds to generate the answer.\nGenerated {len(state["command_response"])} tokens.\nUsing model {state["command_model"]}.")
    return (gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), state, gr.update())

# def choose_merge_model(question, reasoning, state):
#     state["gemini_start_merging"] = time.perf_counter()
#     state["merged_messages"] = [{"role": "user", "parts": [{"text": question}]}]
#     try:  # Gemini 3 Pro, it doesn't support NO reasoning
#         state["gemini_merge_model"] = "Gemini 3 Pro" if reasoning else "Gemini 3 Flash"
#         state = generate_handler.gemini_merge("gemini-3-pro-preview" if reasoning else "gemini-3-flash-preview", reasoning, state)
#     except Exception as e:
#         try:  # Gemini 3 Flash, fallback if Pro is not available
#             state["gemini_merge_model"] = "Gemini 3 Flash"
#             state = generate_handler.gemini_merge("gemini-3-flash-preview", reasoning, state)
#         except Exception as e:
#             try:  # Gemini 2.5 Pro, it doesn't support NO reasoning
#                 state["gemini_merge_model"] = "Gemini 2.5 Pro" if reasoning else "Gemini 2.5 Flash"
#                 state = generate_handler.gemini_merge("gemini-2.5-pro" if reasoning else "gemini-2.5-flash", reasoning, state)
#             except Exception as e:
#                 try:  # Gemini 2.5 Flash, fallback if Pro is not available
#                     state["gemini_merge_model"] = "Gemini 2.5 Flash"
#                     state = generate_handler.gemini_merge("gemini-2.5-flash", reasoning, state)
#                 except Exception as e:
#                     try:  # Gemini 2.5 Flash Lite, fallback if Flash is not available
#                         state["gemini_merge_model"] = "Gemini 2.5 Flash Lite"
#                         state = generate_handler.gemini_merge("gemini-2.5-flash-lite", reasoning, state)
#                     except Exception as e:
#                         try:  # Gemini 2.0 Flash, fallback if 2.5 is not available
#                             state["gemini_merge_model"] = "Gemini 2.0 Flash"
#                             state = generate_handler.gemini_generate("gemini-2.0-flash", reasoning, state)
#                         except Exception as e:
#                             try:  # Gemini 2.0 Flash Lite, fallback if Flash is not available, doesn't support reasoning
#                                 state["gemini_merge_model"] = "Gemini 2.0 Flash Lite"
#                                 state = generate_handler.gemini_generate("gemini-2.0-flash-lite", False)
#                             except Exception as e: gr.Warning(f'Gemini API Key invalid / An error occurred: {e}')
#     return state