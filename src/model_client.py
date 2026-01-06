from google.genai import Client
from cohere import ClientV2
from src import response_handler
from src import generate_handler
from src import file_handler
from src import utils
import time

gemini_client = None
cohere_client = None

gemini_messages = []
command_messages = []
merged_messages = []
gemini_parts = []
gemini_response = ""
command_response = ""
merged_response = ""
gemini_cot = ""
gemini_thought = False
command_thought = False
gemini_end_thinking = None
command_end_thinking = None
gemini_merge_end_thinking = None
gemini_start_generating = None
command_start_generating = None
gemini_start_merging = None
gemini_end_generating = None
command_end_generating = None
gemini_end_merging = None
gemini_model = ""
command_model = ""
gemini_merge_model = ""
embed_model = ""
rerank_model = ""

def initialize_gemini():
    global gemini_client
    while not gemini_client:
        utils.clear_all()
        try:
            key = input("Enter Gemini API Key: ").strip()
            if key == "":  # empty input check
                continue
            else:
                print("Checking if the key is valid...")
                gemini_client = Client(api_key=key)
                gemini_client.models.list()
        except: gemini_client = None  # KeyboardInterrupt check

def initialize_cohere():
    global cohere_client
    while not cohere_client:
        utils.clear_all()
        try:
            key = input("Enter Cohere API Key: ").strip()
            if key == "":  # empty input check
                continue
            else:
                print("Checking if the key is valid...")
                cohere_client = ClientV2(api_key=key)
                cohere_client.models.list()
        except Exception as e: cohere_client = None  # KeyboardInterrupt check

def ask_gemini(question):
    global gemini_cot, gemini_thought, gemini_model
    gemini_cot = ""
    gemini_thought = False
    # for some reason, Gemini 2.0 is called 2.0, Gemini 3 is called 3???????
    try:  # Gemini 3 Pro, it doesn't support NO reasoning
        if response_handler.spreadsheet: raise utils.Error("Skipping Gemini 3 for TAG")
        # for some reason, at least for this project,
        # Gemini 3 tweaks when you tryna function call,
        # VERY LIKELY caused by thought signature,
        # since its REQUIRED (not optional) for function calling in Gemini 3
        # but all the fixes i tried, doesnt work, somehow
        if question[0] == "@":  # Reasoning
            gemini_model = "Gemini 3 Pro"
            generate_handler.gemini_generate("gemini-3-pro-preview", True)
        else:  # No reasoning
            gemini_model = "Gemini 3 Flash"
            generate_handler.gemini_generate("gemini-3-flash-preview", False)
    except:
        if not gemini_thought:
            try:  # Gemini 3 Flash, fallback if Pro is not available
                if response_handler.spreadsheet: raise utils.Error("Skipping Gemini 3 for TAG")
                gemini_model = "Gemini 3 Flash"
                if question[0] == "@":  # Reasoning
                    generate_handler.gemini_generate("gemini-3-flash-preview", True)
                else:  # No reasoning
                    generate_handler.gemini_generate("gemini-3-flash-preview", False)
            except:
                if not gemini_thought:
                    try:  # Gemini 2.5 Pro, it doesn't support NO reasoning
                        if question[0] == "@":  # Reasoning
                            gemini_model = "Gemini 2.5 Pro"
                            generate_handler.gemini_generate("gemini-2.5-pro", True)
                        else:  # No reasoning
                            gemini_model = "Gemini 2.5 Flash"
                            generate_handler.gemini_generate("gemini-2.5-flash", False)
                    except:
                        if not gemini_thought:
                            try:  # Gemini 2.5 Flash, fallback if Pro is not available
                                gemini_model = "Gemini 2.5 Flash"
                                if question[0] == "@":  # Reasoning
                                    generate_handler.gemini_generate("gemini-2.5-flash", True)
                                else:  # No reasoning
                                    generate_handler.gemini_generate("gemini-2.5-flash", False)
                            except:
                                if not gemini_thought:
                                    try:  # Gemini 2.5 Flash Lite, fallback if Flash is not available
                                        gemini_model = "Gemini 2.5 Flash Lite"
                                        if question[0] == "@":  # Reasoning
                                            generate_handler.gemini_generate("gemini-2.5-flash-lite", True)
                                        else:  # No reasoning
                                            generate_handler.gemini_generate("gemini-2.5-flash-lite", False)
                                    except:
                                        if not gemini_thought:
                                            try:  # Gemini 2.0 Flash, fallback if 2.5 is not available
                                                gemini_model = "Gemini 2.0 Flash"
                                                if question[0] == "@":  # Reasoning
                                                    generate_handler.gemini_generate("gemini-2.0-flash", True)
                                                else:  # No reasoning
                                                    generate_handler.gemini_generate("gemini-2.0-flash", False)
                                            except:
                                                if not gemini_thought:
                                                    try:  # Gemini 2.0 Flash Lite, fallback if Flash is not available, doesn't support reasoning
                                                        gemini_model = "Gemini 2.0 Flash Lite"
                                                        generate_handler.gemini_generate("gemini-2.0-flash-lite", False)
                                                    except Exception as e: print(f'Gemini API Key invalid / An error occurred: {e}')

