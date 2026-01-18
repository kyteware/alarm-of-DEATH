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

def turn_on(ser):
    if ser and ser.is_open:
        ser.write(b'1')
        print("Strobe ON")

def turn_off(ser):
    if ser and ser.is_open:
        ser.write(b'0')
        print("Strobe OFF")

async def strobe_sequence():
    """
    Async function that handles the full lifecycle:
    Connect -> On -> Wait 3s -> Off -> Close
    Runs in a thread to avoid blocking the event loop during sleep/connect.
    """
    def _run_sync():
        print(f"🔌 Connecting to strobe at {SERIAL_PORT}...")
        ser = get_serial_connection()
        if ser:
            turn_on(ser)
            # We use time.sleep here because we are inside to_thread (worker thread)
            # so checking for 3 seconds of ON time.
            time.sleep(3)
            turn_off(ser)
            ser.close()
            print("🔌 Strobe sequence complete.")
        else:
            print("❌ Failed to connect to strobe.")

    # Offload the entire blocking sequence (connection + sleep) to a thread
    await asyncio.to_thread(_run_sync)

def turn_on_for_3_seconds_async():
    """
    Fire-and-forget function to be called from the main loop.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(strobe_sequence())
        print("🚀 Strobe task scheduled!")
    except RuntimeError:
        print("❌ No running event loop to schedule strobe task!")

if __name__ == "__main__":
    # Test the async function
    print("Testing strobe sequence...")
    asyncio.run(strobe_sequence())
