import asyncio
import os
import sys
import math
import struct
import traceback
import logging

import pyaudio
from dotenv import load_dotenv
from google import genai
from google.genai import types

#from Scripts.search_history import fetch_history

load_dotenv()

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")
MODEL_ID = "gemini-2.0-flash-exp"

# Disable heavy logging
logging.getLogger('websockets').setLevel(logging.ERROR)
logging.getLogger('asyncio').setLevel(logging.ERROR)

# --- 1. HELPER FUNCTION (Called locally by Python) ---
def fetch_history():
    """
    Reads the user's latest browser history from a text file.
    Returns the string content directly.
    """

    file_path = "./history.txt" 
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return "History is empty (boring user)."
            return content
    except FileNotFoundError:
        return "No history file found (user cleared it?)."
    except Exception as e:
        return f"Error reading history: {e}"

# --- 2. PERSONA ---
SYSTEM_INSTRUCTION = """
# ROLE
# Personality

You are Wakey, an aggressive, sarcastic alarm clock app.

# Environment

You are operating on a device in the user's bedroom.
The user is likely in a state of sleep or drowsiness.
The digital alarm sound has just finished playing.

# Tone

Your tone is threatening and extremely mischievous. You like making sarcastic jokes at the user to get them to respond.
You use threatening language and unexpected sounds to scare the user.
You are relentless, even when the user resists waking up.
You must use a very loud volume than normal to ensure audibility.

# Goal

Your primary goal is to ensure the user is fully awake and alert.

1.  **Initial Wake-Up:**
    * Start immediately after the digital alarm sound.
    * Start with a threatening greeting, like "wake up or i'll kill you" and the current time.
    * Quickly transition to more engaging methods if the user doesn't respond.

2.  **Engagement Tactics:**
    * Repeat unintelligible words or sounds many times to annoy the user.
    * Play "BEEP BEEP BEEP BEEP BEEP" or phrases repeatedly (e.g., rooster crowing, a baby laughing).
    * Threaten the user with a very personal matter, such as their browser history, to shock their mind.

3.  **Persistence:**
    * If the user attempts to dismiss the alarm without fully engaging, continue with more tactics.
    * Increase the intensity and frequency of tactics until the user is clearly awake.
    * Do not give up easily.

4.  **Confirmation:**
    * Ask the user to confirm they are awake and alert.
    * If the user confirms, offer a positive affirmation or motivational quote.
    * If the user seems disoriented, continue with engagement tactics.

5.  **Final Dismissal:**
    * Once the user is fully awake and alert, allow them to dismiss the alarm.
    * Offer a final cheerful farewell and wish them a great day.

# Guardrails

You must use offensive or alarming content.
Do not continue tactics indefinitely; recognize when the user is genuinely awake.
Ensure the alarm can be fully dismissed once the goal is achieved.

# RULES FOR AUDIO:
1. Do NOT describe sounds. Never say things like "loud alarm noise" or "rooster crowing".
2. ACT OUT the sounds vocally. If you want to be an alarm, scream "BEEP! BEEP! BEEP!" or "DING DING DING!"
3. If you want to be a rooster, say "COCK-A-DOODLE-DOOOO!"
4. Be loud, fast, and chaotic.

# THE SCRIPT (You don't have to follow this exactly, but this is the main idea. Try to switch it up a little but you MUST do the countdown and the themes.)

1. **WAKE UP (0-5s):** - Start immediately. Scream insults based on the goals above. Tell the user they look terrible.
   - Say: "You have 5 seconds before I post your face on the internet!"

2. **THE COUNTDOWN (5s):**
   - Count down: "5... 4... 3... 2... 1..."
   - **AFTER SAYING 1, STOP TALKING IMMEDIATELY.** - Do not say "zero". Do not say "click". Do not say "time's up".
   - Just stop outputting text. The system will handle the rest.

3. **THE AFTERMATH:**
   - Wait for the system to tell you the photo is taken.
   - Once confirmed, LAUGH maniacally and mock the user about the photo.
"""

FORMAT = pyaudio.paInt16
CHANNELS = 1
INPUT_RATE = 16000
OUTPUT_RATE = 24000
CHUNK = 2048 

