import serial
import time
import sys
import asyncio

# Configure this to match your Arduino's serial port
# On Linux, it's often /dev/ttyUSB0 or /dev/ttyACM0
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600

def get_serial_connection(port=SERIAL_PORT, baud=BAUD_RATE):
    try:
        ser = serial.Serial(port, baud, timeout=1)
        # Wait for Arduino to reset/initialize
        time.sleep(2) 
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port {port}: {e}")
        return None

def wipe(ser):
    if ser and ser.is_open:
        ser.write(b'WIPE')
        print("wiping")

async def wipe_sequence():
    """
    Async function that handles the full lifecycle:
    Connect -> On -> Wait 2s -> Off -> Close
    """
    def _run_sync():
        print(f"Connecting to table wiper at {SERIAL_PORT}...")
        ser = get_serial_connection()
        if ser:
            wipe(ser)
            ser.close()
            print("Wipe sequence complete.")
        else:
            print("Failed to connect to table wiper.")
    
    # Offload entire blocking sequence (connection, sleep) to a thread
    await asyncio.to_thread(_run_sync)

def wipe_tool():
    """
    Fire-and-forget function to be called from the main loop.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(wipe_sequence())
        print("Wipe task scheduled!")
    except RuntimeError:
        print("No running event loop to schedule table wipe task!")

if __name__ == "__main__":
    # Test async function
    print("Testing wipe sequence...")
    asyncio.run(wipe_sequence())
