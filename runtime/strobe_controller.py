import serial
import time
import sys

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

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = SERIAL_PORT
        
    print(f"Connecting to {port}...")
    ser = get_serial_connection(port)
    
    if ser:
        try:
            while True:
                cmd = input("Enter '1' to ON, '0' to OFF, 'q' to quit: ").strip()
                if cmd == '1':
                    turn_on(ser)
                elif cmd == '0':
                    turn_off(ser)
                elif cmd.lower() == 'q':
                    break
        except KeyboardInterrupt:
            pass
        finally:
            ser.close()
            print("\nConnection closed.")
