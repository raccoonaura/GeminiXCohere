from google.genai import types
from google.genai import Client
from cohere import ClientV2
from src import response_handler
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
    # gMsg.append({"role": "user", "parts": [{"text": "You will receive a question and an existing answer. Write a complementary response that adds new reasoning, details, or viewpoints not covered before. Do not restate or rephrase the previous answer. Only output the new answer itself.\n\nQuestion: " + question + "\n\nExisting answer: " + cRes}]})
    try:  # Gemini 2.5 Pro
        if question[0] == "@":  # Reasoning
            response = client.models.generate_content_stream(
                model="gemini-2.5-pro",
                contents=gMsg,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=-1)  # Dynamic thinking, token usage depends on the complexity of the question
                ),
            )
            for chunk in response:
                if chunk.text is None:
                    continue
                else:
                    if gThought is False:
                        gThought = True
                        gET = f"{time.perf_counter() - response_handler.tS:.3f}"
                        gSG = time.perf_counter()
                    print(chunk.text, end="")  # Real-time printing since the merged response can take a while
                    fullR.append(chunk.text)
        else:  # No reasoning
            response = client.models.generate_content_stream(
                model="gemini-2.5-flash",  # Using Flash here to save time, as Pro cannot disable thinking
                contents=gMsg,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking, for token efficiency, as it's enabled by default
                ),
            )
            for chunk in response:
                if chunk.text is None:
                    continue
                else:
                    if gThought is False:
                        gThought = True
                        gET = f"{time.perf_counter() - response_handler.tS:.3f}"
                        gSG = time.perf_counter()
                    print(chunk.text, end="")  # Real-time printing since the merged response can take a while
                    fullR.append(chunk.text)
    except:
        try:  # Gemini 2.5 Flash, fallback if Pro is not available
            print ("Gemini 2.5 Pro is not available! Using Gemini 2.5 Flash\n")
            if question[0] == "@":  # Reasoning
                response = client.models.generate_content_stream(
                    model="gemini-2.5-flash",
                    contents=gMsg,
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(thinking_budget=-1)  # Dynamic thinking, token usage depends on the complexity of the question
                    ),
                )
                for chunk in response:
                    if chunk.text is None:
                        continue
                    else:
                        if gThought is False:
                            gThought = True
                            gET = f"{time.perf_counter() - response_handler.tS:.3f}"
                            gSG = time.perf_counter()
                        print(chunk.text, end="")  # Real-time printing since the merged response can take a while
                        fullR.append(chunk.text)
            else:  # No reasoning
                response = client.models.generate_content_stream(
                    model="gemini-2.5-flash",
                    contents=gMsg,
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking, for token efficiency, as it's enabled by default
                    ),
                )
                for chunk in response:
                    if chunk.text is None:
                        continue
                    else:
                        if gThought is False:
                            gThought = True
                            gET = f"{time.perf_counter() - response_handler.tS:.3f}"
                            gSG = time.perf_counter()
                        print(chunk.text, end="")  # Real-time printing since the merged response can take a while
                        fullR.append(chunk.text)
        except:  # Gemini 2.5 Flash Lite, fallback if Flash is not available, although you'll barely reach this point
            try:
                print ("Gemini 2.5 Flash is not available! Using Gemini 2.5 Flash Lite\n")
                if question[0] == "@":  # Reasoning
                    response = client.models.generate_content_stream(
                        model="gemini-2.5-flash-lite",
                        contents=gMsg,
                        config=types.GenerateContentConfig(
                            thinking_config=types.ThinkingConfig(thinking_budget=-1)  # Dynamic thinking, token usage depends on the complexity of the question
                        ),
                    )
                    for chunk in response:
                        if chunk.text is None:
                            continue
                        else:
                            if gThought is False:
                                gThought = True
                                gET = f"{time.perf_counter() - response_handler.tS:.3f}"
                                gSG = time.perf_counter()
                            print(chunk.text, end="")  # Real-time printing since the merged response can take a while
                            fullR.append(chunk.text)
                else:  # No reasoning
                    response = client.models.generate_content_stream(
                        model="gemini-2.5-flash-lite",
                        contents=gMsg,
                        config=types.GenerateContentConfig(
                            thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking, for token efficiency, as it's enabled by default
                        ),
                    )
                    for chunk in response:
                        if chunk.text is None:
                            continue
                        else:
                            if gThought is False:
                                gThought = True
                                gET = f"{time.perf_counter() - response_handler.tS:.3f}"
                                gSG = time.perf_counter()
                            print(chunk.text, end="")  # Real-time printing since the merged response can take a while
                            fullR.append(chunk.text)
            except Exception as e:  # Erm... you are probably doing something wrong!
                print("Gemini API Key無效或發生錯誤: ", e)
    gRes = ''.join(fullR)  # Join all chunks into a single string for logging and further processing
    gEG = f"{time.perf_counter() - gSG:.3f}"
    # print ("\n\n----------\n")
    print ("\n\n----------\n")

