import os
import requests
import random
import json
import time
from dotenv import load_dotenv
import cv2

# Load environment variables
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

wake_up_messages = [
    "WAKE UP. It’s 7 AM and you’re out here giving 'absolute NPC energy.' Get up and become the Main Character.",
    "The group chat has officially reached 'Top Tier Hater' status. We are currently dragging your sleep schedule in 4K.",
    "🚨 EMERGENCY 🚨: You’ve been caught lacking in 4K. I’ve sent a screenshot of your 'Offline' status to the squad.",
    "Me: *Tries to be a supportive bot* You: *Stays in bed* The Group Chat: 'And I took that personally.'",
    "Wake up! You really thought you could sleep in and we wouldn't notice? Skill issue. Massive skill issue.",
    "Go ahead, hit snooze again. We’re all in the chat right now saying 'He’s him' (The guy who's going to be unemployed).",
    "WAKE UP. The grind doesn't stop, but apparently you do. Truly a 'certified lover boy' of your own pillow. Embarrassing.",
    "The vibes are currently immaculate in the chat and you’re not invited until you stop being a professional bed-rotter.",
    "Is the bed made of 'Stupid Juice'? Because you're staying in it like it's your job. Get up before the 'L' becomes permanent.",
    "WAKE UP. I’ve told everyone you’re 'Gatekeeping' the morning. The squad is coming to get their 7 AM back by force.",
    "WAKE UP. I’ve just alerted the entire group chat that you’ve been defeated by a rectangular piece of foam.",
    "HEAR YE, HEAR YE: Our friend is currently decomposing in their sheets. Everyone start @-ing them.",
    "If you aren't out of bed in three minutes, I am authorized to start leaking your embarrassing mid-2010s photos.",
    "BEEP BEEP. Your friends have voted, and the consensus is that you’re the 'weak link' this morning.",
    "Attention everyone: The target is still horizontal. Commencing 'Operation: Annoy the Sloth.'",
    "WAKE UP! Your bed is a coffin and you are burying your potential.",
    "I’ve just told the group that you’re treating 'noon' as an early start. The shame is communal now. Rise or be roasted.",
    "Look at you, sleeping while your friends are out here seizing the day. I’ve sent a signal to your phone's battery to drain.",
    "WAKE UP. The group chat has reached a quorum and decided that you are officially 'The Sleepy One.'",
    "EMERGENCY: Your friends are actually being productive. If you don't wake up now, the gap between your success and theirs will become a permanent canyon."
]

if not TOKEN or not CHANNEL_ID:
    print("Error: DISCORD_TOKEN or CHANNEL_ID not found in .env file.")
    exit(1)

def send_image(image_path, message_text="Wake up!"):
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
    
    headers = {
        "Authorization": f"Bot {TOKEN}"
    }
    
    filename = os.path.basename(image_path)
    
    payload = {
        "content": message_text,
        "embeds": [{
            "image": {
                "url": f"attachment://{filename}"
            }
        }]
    }
    
    try:
        with open(image_path, "rb") as f:
            files = {
                "file": (filename, f),
                "payload_json": (None, json.dumps(payload))
            }
            
            response = requests.post(url, headers=headers, files=files)
        
        if response.status_code == 200 or response.status_code == 201:
            print("Image sent successfully!")
        else:
            print(f"Failed to send image. Status Code: {response.status_code}")
            print(response.text)
    except FileNotFoundError:
        print(f"Error: Could not find image file at {image_path}")

def take_image():
    print("Attempting to capture image...")
    # Use 0 (default camera) and CAP_DSHOW on Windows for faster/more reliable access
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cam.isOpened():
        print("Error: Could not open camera.")
        return False

    # Allow camera to warm up
    time.sleep(1)

    ret, frame = cam.read()

    if not ret:
        print("Failed to grab frame")
        cam.release()
        return False

    img_name = "captured_image.png"
    cv2.imwrite(img_name, frame)
    print(f"Captured! Saved as {img_name}")
    
    cam.release()
    return True

# --- Polling Logic ---

def check_trigger():
    try:
        # NOTICE: Port is now 5001
        response = requests.get("http://localhost:5001/trigger")
        if response.status_code == 200:
            data = response.json()
            return data.get("run", False)
    except Exception as e:
        # Don't spam logic with errors if server is down, just wait
        pass
    return False

def reset_trigger():
    try:
        # NOTICE: Port is now 5001
        requests.post("http://localhost:5001/reset")
    except Exception as e:
        print(f"Error resetting trigger: {e}")

if __name__ == "__main__":
    print("📸 Discord Photo Bot Service Started")
    print("Waiting for trigger from server (http://localhost:5001)...")
    
    tick = 0
    while True:
        tick += 1
        if tick % 5 == 0: # Print a heartbeat every ~10 seconds
            print("... Monitor is alive and polling ...")

        if check_trigger():
            print("Trigger received! Taking photo...")
            
            # Take and save photo
            if take_image():
                # Select random message
                random_message = random.choice(wake_up_messages)
                image_path = "captured_image.png" 

                # Send to Discord
                send_image(image_path, random_message)
            else:
                print("Failed to take photo, skipping send.")
            
            # Reset the trigger so we don't loop forever
            reset_trigger()
            
        
        # Sleep to avoid hammering the server
        time.sleep(2)
