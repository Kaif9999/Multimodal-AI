# Multimodal-AI

Here's a comprehensive `README.md` file for your chatbot project. This document will help others understand your codebase and contribute effectively.

---

# Vision Chatbot

Vision Chatbot is an AI-powered assistant capable of performing image recognition and text generation using the Replicate API. The chatbot interacts with users, processes images, and generates text responses based on user input.

## Features

- Image recognition
- Text generation
- Interactive chat experience
- Easy to set up and extend

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Usage](#usage)
4. [Project Structure](#project-structure)
5. [Contributing](#contributing)
6. [License](#license)

## Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/vision-chatbot.git
    cd vision-chatbot
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
    REPLICATE_API_KEY=your_replicate_api_key
    REPLICATE_MODEL=your_replicate_model
    REPLICATE_MODEL_VERSION=your_replicate_model_version
    ```

## Usage

1. **Run the chatbot**:
    ```bash
    python main.py
    ```

2. **Interacting with the chatbot**:
    - Start a chat and send messages.
    - Upload images for recognition.

## Project Structure

```plaintext
vision-chatbot/
├── venv/                   # Virtual environment directory
├── .env                    # Environment variables
├── main.py                 # Main script to run the chatbot
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
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

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Feel free to update this `README.md` with any additional details specific to your project. This should help others understand the structure and contribute effectively.