def ask_command(question):
    global cMsg, cRes, cThought, cET, cSG, cEG
    cThought = False
    try:  # Command A
        if question[0] == "@":  # Reasoning
            response = co.chat_stream(
                model="command-a-reasoning-08-2025",
                messages=cMsg,
            )
            for event in response:
                if event.type == "content-delta":
                    '''
                    if event.delta.message.content.thinking:
                        print(event.delta.message.content.thinking, end="")
                    '''  # Thinking context, maybe I'll re-enable this in the future, but for now it's gonna look messy
                    if event.delta.message.content.text:
                        if cThought is False:
                            cThought = True
                            cET = f"{time.perf_counter() - response_handler.tS:.3f}"
                            cSG = time.perf_counter()
                        chunk = event.delta.message.content.text
                        # print(event.delta.message.content.text, end="")
                        cRes += chunk
        else:  # No reasoning
            res = co.chat_stream(
                model="command-a-03-2025",
                messages=cMsg,
            )
            for event in res:
                if event:
                    if event.type == "content-delta":
                        if event.delta.message.content.text:
                            if cThought is False:
                                cThought = True
                                cET = f"{time.perf_counter() - response_handler.tS:.3f}"
                                cSG = time.perf_counter()
                            chunk = event.delta.message.content.text
                            # print(event.delta.message.content.text, end="")
                            cRes += chunk
    except:  # Command R+, fallback if A is not available
        try:
            # print ("Cohere Command A is not available! Using Command R+\n")
            # if question[0] == "@":  # Reasoning
            #     print ("Current model does not support reasoning!\n")
            res = co.chat_stream(
                model="command-r-plus-08-2024",
                messages=cMsg,
            )
            for event in res:
                if event:
                    if event.type == "content-delta":
                        if event.delta.message.content.text:
                            if cThought is False:
                                cThought = True
                                cET = f"{time.perf_counter() - response_handler.tS:.3f}"
                                cSG = time.perf_counter()
                            chunk = event.delta.message.content.text
                            # print(event.delta.message.content.text, end="")
                            cRes += chunk
        except:  # Command R, fallback if R+ is not available, although you'll barely reach this point
            try:
                # print ("Cohere Command R+ is not available! Using Command R\n")
                # if question[0] == "@":  # Reasoning
                #     print ("Current model does not support reasoning!\n")
                res = co.chat_stream(
                    model="command-r-08-2024",
                    messages=cMsg,
                )
                for event in res:
                    if event:
                        if event.type == "content-delta":
                            if event.delta.message.content.text:
                                if cThought is False:
                                    cThought = True
                                    cET = f"{time.perf_counter() - response_handler.tS:.3f}"
                                    cSG = time.perf_counter()
                                chunk = event.delta.message.content.text
                                # print(event.delta.message.content.text, end="")
                                cRes += chunk
            except Exception as e:  # Erm... you are probably doing something wrong!
                print("Cohere API Key無效或發生錯誤: ", e)
    cEG = f"{time.perf_counter() - cSG:.3f}"
    # print ("\n\n----------\n\nGenerating full response...")

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

    try:  # Gemini 2.5 Pro
        if question[0] == "@":  # Reasoning
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=mMsg,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=-1)  # Dynamic thinking, token usage depends on the complexity of the question
                ),
            )
        else:  # No reasoning
            response = client.models.generate_content(
                model="gemini-2.5-flash",  # Using Flash here to save time, as Pro cannot disable thinking
                contents=mMsg,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking, for token efficiency, as it's enabled by default
                ),
            )
    except:  # Gemini 2.5 Flash, fallback if Pro is not available
        print("Gemini 2.5 Pro is not available! Using Gemini 2.5 Flash\n")
        try:
            if question[0] == "@":  # Reasoning
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=mMsg,
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(thinking_budget=-1)  # Dynamic thinking, token usage depends on the complexity of the question
                    ),
                )
            else:  # No reasoning
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=mMsg,
                    config=types.GenerateContentConfig(
                        thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking, for token efficiency, as it's enabled by default
                    ),
                )
        except:  # Gemini 2.5 Flash Lite, fallback if Flash is not available, although you'll barely reach this point
            print("Gemini 2.5 Flash is not available! Using Gemini 2.5 Flash Lite\n")
            try:
                if question[0] == "@":  # Reasoning
                    response = client.models.generate_content(
                        model="gemini-2.5-flash-lite",
                        contents=mMsg,
                        config=types.GenerateContentConfig(
                            thinking_config=types.ThinkingConfig(thinking_budget=-1)  # Dynamic thinking, token usage depends on the complexity of the question
                        ),
                    )
                else:  # No reasoning
                    response = client.models.generate_content(
                        model="gemini-2.5-flash-lite",
                        contents=mMsg,
                        config=types.GenerateContentConfig(
                            thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking, for token efficiency, as it's enabled by default
                        ),
                    )
            except Exception as e:  # Erm... you are probably doing something wrong!
                print("Gemini API Key無效或發生錯誤: ", e)
    mET = f"{time.perf_counter() - response_handler.tS:.3f}"
    mEG = f"{time.perf_counter() - mSG:.3f}"
    mRes = response.text