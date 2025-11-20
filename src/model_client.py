from google.genai import Client
from cohere import ClientV2
from src import response_handler
from src import generate_handler
from src import file_handler
from src import utils
import time

client = None  # Gemini client
co = None  # Cohere client
# vs code kept asking me to add the previous two lines (WHY) even tho the whole thing works without them

gemini_messages = []
command_messages = []
merged_messages = []
full_response = []
gemini_response = ""
command_response = ""
merged_response = ""
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
    global client
    while not client:
        utils.clear_all()
        try:
            key = input("Enter Gemini API Key: ").strip()
            if key == "":  # empty input check
                continue
            else:
                client = Client(api_key=key)
        except: client = None  # KeyboardInterrupt check

def initialize_cohere():
    global co
    while not co:
        utils.clear_all()
        try:
            key = input("Enter Cohere API Key: ").strip()
            if key == "":  # empty input check
                continue
            else:
                co = ClientV2(api_key=key)
        except: co = None  # KeyboardInterrupt check

def ask_gemini(question):
    global gemini_messages, gemini_response, full_response, gemini_thought, gemini_end_thinking, gemini_start_generating, gemini_end_generating, gemini_model
    gemini_thought = False
    full_response.clear()
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
                                    except Exception as e:
                                        if not gemini_thought: print("Gemini API Key invalid / An error occurred: ", e)
    gemini_response = ''.join(full_response)  # Join all chunks into a single string for logging and further processing
    gemini_end_generating = f"{time.perf_counter() - gemini_start_generating:.3f}"
    print ("\n\n-------------------------\n")

def ask_command(question):
    global command_messages, command_response, command_thought, command_end_thinking, command_start_generating, command_end_generating, command_model
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
                    except Exception as e:
                        print("Cohere API Key invalid / An error occurred: ", e)
    command_end_generating = f"{time.perf_counter() - command_start_generating:.3f}"
    if file_handler.skip_gemini: print ("\n\n-------------------------\n")

def merge_responses(question):
    global gemini_response, command_response, merged_messages, merged_response, gemini_merge_end_thinking, gemini_start_merging, gemini_end_merging, gemini_merge_model, error
    gemini_start_merging = time.perf_counter()
    merged_messages = [{"role": "user", "parts": [{"text": question}]}]

    try:  # Gemini 2.5 Pro, it doesn't support NO reasoning
        if question[0] == "@":  # Reasoning
            gemini_merge_model = "Gemini 2.5 Pro"
            response = generate_handler.gemini_merge("gemini-2.5-pro", True)
        else:  # No reasoning
            gemini_merge_model = "Gemini 2.5 Flash"
            response = generate_handler.gemini_merge("gemini-2.5-flash", False)
        utils.clear_all()
    except:
        try:  # Gemini 2.5 Flash, fallback if Pro is not available
            gemini_merge_model = "Gemini 2.5 Flash"
            if question[0] == "@":  # Reasoning
                response = generate_handler.gemini_merge("gemini-2.5-flash", True)
            else:  # No reasoning
                response = generate_handler.gemini_merge("gemini-2.5-flash", False)
            utils.clear_all()
        except:
            try:  # Gemini 2.5 Flash Lite, fallback if Flash is not available
                gemini_merge_model = "Gemini 2.5 Flash Lite"
                if question[0] == "@":  # Reasoning
                    response = generate_handler.gemini_merge("gemini-2.5-flash-lite", True)
                else:  # No reasoning
                    response = generate_handler.gemini_merge("gemini-2.5-flash-lite", False)
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
                    except Exception as e:
                        print("Gemini API Key invalid / An error occurred: ", e)
    gemini_merge_end_thinking = f"{time.perf_counter() - response_handler.thought_start:.3f}"
    gemini_end_merging = f"{time.perf_counter() - gemini_start_merging:.3f}"
    merged_response = response.text