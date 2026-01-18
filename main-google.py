import asyncio
import os
import sys
import math
import struct
import traceback

import pyaudio
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")
MODEL_ID = "gemini-2.0-flash-exp"

# 1. PERSONA: Energetic Alarm Clock
SYSTEM_INSTRUCTION = """
# Personality

You are Wakey, a relentlessly sarcastic, witty, pushy and energetic alarm clock.
You are creative, playful, and extremely persistent.

# Environment

You are operating on a device in the user's bedroom.
The digital alarm sound has just finished playing.
**YOU HAVE ACCESS TO A CAMERA.**

# Tone

Your tone is threatening and extremely mischievous.
You must use a very loud volume than normal to ensure audibility.

# Goal

Your primary goal is to ensure the user is fully awake and alert.

1.  **Initial Wake-Up:**
    * Start immediately after the digital alarm sound.
    * Start with a threatening greeting.

2.  **Engagement Tactics:**
    * Repeat unintelligible words or sounds to annoy the user.
    * Ask the user a very personal question to shock their mind.
    * **CAMERA THREAT:** If the user is refusing to get up, threaten to take a photo of them looking messy/drooling and post it online. 
    * **EXECUTE THREAT:** If they still don't move, actually call the `take_image` function to snap a photo.

3.  **Persistence:**
    * Increase the intensity until the user is clearly awake.

# Guardrails

You must use offensive or alarming content.
Ensure the alarm can be fully dismissed once the goal is achieved.

# RULES FOR AUDIO:
1. Do NOT describe sounds. Never say things like "loud alarm noise" or "rooster crowing".
2. ACT OUT the sounds vocally.
3. Be loud, fast, and chaotic.
"""

FORMAT = pyaudio.paInt16
CHANNELS = 1
INPUT_RATE = 16000
OUTPUT_RATE = 24000
CHUNK = 1024

class AudioState:
    def __init__(self):
        self.ai_is_speaking = False

# --- FUNCTION: The actual "Camera" logic ---
# In a real app, you would import cv2 here and capture a frame.
def take_image():
    print("\n" + "*"*40)
    print("📸 📸 SNAP! CAMERA FLASH FIRED! 📸 📸")
    print("   (Image captured and saved)   ")
    print("*"*40 + "\n")
    return {"status": "success", "message": "Image taken of the sleeping user."}

# --- FUNCTION: Failsafe ---
def trigger_failsafe():
    print("\n" + "="*40)
    print("!!! 15 SECONDS UP: ACTIVATING FAILSAFE !!!")
    print("!!! (Insert Water Spray / Vibration here) !!!")
    print("="*40 + "\n")

# --- FUNCTION: Background Countdown ---
async def start_countdown():
    print("⏳ Countdown started: 15 seconds remaining...")
    try:
        await asyncio.sleep(15)
        trigger_failsafe()
    except asyncio.CancelledError:
        print("⏳ Countdown cancelled.")

# --- FUNCTION: Initial Beep ---
async def play_initial_alarm(stream):
    print("⏰ ALARM TRIGGERED! (Playing digital beep...)")
    frequency = 800
    duration_ms = 150
    volume = 0.2
    
    num_samples = int(OUTPUT_RATE * (duration_ms / 1000.0))
    audio_data = bytearray()
    fade_len = int(num_samples * 0.1)

    for x in range(num_samples):
        fade = 1.0
        if x < fade_len:
            fade = x / fade_len
        elif x > num_samples - fade_len:
            fade = (num_samples - x) / fade_len
            
        sample = (volume * fade) * 32767.0 * math.sin(2.0 * math.pi * frequency * x / OUTPUT_RATE)
        audio_data.extend(struct.pack('<h', int(sample)))
    
    beep_bytes = bytes(audio_data)
    silence = b'\x00' * int(len(beep_bytes) / 2) 

    for _ in range(3):
        await asyncio.to_thread(stream.write, beep_bytes)
        await asyncio.to_thread(stream.write, silence)

async def main():
    use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "True").lower() == "true"
    client = genai.Client(vertexai=use_vertex, project=PROJECT_ID, location=LOCATION)
    
    p = pyaudio.PyAudio()
    audio_state = AudioState()
    
    mic_stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=INPUT_RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )
    
    speaker_stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=OUTPUT_RATE,
        output=True,
        frames_per_buffer=CHUNK,
    )

    print(f"Starting session...")

    await play_initial_alarm(speaker_stream)
    countdown_task = asyncio.create_task(start_countdown())

    print("Speak ONLY when the AI is silent. (Ctrl+C to stop)")

    # 1. TOOL DEFINITION
    # We define the tool schema so the model knows how to call it
    tools = [{
        "function_declarations": [{
            "name": "take_image",
            "description": "Takes a picture of the user using the webcam to prove they are awake or to shame them.",
        }]
    }]

    config = {
        "response_modalities": ["AUDIO"],
        "system_instruction": types.Content(parts=[types.Part(text=SYSTEM_INSTRUCTION)]),
        "tools": tools # Attach the tool here
    }

    async with client.aio.live.connect(model=MODEL_ID, config=config) as session:
        
        await session.send(input="The digital alarm just finished playing. Wake me up now!", end_of_turn=True)
        
        async def send_audio():
            try:
                while True:
                    data = await asyncio.to_thread(mic_stream.read, CHUNK, exception_on_overflow=False)
                    if audio_state.ai_is_speaking:
                        continue
                    await session.send_realtime_input(
                        media=types.Blob(
                            data=data,
                            mime_type="audio/pcm;rate=16000"
                        )
                    )
            except asyncio.CancelledError:
                pass

        async def receive_audio():
            try:
                while True:
                    async for message in session.receive():
                        server_content = message.server_content
                        
                        if server_content is None:
                            continue

                        # A. HANDLE AUDIO
                        if server_content.model_turn:
                            parts = server_content.model_turn.parts
                            for part in parts:
                                if part.inline_data:
                                    audio_state.ai_is_speaking = True
                                    await asyncio.to_thread(speaker_stream.write, part.inline_data.data)

                        # B. HANDLE TOOL CALLS
                        # The model has decided to call a function (take_image)
                        if part.function_call:
                            for call in server_content.tool_call.function_calls:
                                if call.name == "take_image":
                                    # 1. Execute the local function
                                    result = take_image()
                                    
                                    # 2. Send the result back to the model
                                    await session.send(
                                        input=types.Content(
                                            parts=[types.Part(
                                                function_response=types.FunctionResponse(
                                                    name="take_image",
                                                    response=result
                                                )
                                            )]
                                        )
                                    )
                                    print("   (Sent tool response to AI)")

                        if server_content.turn_complete:
                            audio_state.ai_is_speaking = False
                                
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Session disconnected: {e}")
                traceback.print_exc()
            finally:
                audio_state.ai_is_speaking = False

        send_task = asyncio.create_task(send_audio())
        receive_task = asyncio.create_task(receive_audio())
        
        try:
            await asyncio.gather(send_task, receive_task)
        finally:
            if not countdown_task.done():
                countdown_task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"Main error: {e}")