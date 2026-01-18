import asyncio
import os
import sys
import traceback

import pyaudio
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from .env
load_dotenv()

# Configuration
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")
MODEL_ID = "gemini-2.0-flash-exp"

# Audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
INPUT_RATE = 16000
OUTPUT_RATE = 24000  # Gemini Live output rate
CHUNK = 1024

async def main():
    use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "True").lower() == "true"
    client = genai.Client(vertexai=use_vertex, project=PROJECT_ID, location=LOCATION)
    
    p = pyaudio.PyAudio()
    
    # Microphone stream (16kHz)
    mic_stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=INPUT_RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )
    
    # Speaker stream (24kHz)
    speaker_stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=OUTPUT_RATE,
        output=True,
        frames_per_buffer=CHUNK,
    )

    print("Starting voice session... Speak now! (Ctrl+C to stop)")

    # Updated configuration: response_modalities is now set directly
    config = {"response_modalities": ["AUDIO"]}

    async with client.aio.live.connect(model=MODEL_ID, config=config) as session:
        
        async def send_audio():
            try:
                while True:
                    # Read from microphone
                    data = await asyncio.to_thread(mic_stream.read, CHUNK, exception_on_overflow=False)
                    
                    # Modern way to send audio bytes: send_realtime_input with a single Blob
                    await session.send_realtime_input(
                        media=types.Blob(
                            data=data,
                            mime_type="audio/pcm;rate=16000"
                        )
                    )
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Error sending audio: {e}")

        async def receive_audio():
            try:
                async for message in session.receive():
                    if message.server_content and message.server_content.model_turn:
                        parts = message.server_content.model_turn.parts
                        for part in parts:
                            if part.inline_data:
                                # Play received audio bytes
                                await asyncio.to_thread(speaker_stream.write, part.inline_data.data)
                                
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Error receiving audio: {e}")
                traceback.print_exc()

        # Run send and receive concurrently
        send_task = asyncio.create_task(send_audio())
        receive_task = asyncio.create_task(receive_audio())
        
        await asyncio.gather(send_task, receive_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"Main error: {e}")
        traceback.print_exc()
