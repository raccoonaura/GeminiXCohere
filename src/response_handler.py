from google.genai import types
from google.genai import Client
from cohere import ClientV2
import threading
from src import logging_handler
from src import utils

gMsg = []
cMsg = []
mMsg = []
fullR = []
gRes = ""
cRes = ""
mRes = ""

def initialize_gemini():
    global client
    client = Client(api_key=input("Enter Gemini API Key: ").strip())

def initialize_cohere():
    global co
    co = ClientV2(api_key=input("Enter Cohere API Key: ").strip())

def memorize_question(question):
    gMsg.append({"role": "user", "parts": [{"text": question}]})  # Memorize question (Gemini)
    cMsg.append({"role": "user", "content": question})  # Memorize question (Cohere)

def memorize_response():
    gMsg.append({"role": "model", "parts": [{"text": mRes}]})  # Memorize response (Gemini)
    cMsg.append({"role": "assistant", "content": mRes})  # Memorize response (Cohere)

def ask_gemini(question):
    global gMsg, gRes
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
                print(chunk.text, end="")  # Real-time printing since the merged response can take a while
                fullR.append(chunk.text)
        else:  # No reasoning
            response = client.models.generate_content_stream(
                model="gemini-2.5-pro",
                contents=gMsg,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking, for token efficiency, as it's enabled by default
                ),
            )
            for chunk in response:
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
                        print(chunk.text, end="")  # Real-time printing since the merged response can take a while
                        fullR.append(chunk.text)
            except Exception as e:  # Erm... you are probably doing something wrong!
                print("Gemini API Key無效或發生錯誤: ", e)
    gRes = ''.join(fullR)  # Join all chunks into a single string for logging and further processing
    fullR.clear()
    print ("\n\n----------\n")

def ask_cohere(question):
    global cMsg, cRes
    try:  # Command A
        if question[0] == "@":  # Reasoning
            response = co.chat_stream(
                model="command-a-reasoning-08-2025",
                messages=cMsg,
            )
            for event in response:
                if event.type == "content-delta":
                    """
                    if event.delta.message.content.thinking:
                        print(event.delta.message.content.thinking, end="")
                    """  # Thinking context, maybe I'll re-enable this in the future, but for now it's gonna look messy
                    if event.delta.message.content.text:
                        chunk = event.delta.message.content.text
                        print(event.delta.message.content.text, end="")
                        cRes += chunk
        else:  # No reasoning
            res = co.chat_stream(
                model="command-a-03-2025",
                messages=cMsg,
            )
            for event in res:
                if event:
                    if event.type == "content-delta":
                        chunk = event.delta.message.content.text
                        print(event.delta.message.content.text, end="")
                        cRes += chunk
    except:  # Command R+, fallback if A is not available
        try:
            print ("Cohere Command A is not available! Using Command R+")
            if question[0] == "@":  # Reasoning
                print ("Current model does not support reasoning!\n")
            res = co.chat_stream(
                model="command-r-plus-08-2024",
                messages=cMsg,
            )
            for event in res:
                if event:
                    if event.type == "content-delta":
                        chunk = event.delta.message.content.text
                        print(event.delta.message.content.text, end="")
                        cRes += chunk
        except:  # Command R, fallback if R+ is not available, although you'll barely reach this point
            try:
                print ("Cohere Command R+ is not available! Using Command R")
                if question[0] == "@":  # Reasoning
                    print ("Current model does not support reasoning!\n")
                res = co.chat_stream(
                    model="command-r-08-2024",
                    messages=cMsg,
                )
                for event in res:
                    if event:
                        if event.type == "content-delta":
                            chunk = event.delta.message.content.text
                            print(event.delta.message.content.text, end="")
                            cRes += chunk
            except Exception as e:  # Erm... you are probably doing something wrong!
                print("Cohere API Key無效或發生錯誤: ", e)
    print ("\n\n----------\n\nGenerating full response...")

def merge_responses(question):
    global gRes, cRes, mMsg, mRes
    mMsg = {"role": "user", "parts": [{"text": "Here are two responses to the same question. Please merge them into a single response with additional information that could be relevant, or the previous two responses missed. Try to include most of the non-duplicated content without worrying about the length of the response. Export them without explaining my request, what you're going to do, and what you added, etc.\n\nQuestion: " + question + "\n\nResponse 1: " + gRes + "\n\nResponse 2: " + cRes}]}

    # Easier to read version
    """
    Here are two responses to the same question.
    Please merge them into a single response
    with additional information that could be relevant,
    or the previous two responses missed.
    Try to include most of the non-duplicated content
    without worrying about the length of the response.
    Export them without explaining my request,
    what you're going to do, and what you added, etc.
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
                model="gemini-2.5-pro",
                contents=mMsg,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking, for token efficiency, as it's enabled by default
                ),
            )
    except:  # Gemini 2.5 Flash, fallback if Pro is not available
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
    mRes = response.text

def generate_response(question):
    '''
    t1 = threading.Thread(target=ask_gemini, args=(question,))
    t2 = threading.Thread(target=ask_cohere, args=(question,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    '''

    # Add this and quotes around the below lines to make both models think at the same time for faster generations,
    # but you gotta disable one of their real-time printing

    # '''
    t1 = threading.Thread(target=ask_gemini, args=(question,))
    t1.start()
    t1.join()
    t2 = threading.Thread(target=ask_cohere, args=(question,))
    t2.start()
    t2.join()
    # '''
    t3 = threading.Thread(target=merge_responses, args=(question,))
    t3.start()
    t3.join()

def handle_conversation(question):
    try:
        utils.clear_all()
        print ("You: ", question, "\n\n----------\n")

        memorize_question(question)
        if (question[0] == "@"):
            print ("Enabled reasoning! Please wait...\n\n----------\n")
        generate_response(question)

        # print("\n----------\n\nGemini:\n\n", gRes, "\n\n----------\n\nCohere:\n\n", cRes, "\n\n----------\n\nMerged:\n\n", mRes, "\n\n----------\n")
        utils.clear_all()
        print ("You: ", question, "\n\n----------\n\n", mRes, "\n\n----------\n")

        logging_handler.log_interaction(question, gRes, cRes, mRes)

        memorize_response()

        utils.set_marker()

    except Exception as e:
        print("API Key無效或發生錯誤: ", e)