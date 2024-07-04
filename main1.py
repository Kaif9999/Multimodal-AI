import time
import chainlit as cl
import replicate
import requests
from chainlit import user_session
from decouple import config

#user have to create a .env file and add the following variables
# Load API key and model details from environment variables
REPLICATE_API_KEY = config('REPLICATE_API_KEY')
REPLICATE_TEXT_MODEL = config('REPLICATE_TEXT_MODEL')
REPLICATE_TEXT_MODEL_VERSION = config('REPLICATE_TEXT_MODEL_VERSION')
REPLICATE_IMAGE_MODEL = config('REPLICATE_IMAGE_MODEL')
REPLICATE_IMAGE_MODEL_VERSION = config('REPLICATE_IMAGE_MODEL_VERSION')

# On chat start
@cl.on_chat_start
async def on_chat_start():
    # Initialize message history
    message_history = []
    user_session.set("MESSAGE_HISTORY", message_history)
    
    # Initialize Replicate client with the correct API token
    api_token = config("REPLICATE_API_KEY")
    if not api_token:
        raise ValueError("Replicate API key is not set.")
    client = replicate.Client(api_token=api_token)
    user_session.set("REPLICATE_CLIENT", client)

# Upload image to Replicate
def upload_image(image_path):
    # Get upload URL from Replicate (filename is hardcoded, but not relevant)
    upload_response = requests.post(
        "https://dreambooth-api-experimental.replicate.com/v1/upload/filename.png",
        headers={"Authorization": f"Token {config('REPLICATE_API_KEY')}"},  # Ensure API key is included here
    ).json()
    # Read file
    file_binary = open(image_path, "rb").read()
    # Upload file to Replicate
    requests.put(upload_response["upload_url"], headers={'Content-Type': 'image/png'}, data=file_binary)
    # Return URL
    url = upload_response["serving_url"]
    return url

# Generate image using Replicate
def generate_image(prompt):
    client = user_session.get("REPLICATE_CLIENT")
    input_params = {
        "width": 1024,
        "height": 1024,
        "prompt": prompt,  # Use the prompt for image generation
        "refine": "expert_ensemble_refiner",
        "apply_watermark": False,
        "num_inference_steps": 25
    }
    output = client.run(
        f"{REPLICATE_IMAGE_MODEL}:{REPLICATE_IMAGE_MODEL_VERSION}",
        input=input_params
    )
    return output

# On message
@cl.on_message
async def main(message: cl.Message):
    # Send empty message for loading
    msg = cl.Message(
        content=f"",
        author="",
    )
    await msg.send()

    # Processing images (if any)
    images = [file for file in message.elements if "image" in file.mime]

    # Setup prompt based on user's message content
    prompt = message.content.lower() # Directly use user's message content as prompt

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

    # Check if the message is for image generation
    if "generate image" in message.content.lower():
        # Generate image based on the prompt
        output = generate_image(prompt)
        # Assuming the output is a list of image URLs
        image_url = output[0]
        ai_message = f"Here is the generated image: {image_url}"
        await cl.Message(content=ai_message).send()
    else:
        # Text generation call
        output = client.run(
            f"{REPLICATE_TEXT_MODEL}:{REPLICATE_TEXT_MODEL_VERSION}",
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
