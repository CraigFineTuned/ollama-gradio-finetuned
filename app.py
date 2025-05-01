import gradio as gr
import ollama
import json
import base64
import copy
import traceback
import sys

# Add better debugging
print("Starting application...")

# Test Ollama connection and print available models
try:
    model_list = ollama.list()
    model_names = [model['model'] for model in model_list['models']]
    print(f"Successfully connected to Ollama! Models available: {model_names}")
except Exception as e:
    print(f"ERROR connecting to Ollama: {str(e)}")
    model_names = ["llama3.1:8b"]  # Provide a default model
    print("Using default model list since Ollama connection failed")

PROMPT_LIST = []
VL_CHAT_LIST = []
# Parse prompt
try:
    with open("prompt.json", "r", encoding="utf-8") as f:
        PROMPT_DICT = json.load(f)
        for key in PROMPT_DICT:
            PROMPT_LIST.append(key)
    print(f"Loaded prompts: {PROMPT_LIST}")
except Exception as e:
    print(f"Error loading prompt.json: {str(e)}")
    PROMPT_DICT = {}

# Create a map of Chinese prompt names to English ones (for backward compatibility)
prompt_name_map = {
    "翻译助手": "Translation Assistant",
    "周报助手": "Weekly Report Helper",
    "答案之书": "Book of Answers"
}

# Filter out Chinese prompts from the display list if an English equivalent exists
display_prompt_list = []
for prompt in PROMPT_LIST:
    # If it's a Chinese prompt with an English equivalent, skip it
    if prompt in prompt_name_map and prompt_name_map[prompt] in PROMPT_LIST:
        continue
    display_prompt_list.append(prompt)
    
# Initialize function
def init():
    VL_CHAT_LIST.clear()
    
# Chat function with error handling
def ollama_chat(message, history, model_name, history_flag):
    print(f"\nollama_chat called. Model: {model_name}, Message: {message}")
    try:
        if not model_name:
            print("No model selected!")
            return history + [(message, "ERROR: Please select a model first")]
            
        messages = []
        chat_message = {
            'role': 'user', 
            'content': message
        }
        if history_flag and len(history)>0:
            for element in history:  
                history_user_message = {
                    'role': 'user', 
                    'content': element[0]
                }
                history_assistant_message = {
                    'role': 'assistant', 
                    'content': element[1]
                }
                messages.append(history_user_message)
                messages.append(history_assistant_message)   
        messages.append(chat_message)
        
        print(f"Sending request to Ollama with model: {model_name}")
        print(f"Messages: {messages}")
        
        response = ollama.chat(
            model = model_name,
            messages = messages
        )
        
        print(f"Response received from Ollama")
        
        # Get the response text
        result = response['message']['content']
        
        # Return the updated history with the new message pair
        return history + [(message, result)]
                
    except Exception as e:
        print(f"ERROR in ollama_chat: {str(e)}")
        print(traceback.format_exc())
        error_message = f"Error: {str(e)}"
        return history + [(message, error_message)]

# Generate intelligent agent
def ollama_prompt(message, history, model_name, prompt_info):
    print(f"\nollama_prompt called. Model: {model_name}, Prompt: {prompt_info}, Message: {message}")
    try:
        if not model_name:
            print("No model selected!")
            return history + [(message, "ERROR: Please select a model first")]
            
        # Check if prompt_info is a Chinese key and map it to English if needed
        prompt_key = prompt_info
        if prompt_info in prompt_name_map:
            prompt_key = prompt_name_map[prompt_info]
        
        system_message = {
            'role': 'system', 
            'content': PROMPT_DICT.get(prompt_key, "You are a helpful assistant.")
        }
        user_message = {
            'role': 'user', 
            'content': message
        }
        messages = [system_message, user_message]
        
        print(f"Sending request to Ollama with model: {model_name}")
        print(f"Messages: {messages}")
        
        response = ollama.chat(
            model = model_name,
            messages = messages
        )
        
        print(f"Response received from Ollama")
        
        # Get the response text
        result = response['message']['content']
        
        # Return the updated history with the new message pair
        return history + [(message, result)]
                
    except Exception as e:
        print(f"ERROR in ollama_prompt: {str(e)}")
        print(traceback.format_exc())
        error_message = f"Error: {str(e)}"
        return history + [(message, error_message)]

# Image upload
def vl_image_upload(image_path, chat_history):
    try:
        if not image_path:
            return None, chat_history
            
        message = {
            "type": "image",
            "content": image_path
        }
        chat_history.append(((image_path,), None))
        VL_CHAT_LIST.append(message)
        return None, chat_history
    except Exception as e:
        print(f"ERROR in vl_image_upload: {str(e)}")
        print(traceback.format_exc())
        return None, chat_history

# Submit question
def vl_submit_message(message, chat_history):
    try:
        if not message or message.strip() == "":
            return "", chat_history
            
        messsage = {
            "type": "user",
            "content": message
        }
        chat_history.append((message, None))
        VL_CHAT_LIST.append(messsage)
        return "", chat_history
    except Exception as e:
        print(f"ERROR in vl_submit_message: {str(e)}")
        print(traceback.format_exc())
        return "", chat_history

