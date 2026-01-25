from google.genai import Client
from cohere import ClientV2
import gradio as gr

def initialize_gemini(gemini_key_input, state):
    try:
        if str(gemini_key_input).strip(): key = str(gemini_key_input).strip()
        else:
            gr.Warning("Empty input detected!", 3)
            return (gr.update(value=""), gr.update(), gr.update(), gr.update(), state)
        gr.Info("Checking if the key is valid...", 3)
        state["gemini_client"] = Client(api_key=key)
        state["gemini_client"].models.list()
        gr.Info("Key is valid!", 3)
        return (gr.update(value="", visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=True), state)
    except:
        state["gemini_client"] = None
        gr.Warning("Key is invalid!", 3)
        return (gr.update(value=""), gr.update(), gr.update(), gr.update(), state)

def initialize_cohere(cohere_key_input, state):
    try:
        if str(cohere_key_input).strip(): key = str(cohere_key_input).strip()
        else:
            gr.Warning("Empty input detected!", 3)
            return (gr.update(value=""), gr.update(), state)
        gr.Info("Checking if the key is valid...", 3)
        state["cohere_client"] = ClientV2(api_key=key)
        state["cohere_client"].models.list()
        gr.Info("Key is valid!", 3)
        return (gr.update(value="", visible=False), gr.update(visible=False), state)
    except:
        state["cohere_client"] = None
        gr.Warning("Key is invalid!", 3)
        return (gr.update(value=""), gr.update(), state)