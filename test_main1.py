import pytest
import requests
import requests_mock
from unittest.mock import patch, MagicMock
from decouple import config
from main1 import on_chat_start, main, upload_image
import chainlit as cl
from chainlit import user_session

# Mock environment variables
REPLICATE_API_KEY = 'test_api_key'
REPLICATE_MODEL = 'test_model'
REPLICATE_MODEL_VERSION = 'test_version'

# Helper function to simulate message object
class MockMessage:
    def __init__(self, content, elements=[]):
        self.content = content
        self.elements = elements

    async def send(self):
        pass

    async def stream_token(self, token):
        pass

@pytest.fixture
def setup_environment(monkeypatch):
    monkeypatch.setenv("REPLICATE_API_KEY", REPLICATE_API_KEY)
    monkeypatch.setenv("REPLICATE_MODEL", REPLICATE_MODEL)
    monkeypatch.setenv("REPLICATE_MODEL_VERSION", REPLICATE_MODEL_VERSION)

@patch("replicate.Client")
def test_on_chat_start(mock_replicate_client, setup_environment):
    with patch('chainlit.user_session.set') as mock_set:
        cl.run_sync(on_chat_start())
        mock_set.assert_called_with("REPLICATE_CLIENT", mock_replicate_client.return_value)

@requests_mock.Mocker()
def test_upload_image(mock_request, setup_environment):
    mock_request.post("https://dreambooth-api-experimental.replicate.com/v1/upload/filename.png", json={
        "upload_url": "https://example.com/upload",
        "serving_url": "https://example.com/serving"
    })
    mock_request.put("https://example.com/upload", status_code=200)

    image_url = upload_image("test_image.png")
    assert image_url == "https://example.com/serving"

@patch("replicate.Client")
@patch('main.upload_image', return_value="https://example.com/serving")
def test_main_with_image(mock_upload_image, mock_replicate_client, setup_environment):
    message = MockMessage(content="Describe this image", elements=[MagicMock(mime="image/png", path="test_image.png")])
    user_session.set("MESSAGE_HISTORY", [])
    user_session.set("REPLICATE_CLIENT", mock_replicate_client)

    with patch('chainlit.user_session.get') as mock_get:
        with patch('chainlit.user_session.set') as mock_set:
            mock_get.side_effect = lambda key: user_session.get(key)
            with patch('main.cl.Message.send') as mock_send:
                cl.run_sync(main(message))
                mock_send.assert_called()

@patch("replicate.Client")
def test_main_without_image(mock_replicate_client, setup_environment):
    message = MockMessage(content="Tell me a joke")
    user_session.set("MESSAGE_HISTORY", [])
    user_session.set("REPLICATE_CLIENT", mock_replicate_client)

    with patch('chainlit.user_session.get') as mock_get:
        with patch('chainlit.user_session.set') as mock_set:
            mock_get.side_effect = lambda key: user_session.get(key)
            with patch('main.cl.Message.send') as mock_send:
                cl.run_sync(main(message))
                mock_send.assert_called()