# Retry
def vl_retry(chat_history):
    try:
        if len(VL_CHAT_LIST) > 1:
            if VL_CHAT_LIST[len(VL_CHAT_LIST)-1]['type'] == "assistant":
                VL_CHAT_LIST.pop()
                if chat_history and len(chat_history) > 0:
                    chat_history.pop()
        return chat_history
    except Exception as e:
        print(f"ERROR in vl_retry: {str(e)}")
        print(traceback.format_exc())
        return chat_history

# Undo
def vl_undo(chat_history):
    try:
        message = ""
        chat_list = copy.deepcopy(VL_CHAT_LIST)
        if len(chat_list) > 1:
            if chat_list[len(chat_list)-1]['type'] == "assistant":
                # Get the user message content
                message = chat_list[len(chat_list)-2]['content']
                # Remove the assistant message and the user message
                VL_CHAT_LIST.pop()
                VL_CHAT_LIST.pop()
                if chat_history and len(chat_history) >= 2:
                    chat_history.pop()
                    chat_history.pop()
            elif chat_list[len(chat_list)-1]['type'] == "user":
                # Get the user message content
                message = chat_list[len(chat_list)-1]['content']
                # Remove the user message
                VL_CHAT_LIST.pop()
                if chat_history and len(chat_history) > 0:
                    chat_history.pop()
        return message, chat_history
    except Exception as e:
        print(f"ERROR in vl_undo: {str(e)}")
        print(traceback.format_exc())
        return "", chat_history

# Clear
def vl_clear():
    try:
        VL_CHAT_LIST.clear()
        return None, "", []
    except Exception as e:
        print(f"ERROR in vl_clear: {str(e)}")
        print(traceback.format_exc())
        return None, "", []

# Return the answer to the question
def vl_submit(history_flag, chinese_flag, chat_history, vision_model_info):
    try:
        if len(VL_CHAT_LIST) > 1:
            messages = get_vl_message(history_flag, chinese_flag)
            # Use selected model or fallback to llava
            vision_model = vision_model_info if vision_model_info else "llava:7b-v1.6"
            print(f"Sending request to Ollama with vision model: {vision_model}")
            print(f"Messages: {messages}")
            
            response = ollama.chat(
                model = vision_model,
                messages = messages
            )
            
            print(f"Response received: {response}")
            
            result = response["message"]["content"]
            output = {
                "type": "assistant",
                "content": result
            }
            # Use tuple format for Chatbot
            chat_history.append((None, result))
            VL_CHAT_LIST.append(output)
        else:
            print("Not enough messages in VL_CHAT_LIST")
            gr.Warning('Error: No messages to process')
        return chat_history
    except Exception as e:
        print(f"ERROR in vl_submit: {str(e)}")
        print(traceback.format_exc())
        gr.Warning(f'Error getting result: {str(e)}')
        return chat_history

def get_vl_message(history_flag, chinese_flag):
    try:
        messages = []
        
        if history_flag:
            i = 0
            while i < len(VL_CHAT_LIST):
                if i + 1 < len(VL_CHAT_LIST) and VL_CHAT_LIST[i]['type'] == "image" and VL_CHAT_LIST[i+1]['type'] == "user":
                    image_path = VL_CHAT_LIST[i]["content"]
                    # Read binary data of the image file
                    with open(image_path, "rb") as image_file:
                        image_data = image_file.read()
                    # Convert binary data to a base64 encoded string
                    base64_string = base64.b64encode(image_data).decode("utf-8")
                    content = VL_CHAT_LIST[i+1]["content"]
                    chat_message = {
                        'role': 'user', 
                        'content': content,
                        'images': [base64_string]
                    }
                    messages.append(chat_message)
                    i += 2
                elif VL_CHAT_LIST[i]['type'] == "assistant":
                    assistant_message = {
                        "role": "assistant",
                        "content": VL_CHAT_LIST[i]['content']
                    }
                    messages.append(assistant_message)
                    i += 1
                elif VL_CHAT_LIST[i]['type'] == "user":
                    user_message = {
                        "role": "user",
                        "content": VL_CHAT_LIST[i]['content']
                    }
                    messages.append(user_message)
                    i += 1
                else:
                    i += 1
        else:
            if len(VL_CHAT_LIST) >= 2 and VL_CHAT_LIST[0]['type'] == "image" and VL_CHAT_LIST[-1]['type'] == "user":
                image_path = VL_CHAT_LIST[0]["content"]
                # Enable context
                with open(image_path, "rb") as image_file:
                    image_data = image_file.read()
                # Handle image processing
                base64_string = base64.b64encode(image_data).decode("utf-8")
                content = VL_CHAT_LIST[-1]["content"]
                chat_message = {
                    'role': 'user', 
                    'content': content,
                    'images': [base64_string]
                }
                messages.append(chat_message)
    except Exception as e:
        print(f"Error processing messages: {str(e)}")
        print(traceback.format_exc())
        # Return a simple message if there's an error
        messages = [{
            'role': 'user',
            'content': 'There was an error processing the messages.'
        }]
    
    # Add system message based on language preference
    if chinese_flag:
        system_message = {
            'role': 'system', 
            'content': 'You are a Helpful Assistant. Please answer the question in Chinese. 你是一个有帮助的助手，请用中文回答问题。'
        }
        messages.insert(0, system_message)
    else:
        system_message = {
            'role': 'system', 
            'content': 'You are a Helpful Assistant. Please answer the question accordingly.'
        }
        messages.insert(0, system_message)
    
    return messages

