from src.app import response_handler
from src.app import model_client
import gradio as gr

question = ""

with gr.Blocks() as interface:  # very early stage, WIP
    gemini_state = gr.State(value={
        "gemini_client": None,
        "thought_start": None,
        "gemini_messages": [],
        "gemini_parts": [],
        "gemini_response": "",
        "gemini_cot": "",
        "gemini_start": False,
        "gemini_end": False,
        "gemini_end_thinking": None,
        "gemini_merge_end_thinking": None,
        "gemini_start_generating": None,
        "gemini_end_generating": None,
        "gemini_model": "",
    })
    cohere_state = gr.State(value={
        "cohere_client": None,
        "thought_start": None,
        "command_messages": [],
        "command_response": "",
        "command_cot": "",
        "command_start": False,
        "command_end": False,
        "command_end_thinking": None,
        "command_start_generating": None,
        "command_end_generating": None,
        "command_model": "",
    })
    with gr.Row():
        gemini_button = gr.Button("Confirm", scale=1)
        gemini_key_input = gr.Textbox(value="", label="Enter Gemini API Key:", scale=19)
    with gr.Row():
        cohere_button = gr.Button("Confirm", visible=False, interactive=True, scale=1)
        cohere_key_input = gr.Textbox(value="", label="Enter Cohere API Key:", visible=False, interactive=True, scale=19)
    with gr.Row():
        with gr.Column():
            reasoning_toggled = gr.Checkbox(label="Reasoning", visible=False, interactive=True, scale=1)
            send_button = gr.Button("Send", visible=False, interactive=True, scale=1)
        prompt_input = gr.Textbox(value="", label="Hello! How can I assist you today?", visible=False, interactive=True, scale=19)
    with gr.Row():
        gemini_textbox = gr.Textbox(value="", label="Gemini's answer:", visible=False, interactive=False)
        command_textbox = gr.Textbox(value="", label="Command's answer:", visible=False, interactive=False)
    gemini_button.click(
        fn=model_client.initialize_gemini,
        inputs=[gemini_key_input, gemini_state],
        outputs=[gemini_key_input, gemini_button, cohere_key_input, cohere_button, gemini_state]
    )
    cohere_button.click(
        fn=model_client.initialize_cohere,
        inputs=[cohere_key_input, cohere_state],
        outputs=[cohere_key_input, cohere_button, send_button, reasoning_toggled, prompt_input, cohere_state, gemini_textbox, command_textbox]
    )
    send_button.click(
        fn=response_handler.handle_conversation,
        inputs=[prompt_input, reasoning_toggled, gemini_state, cohere_state],
        outputs=[prompt_input, reasoning_toggled, send_button, gemini_state, gemini_textbox, cohere_state, command_textbox]
    )

interface.launch()

# heres everything that WILL be in both states and i put it here to make myself easier to copy and paste
#         "gemini_client": None,
#         "cohere_client": None,
#         "thought_start": None,
#         "image": [],
#         "document": [],
#         "spreadsheet": [],
#         "context": "",
#         "gemini_messages": [],
#         "command_messages": [],
#         "merged_messages": [],
#         "gemini_parts": [],
#         "merged_part": None,
#         "gemini_response": "",
#         "command_response": "",
#         "merged_response": "",
#         "gemini_cot": "",
#         "command_cot": "",
#         "gemini_start": False,
#         "command_start": False,
#         "gemini_end": False,
#         "command_end": False,
#         "gemini_end_thinking": None,
#         "command_end_thinking": None,
#         "gemini_merge_end_thinking": None,
#         "gemini_start_generating": None,
#         "command_start_generating": None,
#         "gemini_start_merging": None,
#         "gemini_end_generating": None,
#         "command_end_generating": None,
#         "gemini_end_merging": None,
#         "gemini_model": "",
#         "command_model": "",
#         "gemini_merge_model": "",
#         "embed_model": "",
#         "rerank_model": "",