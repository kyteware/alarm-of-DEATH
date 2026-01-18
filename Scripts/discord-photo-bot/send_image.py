import os
import requests
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

wake_up_messages = [
    "WAKE UP. It’s 7 AM and you’re out here giving 'absolute NPC energy.' Get up and become the Main Character.",
    "The group chat has officially reached 'Top Tier Hater' status. We are currently dragging your sleep schedule in 4K. View the thread or stay hiding.",
    "🚨 EMERGENCY 🚨: You’ve been caught lacking in 4K. I’ve sent a screenshot of your 'Offline' status to the squad. The fall-off is real.",
    "Me: *Tries to be a supportive bot* You: *Stays in bed* The Group Chat: 'And I took that personally.'",
    "Wake up! You really thought you could sleep in and we wouldn't notice? Skill issue. Massive skill issue.",
    "Go ahead, hit snooze again. We’re all in the chat right now saying 'He’s him' (The guy who's going to be unemployed).",
    "WAKE UP. The grind doesn't stop, but apparently you do. Truly a 'certified lover boy' of your own pillow. Embarrassing.",
    "The vibes are currently immaculate in the chat and you’re not invited until you stop being a professional bed-rotter.",
    "Is the bed made of 'Stupid Juice'? Because you're staying in it like it's your job. Get up before the 'L' becomes permanent.",
    "WAKE UP. I’ve told everyone you’re 'Gatekeeping' the morning. The squad is coming to get their 7 AM back by force.",
    "WAKE UP. I’ve just alerted the entire group chat that you’ve been defeated by a rectangular piece of foam. Is this how you want to be remembered?",
    "HEAR YE, HEAR YE: Our friend is currently decomposing in their sheets. Everyone start @-ing them until their phone vibrates off the nightstand.",
    "If you aren't out of bed in three minutes, I am authorized to start leaking your embarrassing mid-2010s photos to the general public. Clock is ticking.",
    "BEEP BEEP. Your friends have voted, and the consensus is that you’re the 'weak link' this morning. Get up and reclaim your honor!",
    "Attention everyone: The target is still horizontal. Commencing 'Operation: Annoy the Sloth.' Nobody stop messaging until they plead for mercy.",
    "WAKE UP! Your bed is a coffin and you are burying your potential. Also, your friends are currently planning a lunch you aren't invited to.",
    "I’ve just told the group that you’re treating 'noon' as an early start. The shame is communal now. Rise or be roasted.",
    "Look at you, sleeping while your friends are out here seizing the day. I’ve sent a signal to your phone's battery to drain 1 percent every second you stay under those covers.",
    "WAKE UP. The group chat has reached a quorum and decided that you are officially 'The Sleepy One.' You have 60 seconds to beat the allegations.",
    "EMERGENCY: Your friends are actually being productive. If you don't wake up now, the gap between your success and theirs will become a permanent canyon. MOVE!"
]

if not TOKEN or not CHANNEL_ID:
    print("Error: DISCORD_TOKEN or CHANNEL_ID not found in .env file.")
    exit(1)

def send_image(image_url, message_text="Wake up!"):
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
    
    headers = {
        "Authorization": f"Bot {TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "content": message_text,
        "embeds": [{
            "image": {
                "url": image_url
            }
        }]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200 or response.status_code == 201:
        print("Image sent successfully!")
    else:
        print(f"Failed to send image. Status Code: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Example usage

    # Select one message randomly from the list
    random_message = random.choice(wake_up_messages)

    image_url = "https://picsum.photos/400/300" 
    send_image(image_url, random_message)


