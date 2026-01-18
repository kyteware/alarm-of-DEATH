import os
import json
from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='.env')

print("Starting Unified Python Server...")

app = Flask(__name__)

# State
STATE = {"trigger": False}

# Discord Configuration
PUBLIC_KEY = os.getenv('PUBLIC_KEY')
if not PUBLIC_KEY:
    print("WARNING: PUBLIC_KEY not found in .env. Discord interactions will fail verification.")
else:
    from nacl.signing import VerifyKey
    from nacl.exceptions import BadSignatureError
    print("Public Key loaded.")

# --- Helper Functions ---
def verify_discord_request(req):
    signature = req.headers.get('X-Signature-Ed25519')
    timestamp = req.headers.get('X-Signature-Timestamp')
    
    if not signature or not timestamp:
        print("Missing signature headers")
        return False
        
    try:
        verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
        verify_key.verify(f'{timestamp}{req.data.decode("utf-8")}'.encode(), bytes.fromhex(signature))
        return True
    except BadSignatureError:
        print("Bad signature")
        return False
    except Exception as e:
        print(f"Verification error: {e}")
        return False

# --- Routes ---

@app.route("/", methods=["GET"])
def home():
    return "Server is running!"

@app.route("/trigger", methods=["GET"])  
def get_trigger():
    # print(f"Polling check... Current state: {STATE['trigger']}") # Uncomment for verbose polling logs
    return jsonify({"run": STATE["trigger"]})

@app.route("/fire", methods=["POST"])
def fire():
    STATE["trigger"] = True
    print(">>> MANUAL TRIGGER FIRED! State set to True.")
    return {"status": "fired"}

@app.route("/reset", methods=["POST"])
def reset():
    STATE["trigger"] = False
    print(">>> Trigger reset. State set to False.")
    return {"status": "reset"}

@app.route("/interactions", methods=["POST"])
def interactions():
    if not verify_discord_request(request):
        abort(401, 'invalid request signature')

    data = request.json
    type_ = data.get('type')

    if type_ == 1: # InteractionType.PING
        return jsonify({"type": 1}) # InteractionResponseType.PONG
    
    if type_ == 2: # InteractionType.APPLICATION_COMMAND
        name = data.get('data', {}).get('name')
        
        if name == 'test':
            return jsonify({
                "type": 4, # CHANNEL_MESSAGE_WITH_SOURCE
                "data": {
                    "content": "Hello world from Camera Server! 🐍"
                }
            })
            
        if name == 'send_image':
            STATE["trigger"] = True
            print(">>> DISCORD COMMAND TRIGGER FIRED!")
            return jsonify({
                "type": 4, 
                "data": {
                    "content": "Triggering the camera! Watch out... 📸"
                }
            })

    return jsonify({"error": "unknown command"}), 400

if __name__ == "__main__":
    print("Starting Camera/Discord Server on Port 5001...")
    # CHANGED PORT TO 5001 to avoid conflict with history logger
    app.run(port=5001)
