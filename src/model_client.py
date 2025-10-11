from google.genai import Client
from cohere import ClientV2
from src import response_handler
from src import generate_handler
from src import reasoning_handler
import time

client = None  # Gemini client
co = None  # Cohere client
# vs code kept asking me to add the previous two lines (WHY) even tho the whole thing works without them

gMsg = []  # Stands for Gemini messages
cMsg = []  # Stands for Command messages
mMsg = []  # Stands for merged messages
fullR = []  # Stands for full response
gRes = ""  # Stands for Gemini response
cRes = ""  # Stands for Command response
mRes = ""  # Stands for merged response
gThought = False  # Stands for Gemini thought
cThought = False  # Stands for Command thought
gET = None  # Stands for Gemini End Thinking
cET = None  # Stands for Command End Thinking
mET = None  # Stands for Merged End Thinking
gSG = None  # Stands for Gemini Start Generating
cSG = None  # Stands for Command Start Generating
mSG = None  # Stands for Merged Start Generating
gEG = None  # Stands for Gemini End Generating
cEG = None  # Stands for Command End Generating
mEG = None  # Stands for Merged End Generating

def initialize_gemini():
    global client
    client = Client(api_key=input("Enter Gemini API Key: ").strip())

def initialize_cohere():
    global co
    co = ClientV2(api_key=input("Enter Cohere API Key: ").strip())

def memorize_question(question):
    gMsg.append({"role": "user", "parts": [{"text": question}]})
    cMsg.append({"role": "user", "content": question})

def memorize_response():
    gMsg.append({"role": "model", "parts": [{"text": mRes}]})
    cMsg.append({"role": "assistant", "content": mRes})

def ask_gemini(question):
    global gMsg, gRes, fullR, gThought, gET, gSG, gEG
    gThought = False
    fullR.clear()
    try:  # Gemini 2.5 Pro, it doesn't support NO reasoning
        if question[0] == "@":  # Reasoning
            reasoning_handler.gp_think()
        else:  # No reasoning
            generate_handler.gf_generate()
    except:
        try:  # Gemini 2.5 Flash, fallback if Pro is not available
            print ("Gemini 2.5 Pro is not available! Using Gemini 2.5 Flash\n")
            if question[0] == "@":  # Reasoning
                reasoning_handler.gf_think()
            else:  # No reasoning
                generate_handler.gf_generate()
        except:  # Gemini 2.5 Flash Lite, fallback if Flash is not available, although you'll barely reach this point
            try:
                print ("Gemini 2.5 Flash is not available! Using Gemini 2.5 Flash Lite\n")
                if question[0] == "@":  # Reasoning
                    reasoning_handler.gfl_think()
                else:  # No reasoning
                    generate_handler.gfl_generate()
            except Exception as e:  # Erm... you are probably doing something wrong!
                print("Gemini API Key無效或發生錯誤: ", e)
    gRes = ''.join(fullR)  # Join all chunks into a single string for logging and further processing
    gEG = f"{time.perf_counter() - gSG:.3f}"
    print ("\n\n----------\n")

def ask_command(question):
    global cMsg, cRes, cThought, cET, cSG, cEG
    cThought = False
    try:  # Command A
        if question[0] == "@":  # Reasoning
            generate_handler.ca_think()
        else:  # No reasoning
            generate_handler.ca_generate()
    except:  # Command R+, fallback if A is not available, it doesn't support reasoning
        try:
            generate_handler.crp_generate()
        except:  # Command R, fallback if R+ is not available, although you'll barely reach this point, it doesn't support reasoning
            try:
                generate_handler.cr_generate()
            except Exception as e:  # Erm... you are probably doing something wrong!
                print("Cohere API Key無效或發生錯誤: ", e)
    cEG = f"{time.perf_counter() - cSG:.3f}"

def merge_responses(question):
    global gRes, cRes, mMsg, mRes, mET, mSG, mEG
    mSG = time.perf_counter()
    mMsg = {"role": "user", "parts": [{"text": "You are given two responses to the same question. Merge them into a single, comprehensive answer that preserves most of the unique and valuable content from both. Expand upon the topic by adding relevant insights or perspectives the original responses may have missed. Output only the final merged answer without any explanations, notes, or meta commentary.\n\nQuestion: " + question + "\n\nResponse 1: " + gRes + "\n\nResponse 2: " + cRes}]}

    # Easier to read version
    """
    You are given two responses to the same question.
    Merge them into a single, comprehensive answer that preserves most of the unique and valuable content from both.
    Expand upon the topic by adding relevant insights or perspectives the original responses may have missed.
    Output only the final merged answer without any explanations, notes, or meta commentary.
    \n\nQuestion: " + question + "\n\nResponse 1: " + gRes + "\n\nResponse 2: " + cRes
    """
    # TODO: Find a better way to format this for Gemini

    try:  # Gemini 2.5 Pro, it doesn't support NO reasoning
        if question[0] == "@":  # Reasoning
            response = reasoning_handler.gp_think_merge()
        else:  # No reasoning
            response = generate_handler.gf_merge()
    except:  # Gemini 2.5 Flash, fallback if Pro is not available
        print("Gemini 2.5 Pro is not available! Using Gemini 2.5 Flash\n")
        try:
            if question[0] == "@":  # Reasoning
                response = reasoning_handler.gf_think_merge()
            else:  # No reasoning
                response = generate_handler.gf_merge()
        except:  # Gemini 2.5 Flash Lite, fallback if Flash is not available, although you'll barely reach this point
            print("Gemini 2.5 Flash is not available! Using Gemini 2.5 Flash Lite\n")
            try:
                response = generate_handler.gfl_merge()
            except Exception as e:  # Erm... you are probably doing something wrong!
                print("Gemini API Key無效或發生錯誤: ", e)
    mET = f"{time.perf_counter() - response_handler.tS:.3f}"
    mEG = f"{time.perf_counter() - mSG:.3f}"
    mRes = response.text