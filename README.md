# Open-source Multimodal 

Here's a comprehensive `README.md` file for you all to get started with this concept of Multimodality AI project

---

MVP Chatbot is an AI-powered chatbot capable of performing image recognition and text generation using the Replicate API which uses MIstral 7B under the hood. The chatbot interacts with users, processes images, and generates text responses based on user input.

## Features

- Image recognition
- Image generation
- Text generation
- Interactive chat experience
- Easy to set up and extend

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Usage](#usage)
4. [Project Structure](#project-structure)
5. [Future Scope](#future-scope)
6. [Contributing](#contributing)

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/Kaif9999/Multimodal-AI
    cd Mulimodal-AI
    ```

2. **Create a virtual environment**:
    ```bash
    python -m venv venv
    ```

3. **Activate the virtual environment**:
    - On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. **Set up environment variables**:
    Create a `.env` file in the root directory and add the following variables:
    ```env
    REPLICATE_API_KEY = <'Your Replicate API key'>
    REPLICATE_TEXT_MODEL = yorickvp/llava-v1.6-mistral-7b
    REPLICATE_TEXT_MODEL_VERSION = 19be067b589d0c46689ffa7cc3ff321447a441986a7694c01225973c2eafc874
    REPLICATE_IMAGE_MODEL = stability-ai/sdxl
    REPLICATE_IMAGE_MODEL_VERSION = 7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc
    ```

## Usage

1. **Run the chatbot**:

   #### Step 1
    ```bash
    python main1.py
    ```
   #### Step 2
    ```bash
    chainlit run main1.py
    ```

3. **Interacting with the chatbot**:
    - Start a chat and send messages.
    - Upload images for recognition.

## Project Structure

```plaintext
Multimodal-AI/
├── venv/                   # Virtual environment directory
├── .env                     # Environment Variables
├── .gitignore                    # gitignore file
├── main1.py                 # Main script to run the chatbot
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── chainlit.md             # Text that displays on the frontend of the Chatbot
└── test_main1.py           # Performs Unit Tests and Mock Test on main1.py file
```

## Code Explanation

### main.py

The main script initializes the chatbot, sets up the Replicate client, processes user messages, and handles image uploads.

- **Imports**:
    ```python
    import time
    import chainlit as cl
    import replicate
    import requests
    from chainlit import user_session
    from decouple import config
    ```

- **On chat start**:
    Initializes message history and Replicate client.
    ```python
    @cl.on_chat_start
    async def on_chat_start():
        message_history = []
        user_session.set("MESSAGE_HISTORY", message_history)
        api_token = config("REPLICATE_API_KEY")
        client = replicate.Client(api_token=api_token)
        user_session.set("REPLICATE_CLIENT", client)
    ```

- **Upload image**:
    Handles image upload to Replicate.
    ```python
    def upload_image(image_path):
        upload_response = requests.post(
            "https://dreambooth-api-experimental.replicate.com/v1/upload/filename.png",
            headers={"Authorization": f"Token {config('REPLICATE_API_KEY')}"}
        ).json()
        file_binary = open(image_path, "rb").read()
        requests.put(upload_response["upload_url"], headers={'Content-Type': 'image/png'}, data=file_binary)
        return upload_response["serving_url"]
    ```

- **On message**:
    Processes user messages, uploads images, and generates responses.
    ```python
    @cl.on_message
    async def main(message: cl.Message):
        msg = cl.Message(content="", author="mvp assistant")
        await msg.send()

        images = [file for file in message.elements if "image" in file.mime]
        prompt = f"You are a helpful Assistant that can help me with image recognition and text generation.\n\nPrompt: {message.content}"

        message_history = user_session.get("MESSAGE_HISTORY")
        client = user_session.get("REPLICATE_CLIENT")

        if images:
            message_history = []
            url = upload_image(images[0].path)
            input_vision = {"image": url, "top_p": 1, "prompt": prompt, "max_tokens": 1024, "temperature": 0.6}
        else:
            input_vision = {"top_p": 1, "prompt": prompt, "max_tokens": 1024, "temperature": 0.5, "history": message_history}

        output = client.run(f"{config('REPLICATE_MODEL')}:{config('REPLICATE_MODEL_VERSION')}", input=input_vision)

        ai_message = ""
        for item in output:
            await msg.stream_token(item)
            time.sleep(0.1)
            ai_message += item
        await msg.send()

        message_history.append(f"User: {message.content}")
        message_history.append(f"Assistant: {ai_message}")
        user_session.set("MESSAGE_HISTORY", message_history)
    ```

## Future Scope 
1. Implementation of image generation function
2. To be able to give input in multiple languages, and get output in your desired language
3. Implementation of text to speech
4. Looking for integrating Gemini-Flash for image and text generation

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. **Fork the repository**.
2. **Create a new branch**:
    ```bash
    git checkout -b feature-branch
    ```
3. **Make your changes**.
4. **Commit your changes**:
    ```bash
    git commit -m "Add feature"
    ```
5. **Push to the branch**:
    ```bash
    git push origin feature-branch
    ```
6. **Create a Pull Request**.