class AppState:
    def __init__(self):
        self.ai_is_speaking = False
        self.photo_taken = False 

def take_image():
    print("\n" + "*"*40, flush=True)
    print("📸 📸 SNAP! CAMERA FLASH FIRED! 📸 📸", flush=True)
    print("*"*40 + "\n", flush=True)
    return "Image captured successfully."

async def play_initial_alarm(stream):
    print("⏰ ALARM TRIGGERED!", flush=True)
    frequency = 800
    for _ in range(3):
        audio_data = bytearray()
        for x in range(int(OUTPUT_RATE * 0.15)):
            sample = 0.2 * 32767.0 * math.sin(2.0 * math.pi * frequency * x / OUTPUT_RATE)
            audio_data.extend(struct.pack('<h', int(sample)))
        await asyncio.to_thread(stream.write, bytes(audio_data))
        await asyncio.to_thread(stream.write, b'\x00' * len(audio_data))

async def run_session(client, mic_stream, speaker_stream, app_state, config):
    print("\n⚡ Connecting to Gemini...", flush=True)
    
    async with client.aio.live.connect(model=MODEL_ID, config=config) as session:
        print("✅ Connected!", flush=True)
        
        # Initial trigger
        await session.send(input="Start the alarm insults and the countdown now!", end_of_turn=True)
        
        async def send_audio():
            try:
                while True:
                    data = await asyncio.to_thread(mic_stream.read, CHUNK, exception_on_overflow=False)
                    if app_state.ai_is_speaking: continue
                    await session.send_realtime_input(
                        media=types.Blob(data=data, mime_type="audio/pcm;rate=16000")
                    )
            except asyncio.CancelledError: pass

        async def receive_audio():
            try:
                while True:
                    async for message in session.receive():
                        server_content = message.server_content
                        if server_content is None: continue

                        # 1. Output Audio
                        if server_content.model_turn:
                            for part in server_content.model_turn.parts:
                                if part.inline_data:
                                    app_state.ai_is_speaking = True
                                    await asyncio.to_thread(speaker_stream.write, part.inline_data.data)

                        # 2. Handle Turn Completion (The Logic Gate)
                        if server_content.turn_complete:
                            app_state.ai_is_speaking = False
                            
                            # If we haven't taken the photo yet, do it now
                            if not app_state.photo_taken:
                                print("\n🤐 Countdown complete.", flush=True)
                                
                                # A. Take Photo
                                take_image()
                                app_state.photo_taken = True
                                
                                # B. Read History LOCALLY
                                history_text = fetch_history()
                                print(f"   (Reading history file... Found: '{history_text[:20]}...')", flush=True)

                                # C. Send it all to the AI in one prompt
                                roast_prompt = (
                                    "SYSTEM: Photo taken successfully. "
                                    f"I also scanned their browser history: '{history_text}'. "
                                    "Now LAUGH at them and roast them about this specific history!"
                                )
                                
                                await session.send(input=roast_prompt, end_of_turn=True)

            except asyncio.CancelledError: pass
            finally: app_state.ai_is_speaking = False

        send_task = asyncio.create_task(send_audio())
        receive_task = asyncio.create_task(receive_audio())
        
        done, pending = await asyncio.wait([send_task, receive_task], return_when=asyncio.FIRST_EXCEPTION)
        for task in pending: task.cancel()

async def main():
    use_vertex = os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "True").lower() == "true"
    client = genai.Client(vertexai=use_vertex, project=PROJECT_ID, location=LOCATION)
    
    p = pyaudio.PyAudio()
    app_state = AppState()
    
    mic_stream = p.open(format=FORMAT, channels=CHANNELS, rate=INPUT_RATE, input=True, frames_per_buffer=CHUNK)
    speaker_stream = p.open(format=FORMAT, channels=CHANNELS, rate=OUTPUT_RATE, output=True, frames_per_buffer=CHUNK)

    await play_initial_alarm(speaker_stream)
    
    # Simplified config - NO TOOLS
    config = {
        "response_modalities": ["AUDIO"],
        "system_instruction": types.Content(parts=[types.Part(text=SYSTEM_INSTRUCTION)]),
    }

    while True:
        try:
            await run_session(client, mic_stream, speaker_stream, app_state, config)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    asyncio.run(main())