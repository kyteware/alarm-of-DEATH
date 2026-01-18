import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

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
    image_url = "https://picsum.photos/400/300" 
    send_image(image_url, "Automatic wake up call!")
