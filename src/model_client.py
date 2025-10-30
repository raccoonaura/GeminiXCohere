from google.genai import Client
from cohere import ClientV2
from src import response_handler
from src import generate_handler
from src import reasoning_handler
from src import embedding_handler
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
        if question[0] == "$": question = question[1:]  # RAG
        if question[0] == "@":  # Reasoning
            gMd = "Gemini 2.5 Pro"
            question = question[1:]
            reasoning_handler.gp_think()
        else:  # No reasoning
            gMd = "Gemini 2.5 Flash"
            generate_handler.gf_generate()
    except:
        try:  # Gemini 2.5 Flash, fallback if Pro is not available
            if question[0] == "$": question = question[1:]  # RAG
            if question[0] == "@":  # Reasoning
                gMd = "Gemini 2.5 Flash"
                question = question[1:]
                reasoning_handler.gf_think()
                gMd = "Gemini 2.5 Flash"
            else:  # No reasoning
                generate_handler.gf_generate()
        except:
            try:  # Gemini 2.5 Flash Lite, fallback if Flash is not available, although you'll barely reach this point
                if question[0] == "$": question = question[1:]  # RAG
                if question[0] == "@":  # Reasoning
                    gMd = "Gemini 2.5 Flash Lite"
                    question = question[1:]
                    reasoning_handler.gfl_think()
                else:  # No reasoning
                    gMd = "Gemini 2.5 Flash Lite"
                    generate_handler.gfl_generate()
            except Exception as e:  # Erm... you are probably doing something wrong!
                print("Gemini API Key invalid / An error occurred: ", e)
    gRes = ''.join(fullR)  # Join all chunks into a single string for logging and further processing
    gEG = f"{time.perf_counter() - gSG:.3f}"
    print ("\n\n----------\n")

def ask_command(question):
    global cMsg, cRes, cThought, cET, cSG, cEG, cMd
    cThought = False
    try:  # Command A
        if question[0] == "$": question = question[1:]  # RAG
        if question[0] == "@":  # Reasoning
            cMd = "Command A"
            question = question[1:]
            reasoning_handler.ca_think()
        else:  # No reasoning
            cMd = "Command A"
            generate_handler.ca_generate()
    except Exception as e:
        print(e)
        try:  # Command R+, fallback if A is not available, it doesn't support reasoning
            if question[0] == "$": question = question[1:]  # RAG
            cMd = "Command R+"
            question = question[1:]
            generate_handler.crp_generate()
        except:
            try:  # Command R, fallback if R+ is not available, although you'll barely reach this point, R doesn't support reasoning
                if question[0] == "$": question = question[1:]  # RAG
                cMd = "Command R"
                generate_handler.cr_generate()
            except Exception as e:  # Erm... you are probably doing something wrong!
                print("Cohere API Key invalid / An error occurred: ", e)
    cEG = f"{time.perf_counter() - cSG:.3f}"

def merge_responses(question):
    global gRes, cRes, mMsg, mRes, mET, mSG, mEG, mMd
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
        if question[0] == "$": question = question[1:]  # RAG
        if question[0] == "@":  # Reasoning
            mMd = "Gemini 2.5 Pro"
            question = question[1:]
            response = reasoning_handler.gp_think_merge()
        else:  # No reasoning
            mMd = "Gemini 2.5 Flash"
            response = generate_handler.gf_merge()
    except:
        try:  # Gemini 2.5 Flash, fallback if Pro is not available
            if question[0] == "$": question = question[1:]  # RAG
            if question[0] == "@":  # Reasoning
                mMd = "Gemini 2.5 Flash"
                question = question[1:]
                response = reasoning_handler.gf_think_merge()
            else:  # No reasoning
                mMd = "Gemini 2.5 Flash"
                response = generate_handler.gf_merge()
        except:
            try:  # Gemini 2.5 Flash Lite, fallback if Flash is not available, although you'll barely reach this point
                if question[0] == "$": question = question[1:]  # RAG
                if question[0] == "@":  # Reasoning
                    mMd = "Gemini 2.5 Flash Lite"
                    question = question[1:]
                    response = reasoning_handler.gfl_think_merge()
                else:  # No reasoning
                    mMd = "Gemini 2.5 Flash Lite"
                    response = generate_handler.gfl_merge()
            except Exception as e:  # Erm... you are probably doing something wrong!
                print("Gemini API Key invalid / An error occurred: ", e)
    mET = f"{time.perf_counter() - response_handler.tS:.3f}"
    mEG = f"{time.perf_counter() - mSG:.3f}"
    mRes = response.text