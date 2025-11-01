from google.genai import Client
from cohere import ClientV2
from src import response_handler
from src import generate_handler
from src import embedding_handler
from src import utils
import time

client = None  # Gemini client
co = None  # Cohere client
# vs code kept asking me to add the previous two lines (WHY) even tho the whole thing works without them

gMsg = []  # Stands for Gemini messages
cMsg = []  # Stands for Cohere messages
mMsg = []  # Stands for merged messages
fullR = []  # Stands for full response
gRes = ""  # Stands for Gemini response
cRes = ""  # Stands for Cohere response
mRes = ""  # Stands for merged response
gThought = False  # Stands for Gemini thought
cThought = False  # Stands for Cohere thought
gET = None  # Stands for Gemini End Thinking
cET = None  # Stands for Cohere End Thinking
mET = None  # Stands for Merged End Thinking
gSG = None  # Stands for Gemini Start Generating
cSG = None  # Stands for Cohere Start Generating
mSG = None  # Stands for Merged Start Generating
gEG = None  # Stands for Gemini End Generating
cEG = None  # Stands for Cohere End Generating
mEG = None  # Stands for Merged End Generating
gMd = ""  # Stands for Gemini Model
cMd = ""  # Stands for Cohere Model
mMd = ""  # Stands for Merged Model

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

def memorize_question(question):
    gMsg.append({"role": "user", "parts": [{"text": question}]})
    cMsg.append({"role": "user", "content": question})

def memorize_response():
    gMsg.append({"role": "model", "parts": [{"text": mRes}]})
    cMsg.append({"role": "assistant", "content": mRes})

def embedding(question):
    try:
        question = question[1:]
        context = embedding_handler.ge_embed(question)
        return context
    except:
        try:
            question = question[1:]
            embedding_handler.e4_embed()
        except:
            try:
                question = question[1:]
                embedding_handler.e3_embed()
            except:
                try:
                    question = question[1:]
                    embedding_handler.el3_embed()
                except Exception as e:  # Erm... you are probably doing something wrong!
                    print("An error occurred while embedding: ", e)

def ask_gemini(question):
    global gMsg, gRes, fullR, gThought, gET, gSG, gEG, gMd
    gThought = False
    fullR.clear()
    try:  # Gemini 2.5 Pro, it doesn't support NO reasoning
        if question[0] == "$": question = question[1:]  # File reading
        if question[0] == "@":  # Reasoning
            gMd = "Gemini 2.5 Pro"
            question = question[1:]
            generate_handler.gemini_generate("gemini-2.5-pro", -1)
        else:  # No reasoning
            gMd = "Gemini 2.5 Flash"
            generate_handler.gemini_generate("gemini-2.5-flash", 0)
    except:
        try:  # Gemini 2.5 Flash, fallback if Pro is not available
            gMd = "Gemini 2.5 Flash"
            if question[0] == "$": question = question[1:]  # File reading
            if question[0] == "@":  # Reasoning
                question = question[1:]
                generate_handler.gemini_generate("gemini-2.5-flash", -1)
            else:  # No reasoning
                generate_handler.gemini_generate("gemini-2.5-flash", 0)
        except:
            try:  # Gemini 2.5 Flash Lite, fallback if Flash is not available, although you'll barely reach this point
                gMd = "Gemini 2.5 Flash Lite"
                if question[0] == "$": question = question[1:]  # File reading
                if question[0] == "@":  # Reasoning
                    question = question[1:]
                    generate_handler.gemini_generate("gemini-2.5-flash-lite", -1)
                else:  # No reasoning
                    generate_handler.gemini_generate("gemini-2.5-flash-lite", 0)
            except Exception as e:  # Erm... you are probably doing something wrong!
                print("Gemini API Key invalid / An error occurred: ", e)
    gRes = ''.join(fullR)  # Join all chunks into a single string for logging and further processing
    gEG = f"{time.perf_counter() - gSG:.3f}"
    print ("\n\n-------------------------\n")

def ask_command(question):
    global cMsg, cRes, cThought, cET, cSG, cEG, cMd
    cThought = False
    cRes = ""
    try:  # Command A
        cMd = "Command A"
        if question[0] == "$": question = question[1:]  # File reading
        if question[0] == "@":  # Reasoning
            question = question[1:]
            generate_handler.command_generate("command-a-reasoning-08-2025", "enabled")
        else:  # No reasoning
            generate_handler.command_generate("command-a-03-2025", "disabled")
    except Exception as e:
        print(e)
        try:  # Command R+, fallback if A is not available, it doesn't support reasoning
            cMd = "Command R+"
            if question[0] == "$": question = question[1:]  # File reading
            question = question[1:]
            generate_handler.command_generate("command-r-plus-08-2024", "disabled")
        except:
            try:  # Command R, fallback if R+ is not available, although you'll barely reach this point, R doesn't support reasoning
                cMd = "Command R"
                if question[0] == "$": question = question[1:]  # File reading
                generate_handler.command_generate("command-r-08-2024", "disabled")
            except Exception as e:  # Erm... you are probably doing something wrong!
                print("Cohere API Key invalid / An error occurred: ", e)
    cEG = f"{time.perf_counter() - cSG:.3f}"

def merge_responses(question):
    global gRes, cRes, mMsg, mRes, mET, mSG, mEG, mMd
    mSG = time.perf_counter()
    mMsg = [{"role": "user", "parts": [{"text": question}]}]

    try:  # Gemini 2.5 Pro, it doesn't support NO reasoning
        if question[0] == "$": question = question[1:]  # File reading
        if question[0] == "@":  # Reasoning
            mMd = "Gemini 2.5 Pro"
            question = question[1:]
            response = generate_handler.gemini_merge("gemini-2.5-pro", -1)
        else:  # No reasoning
            mMd = "Gemini 2.5 Flash"
            response = generate_handler.gemini_merge("gemini-2.5-flash", 0)
    except:
        try:  # Gemini 2.5 Flash, fallback if Pro is not available
            if question[0] == "$": question = question[1:]  # File reading
            if question[0] == "@":  # Reasoning
                mMd = "Gemini 2.5 Flash"
                question = question[1:]
                response = generate_handler.gemini_merge("gemini-2.5-flash", -1)
            else:  # No reasoning
                mMd = "Gemini 2.5 Flash"
                response = generate_handler.gemini_merge("gemini-2.5-flash", 0)
        except:
            try:  # Gemini 2.5 Flash Lite, fallback if Flash is not available, although you'll barely reach this point
                if question[0] == "$": question = question[1:]  # File reading
                if question[0] == "@":  # Reasoning
                    mMd = "Gemini 2.5 Flash Lite"
                    question = question[1:]
                    response = generate_handler.gemini_merge("gemini-2.5-flash-lite", -1)
                else:  # No reasoning
                    mMd = "Gemini 2.5 Flash Lite"
                    response = generate_handler.gemini_merge("gemini-2.5-flash-lite", 0)
            except Exception as e:  # Erm... you are probably doing something wrong!
                print("Gemini API Key invalid / An error occurred: ", e)
    mET = f"{time.perf_counter() - response_handler.tS:.3f}"
    mEG = f"{time.perf_counter() - mSG:.3f}"
    mRes = response.text