def ask_command(question):
    global command_response, command_thought, command_model
    command_thought = False
    command_response = ""
    try:  # Command A
        if question[0] == "@":  # Reasoning
            command_model = "Command A Reasoning"
            generate_handler.command_generate("command-a-reasoning-08-2025", "enabled")
        else:  # No reasoning
            if file_handler.command_image:
                command_model = "Command A Vision"
                generate_handler.command_generate("command-a-vision-07-2025", "disabled")
            else:
                command_model = "Command A"
                generate_handler.command_generate("command-a-03-2025", "disabled")
    except:
        if not command_thought:
            try:  # Command R+, fallback if A is not available, doesn't support reasoning and image reading
                command_model = "Command R+"
                generate_handler.command_generate("command-r-plus-08-2024", "disabled")
            except:
                if not command_thought:
                    try:  # Command R, fallback if R+ is not available, doesn't support reasoning
                        command_model = "Command R"
                        generate_handler.command_generate("command-r-08-2024", "disabled")
                    except Exception as e: print(f'Cohere API Key invalid / An error occurred: {e}')

def merge_responses(question):
    global merged_messages, gemini_start_merging, gemini_merge_model
    gemini_start_merging = time.perf_counter()
    merged_messages = [{"role": "user", "parts": [{"text": question}]}]
    try:  # Gemini 3 Pro, it doesn't support NO reasoning
        if question[0] == "@":  # Reasoning
            gemini_merge_model = "Gemini 3 Pro"
            generate_handler.gemini_merge("gemini-3-pro-preview", True)
        else:  # No reasoning
            gemini_merge_model = "Gemini 3 Flash"
            generate_handler.gemini_merge("gemini-3-flash-preview", False)
        utils.clear_all()
    except:
        try:  # Gemini 3 Flash, fallback if Pro is not available
            gemini_merge_model = "Gemini 3 Flash"
            if question[0] == "@":  # Reasoning
                generate_handler.gemini_merge("gemini-3-flash-preview", True)
            else:  # No reasoning
                generate_handler.gemini_merge("gemini-3-flash-preview", False)
            utils.clear_all()
        except:
            try:  # Gemini 2.5 Pro, it doesn't support NO reasoning
                if question[0] == "@":  # Reasoning
                    gemini_merge_model = "Gemini 2.5 Pro"
                    generate_handler.gemini_merge("gemini-2.5-pro", True)
                else:  # No reasoning
                    gemini_merge_model = "Gemini 2.5 Flash"
                    generate_handler.gemini_merge("gemini-2.5-flash", False)
                utils.clear_all()
            except:
                try:  # Gemini 2.5 Flash, fallback if Pro is not available
                    gemini_merge_model = "Gemini 2.5 Flash"
                    if question[0] == "@":  # Reasoning
                        generate_handler.gemini_merge("gemini-2.5-flash", True)
                    else:  # No reasoning
                        generate_handler.gemini_merge("gemini-2.5-flash", False)
                    utils.clear_all()
                except:
                    try:  # Gemini 2.5 Flash Lite, fallback if Flash is not available
                        gemini_merge_model = "Gemini 2.5 Flash Lite"
                        if question[0] == "@":  # Reasoning
                            generate_handler.gemini_merge("gemini-2.5-flash-lite", True)
                        else:  # No reasoning
                            generate_handler.gemini_merge("gemini-2.5-flash-lite", False)
                        utils.clear_all()
                    except:
                        try:  # Gemini 2.0 Flash, fallback if 2.5 is not available
                            gemini_merge_model = "Gemini 2.0 Flash"
                            if question[0] == "@":  # Reasoning
                                generate_handler.gemini_generate("gemini-2.0-flash", True)
                            else:  # No reasoning
                                generate_handler.gemini_generate("gemini-2.0-flash", False)
                        except:
                            try:  # Gemini 2.0 Flash Lite, fallback if Flash is not available, doesn't support reasoning
                                gemini_merge_model = "Gemini 2.0 Flash Lite"
                                generate_handler.gemini_generate("gemini-2.0-flash-lite", False)
                            except Exception as e: print(f'Gemini API Key invalid / An error occurred: {e}')