from src.cli import file_handler
from src.cli import model_client

match = None

def memorize_question(question, gemini_state, cohere_state):
    # if file_handler.gemini_image:
    #     data = []
    #     for image in file_handler.gemini_image:
    #         data.append({"inline_data": image})
    #     model_client.gemini_messages.append({"role": "user","parts": [{"text": question}] + data})
    # else:
    gemini_state["gemini_messages"].append({"role": "user", "parts": [{"text": question}]})
    # if file_handler.command_image:
    #     data = []
    #     for image in file_handler.command_image:
    #         data.append({"type": "image_url","image_url": {"url": image,"detail": "high"}})
    #     model_client.command_messages.append({"role": "user", "content": [{"type": "text","text": question}] + data})
    # else:
    cohere_state["command_messages"].append({"role": "user", "content": question})
    return gemini_state, cohere_state

# def memorize_response():
#     global current_history
#     if file_handler.skip_command and file_handler.skip_gemini:
#         return
#     elif file_handler.skip_command:
#         gemini_histories.append({"role": "model", "parts": [{"text": model_client.gemini_response}]})
#         command_histories.append({"role": "assistant", "content": model_client.gemini_response})
#         model_client.gemini_messages.append({"role": "model", "parts": model_client.gemini_parts})
#         model_client.command_messages.append({"role": "assistant", "content": model_client.gemini_response})
#     elif file_handler.skip_gemini:
#         gemini_histories.append({"role": "model", "parts": [{"text": model_client.command_response}]})
#         command_histories.append({"role": "assistant", "content": model_client.command_response})
#         model_client.gemini_messages.append({"role": "model", "parts": [{"text": model_client.command_response}]})
#         model_client.command_messages.append({"role": "assistant", "content": model_client.command_response})
#     else:
#         gemini_histories.append({"role": "model", "parts": [{"text": model_client.merged_response}]})
#         command_histories.append({"role": "assistant", "content": model_client.merged_response})
#         model_client.gemini_messages.append({"role": "model", "parts": [model_client.merged_part]})
#         model_client.command_messages.append({"role": "assistant", "content": model_client.merged_response})

#     if not current_history:
#         data = {'gemini': gemini_histories, 'command': command_histories}
#         dt = datetime.datetime.now()
#         now = dt.strftime('%Y-%m-%d-%H-%M-%S')
#         current_history = f'{now}.json'
#         with open("histories/" + current_history, 'w', encoding="utf8") as f: json.dump(data, f, ensure_ascii=False)
#     else:
#         data = {'gemini': gemini_histories, 'command': model_client.command_messages}
#         with open("histories/" + current_history, 'w', encoding="utf8") as f: json.dump(data, f, ensure_ascii=False)