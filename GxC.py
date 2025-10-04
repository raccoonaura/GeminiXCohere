from google.genai import Client
from google.genai import types
import cohere
import threading
with open("geminiLog.txt", "w", encoding="utf-8") as file:
    pass
with open("cohereLog.txt", "w", encoding="utf-8") as file:
    pass
with open("mergedLog.txt", "w", encoding="utf-8") as file:
    pass

client = Client(api_key=input("Enter Gemini API Key: ").strip())
co = cohere.ClientV2(api_key=input("Enter Cohere API Key: ").strip())
question = input("Hello! How can I assist you today? ")

gMsg = []
cMsg = []
mMsg = []
gRes = None
cRes = None
mRes = None

def ask_gemini(question):
    global gRes
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=gMsg,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking, for token efficiency, as it's enabled by default
        ),
    )
    gRes = response.text

def ask_cohere(question):
    global cRes
    res = co.chat(
        model="command-a-03-2025",
        messages=cMsg,
    )
    cRes = res.message.content[0].text

def merge_responses(question):
    global gRes, cRes, mMsg, mRes
    mMsg = {"role": "user", "parts": [{"text": "Here are two responses to the same question. Please merge them into a single, try and include most of the non duplicated contents without worrying about the length of the response, and straight export them without explaining my request and what you're going to do.\n\nQuestion: " + question + "\n\nResponse 1: " + gRes + "\n\nResponse 2: " + cRes}]}  # TODO: Find a better way to format this for Gemini, as it's still exporting the prompt in the response
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=mMsg,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking, for token efficiency, as it's enabled by default
        ),
    )
    mRes = response.text

while True:  # There could be a better way to do this, but this works for now
    try:
        gMsg.append({"role": "user", "parts": [{"text": question}]})  # Memorize question (Gemini)
        cMsg.append({"role": "user", "content": question})  # Memorize question (Cohere)

        t1 = threading.Thread(target=ask_gemini, args=(question,))
        t2 = threading.Thread(target=ask_cohere, args=(question,))
        t1.start()
        t2.start()
        print("Waiting for responses...")
        t1.join()
        t2.join()
        t3 = threading.Thread(target=merge_responses, args=(question,))
        t3.start()
        t3.join()

        # print("\n----------\n\nGemini:\n\n", gRes, "\n\n----------\n\nCohere:\n\n", cRes, "\n\n----------\n\nMerged:\n\n", mRes, "\n\n----------\n")
        print ("\n----------\n\n", mRes, "\n\n----------\n")
        with open("geminiLog.txt", "a", encoding="utf-8") as file:
            file.write("User:" + question + "\n\n" + "Bot:" + gRes + "\n\n")
        with open("cohereLog.txt", "a", encoding="utf-8") as file:
            file.write("User:" + question + "\n\n" + "Bot:" + cRes + "\n\n")
        with open("mergedLog.txt", "a", encoding="utf-8") as file:
            file.write("User:" + question + "\n\n" + "Bot:" + mRes + "\n\n")
        gMsg.append({"role": "model", "parts": [{"text": gRes}]})  # Memorize response (Gemini)
        cMsg.append({"role": "assistant", "content": cRes})  # Memorize response (Cohere)
        question = input("Your turn: ")
    except Exception as e:
        print("API Key無效或發生錯誤: ", e)