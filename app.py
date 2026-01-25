from src.app import model_client
import gradio as gr

question = ""

with gr.Blocks() as interface:  # very early stage, WIP
    season_state = gr.State(value={
        "gemini_client": None,
        "cohere_client": None
    })
    gemini_key_input = gr.Textbox(value="", label="Enter Gemini API Key:")
    cohere_key_input = gr.Textbox(value="", label="Enter Cohere API Key:", visible=False, interactive=True)
    gemini_button = gr.Button("Confirm")
    cohere_button = gr.Button("Confirm", visible=False, interactive=True)
    gemini_button.click(
        fn=model_client.initialize_gemini,
        inputs=[gemini_key_input, season_state],
        outputs=[gemini_key_input, gemini_button, cohere_key_input, cohere_button, season_state]
    )
    cohere_button.click(
        fn=model_client.initialize_cohere,
        inputs=[cohere_key_input, season_state],
        outputs=[cohere_key_input, cohere_button, season_state]
    )

interface.launch()