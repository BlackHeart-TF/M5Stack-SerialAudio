import serial
import binascii

# Configuration for your serial port
SERIAL_PORT = '/dev/ttyUSB0'  # Adjust this to your serial port, e.g., 'COM3' on Windows
BAUD_RATE = 115200

def main():
    # Open the serial port
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        print("Opened serial port:", SERIAL_PORT)
        
        try:
            while True:
                # Read a single byte
                data = ser.read(4)
                
                # If data is received, print it in hex format
                if data:
                    hex_data = binascii.hexlify(data).decode('utf-8')
                    print(f"Received byte: {hex_data}")
                    
        except KeyboardInterrupt:
            print("Program terminated by user")
        finally:
            print("Closing serial port")

if __name__ == "__main__":
    main()