with gr.Blocks(title="Ollama WebUI") as demo:
    with gr.Tab("Chat"):
        with gr.Row():
            with gr.Column(scale=1):
                model_info = gr.Dropdown(model_names, value=model_names[0] if model_names else "llama3.1:8b", allow_custom_value=True, label="Model Selection")
                history_flag = gr.Checkbox(label="Enable Context")
            with gr.Column(scale=4):
                chat_bot = gr.Chatbot(height=600, label="Chat")
                with gr.Row():
                    text_box = gr.Textbox(label="Message", placeholder="Type your message here...")
                    submit_btn = gr.Button("Submit", variant="primary")
                
                # Set up simple event handlers
                submit_btn.click(
                    fn=ollama_chat,
                    inputs=[text_box, chat_bot, model_info, history_flag],
                    outputs=chat_bot
                ).then(
                    fn=lambda: "",
                    inputs=None,
                    outputs=text_box
                )
                
                text_box.submit(
                    fn=ollama_chat,
                    inputs=[text_box, chat_bot, model_info, history_flag],
                    outputs=chat_bot
                ).then(
                    fn=lambda: "",
                    inputs=None,
                    outputs=text_box
                )
                
                gr.Button("Clear").click(
                    fn=lambda: [],
                    inputs=None,
                    outputs=chat_bot
                )
    with gr.Tab("Agent"):
        with gr.Row():
            with gr.Column(scale=1):
                prompt_model_info = gr.Dropdown(model_names, value=model_names[0] if model_names else "llama3.1:8b", allow_custom_value=True, label="Model Selection")
                prompt_info = gr.Dropdown(choices=display_prompt_list, value=display_prompt_list[0] if display_prompt_list else None, label="Agent Selection", interactive=True)
            with gr.Column(scale=4):
                prompt_chat_bot = gr.Chatbot(height=600, label="Agent Chat")
                with gr.Row():
                    prompt_text_box = gr.Textbox(label="Message", placeholder="Type your message here...")
                    prompt_submit_btn = gr.Button("Submit", variant="primary")
                
                # Set up simple event handlers
                prompt_submit_btn.click(
                    fn=ollama_prompt,
                    inputs=[prompt_text_box, prompt_chat_bot, prompt_model_info, prompt_info],
                    outputs=prompt_chat_bot
                ).then(
                    fn=lambda: "",
                    inputs=None,
                    outputs=prompt_text_box
                )
                
                prompt_text_box.submit(
                    fn=ollama_prompt,
                    inputs=[prompt_text_box, prompt_chat_bot, prompt_model_info, prompt_info],
                    outputs=prompt_chat_bot
                ).then(
                    fn=lambda: "",
                    inputs=None,
                    outputs=prompt_text_box
                )
                
                gr.Button("Clear").click(
                    fn=lambda: [],
                    inputs=None,
                    outputs=prompt_chat_bot
                )
    with gr.Tab("Vision Assistant"):
        with gr.Row():
            with gr.Column(scale=1):
                history_flag = gr.Checkbox(label="Enable Context")
                chinese_flag = gr.Checkbox(value=False, label="Force Chinese")
                vision_model_info = gr.Dropdown(model_names, value="llava:7b-v1.6", allow_custom_value=True, label="Model Selection")
                image = gr.Image(type="filepath")
            with gr.Column(scale=4):
                chat_bot = gr.Chatbot(height=600, label="Vision Chat")
                with gr.Row():
                    message = gr.Textbox(label="Message", placeholder="Type your message here...")
                    submit_btn = gr.Button("Submit", variant="primary")
                
                # Clear button
                gr.Button("Clear").click(fn=vl_clear, inputs=[], outputs=[image, message, chat_bot])
        
        # Set up event handlers
        image.upload(fn=vl_image_upload, inputs=[image, chat_bot], outputs=[image, chat_bot])
        
        submit_btn.click(
            fn=vl_submit_message,
            inputs=[message, chat_bot],
            outputs=[message, chat_bot]
        ).then(
            fn=vl_submit,
            inputs=[history_flag, chinese_flag, chat_bot, vision_model_info],
            outputs=[chat_bot]
        )
    demo.load(fn=init)

if __name__ == "__main__":
    demo.queue()  # Use queue method instead of enable_queue parameter
    demo.launch(share=False)