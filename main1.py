import time
import chainlit as cl
import replicate
import requests
from chainlit import user_session
from decouple import config

# On chat start
@cl.on_chat_start
async def on_chat_start():
    # Message history
        message_history = []
        user_session.set("MESSAGE_HISTORY", message_history)
                # Replicate client
        client = replicate.Client(api_token=config("REPLICATE_API_KEY"))
        user_session.set("REPLICATE_CLIENT", client)

# Upload image to Replicate
def upload_image(image_path):
    # Get upload URL from Replicate (filename is hardcoded, but not relevant)
    upload_response = requests.post(
                "https://dreambooth-api-experimental.replicate.com/v1/upload/filename.png",
                        headers={"Authorization": f"Token {config('REPLICATE_API_KEY')}"},
                            ).json()
                                # Read file
    file_binary = open(image_path, "rb").read()
                                        # Upload file to Replicate
    requests.put(upload_response["upload_url"], headers={'Content-Type': 'image/png'}, data=file_binary)
                                                # Return URL
    url = upload_response["serving_url"]
    return url

# On message
@cl.on_message
async def main(message: cl.Message):
    # Send empty message for loading
    msg = cl.Message(
        content=f"",
        author="MVP Chatbot",
    )
    await msg.send()

    # Processing images (if any)
    images = [file for file in message.elements if "image" in file.mime]

    # Setup prompt
    prompt = """You are a helpful Assistant that can help me with image recognition and text generation.\n\n"""
    prompt += """Prompt: """ + message.content

    # Retrieve message history
    message_history = user_session.get("MESSAGE_HISTORY")

    # Retrieve Replicate client
    client = user_session.get("REPLICATE_CLIENT")

    # Check if there are images and set input
    if len(images) >= 1:
        # Clear history (we clear history when we have a new image)
        message_history = []
        # Upload image to Replicate
        url = upload_image(images[0].path)
        # Set input with image and without history
        input_vision = {
            "image": url,
            "top_p": 1,
            "prompt": prompt,
            "max_tokens": 1024,
            "temperature": 0.5,
        }
    else:
        # Set input without image and with history
        input_vision = {
            "top_p": 1,
            "prompt": prompt,
            "max_tokens": 1024,
            "temperature": 0.5,
            "history": message_history
        }

    # Call Replicate
    output = client.run(
        f"{config('REPLICATE_MODEL')}:{config('REPLICATE_MODEL_VERSION')}",
        input=input_vision
    )

    # Process the output
    ai_message = ""
    for item in output:
        # Stream token by token
        await msg.stream_token(item)
        # Sleep to provide a better user experience
        time.sleep(0.1)
        # Append to the AI message
        ai_message += item
    # Send the message
    await msg.send()

    # Add to history
    user_text = message.content
    message_history.append("User: " + user_text)
    message_history.append("Assistant:" + ai_message)
    user_session.set("MESSAGE_HISTORY", message_history)