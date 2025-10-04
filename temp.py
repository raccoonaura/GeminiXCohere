from google.genai import Client
from google.genai import types
import cohere
import threading
client = Client(api_key=input("Enter Gemini API Key: ").strip())
co = cohere.ClientV2(api_key=input("Enter Cohere API Key: ").strip())
question = input("Hello! How can I assist you today? ").strip()
gMsg = []
cMsg = []
gRes = None
cRes = None
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

try:
    gMsg.append({"role": "user", "parts": [{"text": question}]})
    cMsg.append({"role": "user", "content": question})

    t1 = threading.Thread(target=ask_gemini, args=(question,))
    t2 = threading.Thread(target=ask_cohere, args=(question,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print("\n----------\n\nGemini:\n\n", gRes, "\n\n----------\n\nCohere:\n\n", cRes, "\n\n----------\n")
    gMsg.append({"role": "model", "parts": [{"text": gRes}]})  # Memorize response
    cMsg.append({"role": "assistant", "content": cRes})  # Memorize response
except Exception as e:
    print("API Key無效或發生錯誤: ", e)