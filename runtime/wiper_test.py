from wiper import Wiper
from pynput.keyboard import Key, Listener

print("Setting up...")
arduino = Wiper('/dev/ttyACM0')
if not arduino.connect():
  print("Arduino not found")
  exit

print ("Reading response...")
response = arduino.read_response()
print(f"Arduino says: {response}")

def show(key):
    if key == "w":
      print(arduino.send_command("WIPE"))
        
    # by pressing 'delete' button 
    # you can terminate the loop 
    if key == Key.delete: 
        arduino.close()
        return False

# Collect all event until released
with Listener(on_press = show) as listener:
    listener.join()