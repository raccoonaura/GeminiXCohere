from google.genai import types
import gradio as gr
import time

def gemini_generate(model, boolean, state):
    gr.Info("".join(["check", "point", " ", "one"]))
    gemini_parts = []
    full_thought = []
    full_response = []
    if model == "gemini-3.0-pro" or model == "gemini-3.0-flash":
        config = types.GenerateContentConfig(
            thinking_config = types.ThinkingConfig(
                thinking_level = "high" if boolean else "medium",
                include_thoughts = boolean
            )
        )
    else:
        config = types.GenerateContentConfig(
            thinking_config = types.ThinkingConfig(
                thinking_budget = -1 if boolean else 0,
                include_thoughts = boolean
            )
        )
    gr.Info("".join(["check", "point", " ", "two"]))

    for chunk in state["gemini_client"].models.generate_content_stream(
        model = model,
        contents = state["gemini_messages"],
        config = config
    ):
        for part in chunk.candidates[0].content.parts:
            gr.Info("".join(["check", "point", " ", "two-1"]))
            gemini_parts.append(part)
            gr.Info("".join(["check", "point", " ", "two-2"]))
            if not part.text:
                continue
            elif part.thought:
                if boolean:
                    full_thought.append(part.text)
                    yield (gr.update(), gr.update(), gr.update(), state, gr.update(value = "\n".join(full_thought)), gr.update(), gr.update())
            else:
                if not state["gemini_start"]:
                    gr.Info("".join(["check", "point", " ", "three"]))
                    # if boolean: utils.clear_screen()
                    state["gemini_start"] = True
                    state["gemini_end_thinking"] = f"{time.perf_counter() - state["thought_start"]:.3f}"
                    state["gemini_start_generating"] = time.perf_counter()
                    gr.Info("".join(["check", "point", " ", "three-one"]))
                full_response.append(part.text)
                yield (gr.update(), gr.update(), gr.update(), state, gr.update(value = "".join(full_response)), gr.update(), gr.update())
    gr.Info("".join(["check", "point", " ", "four"]))
    state["gemini_cot"] = '\n'.join(full_thought)
    state["gemini_response"] = ''.join(full_response)
    state["gemini_end_generating"] = f"{time.perf_counter() - state["gemini_start_generating"]:.3f}"
    state["gemini_end"] = True
    return (gr.update(), gr.update(), gr.update(), state, gr.update(), gr.update(), gr.update())

def command_generate(model, value, state):
    # if state["context"]:
    #     res = state["cohere_client"].chat_stream(
    #         model = model,
    #         messages = state["command_messages"] + [{"role": "system", "content": state["context"]}],
    #         thinking = {"type": value},
    #     )
    # else:
    gr.Info("".join(["check", "point", " ", "five"]))
    full_thought = []
    full_response = []
    res = state["cohere_client"].chat_stream(
        model = model,
        messages = state["command_messages"],
        thinking = {"type": value},
    )
    gr.Info("".join(["check", "point", " ", "six"]))
    for event in res:
        if event.type == "content-delta":
            if event.delta.message.content.thinking:
                full_thought.append(event.delta.message.content.thinking)
                yield (gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), state, gr.update(value = "\n".join(full_thought)))
            elif event.delta.message.content.text:
                if not state["command_start"]:
                    gr.Info("".join(["check", "point", " ", "seven"]))
                    state["command_start"] = True
                    state["command_end_thinking"] = f"{time.perf_counter() - state["thought_start"]:.3f}"
                    state["command_start_generating"] = time.perf_counter()
                    gr.Info("".join(["check", "point", " ", "seven-one"]))
                full_response.append(event.delta.message.content.text)
                gr.Info("".join(full_response), 1)
                yield (gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), state, gr.update(value = "".join(full_response)))
    gr.Info("".join(["check", "point", " ", "eight"]))
    state["command_response"] = "".join(full_response)
    state["command_end_generating"] = f"{time.perf_counter() - state["command_start_generating"]:.3f}"
    state["command_end"] = True
    return (gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), state, gr.update())

# def gemini_merge(model, boolean, state):
#     instruction = f"""
# You're a helpful assistant for merging two LLM's responses
# Merge both responses into one comprehensive answer
# 1. Use the longer response as foundation
# 2. Integrate unique points from the shorter one
# 3. Add relevant insights both responses missed
# 4. Do not include any preamble, headers, or concluding remarks
# 5. Start the response immediately with the integrated content

# Response 1:
# {state["gemini_response"]}

# Response 2:
# {state["command_response"]}

# {state["context"]}
# """
#     if model == "gemini-3.0-pro" or model == "gemini-3.0-flash":
#         config = types.GenerateContentConfig(
#                     thinking_level = "high" if boolean else "medium",
#                     system_instruction = instruction
#         )
#     else:
#         config = types.GenerateContentConfig(
#                     thinking_config = types.ThinkingConfig(thinking_budget=-1 if boolean else 0),
#                     system_instruction = instruction
#         )
#     response = state["gemini_client"].models.generate_content(
#         model = model,
#         contents = state["merged_messages"],
#         config = config,
#     )
#     state["gemini_merge_end_thinking"] = f"{time.perf_counter() - state["thought_start"]:.3f}"
#     state["gemini_end_merging"] = f"{time.perf_counter() - state["gemini_start_merging"]:.3f}"
#     state["merged_part"] = response
#     state["merged_response"] = response.text
#     return state