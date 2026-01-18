import requests

print("Firing Camera Trigger...")
try:
    # Notice Port 5001 for Camera Server
    response = requests.post("http://localhost:5001/fire")
    if response.status_code == 200:
        print("Trigger fired successfully! Monitor (send_image.py) should wake up soon.")
    else:
        print(f"Failed to fire trigger. Status: {response.status_code}")
except Exception as e:
    print(f"Error connecting to server: {e}")
    print("Is server.py running on port 5001?")
