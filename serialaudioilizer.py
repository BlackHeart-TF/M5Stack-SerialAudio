import sys
import serial
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt, QTimer

# Configure this with your serial port details
SERIAL_PORT = '/dev/ttyUSB1'  # or '/dev/ttyUSB0' on Unix
BAUD_RATE = 115200

start_sequence = bytearray([0x66, 0x92, 0x66])



class AudioVisualizer(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Audio Visualizer")
        self.resize(400, 200)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.samples = [0] * 200  # Adjust based on your visualization needs
        self.data_buffer = bytearray()

        # Set up serial connection
        self.serial = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        
        # Set up a timer to periodically update the plot
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_serial_data)
        self.timer.start(100)  # Adjust interval for your data rate

    def read_serial_data(self):
        # Ensure there's data waiting to be read
        if self.serial.in_waiting:
            # Read available data
            bytes_to_read = self.serial.in_waiting
            raw_data = self.serial.read(bytes_to_read)
            
            # Append the newly read data to the buffer
            self.data_buffer += raw_data

            i = 0  # Start from the beginning of the new data
            while i < len(self.data_buffer) - 3:  # Ensure there's enough data for the structure
                if self.data_buffer[i] == 0x00 and self.data_buffer[i + 3] == 0xFF:
                    # Structure matches, process as valid data
                    lb = self.data_buffer[i + 1]
                    hb = self.data_buffer[i + 2]
                    sample = int.from_bytes([lb, hb], byteorder='little', signed=True)

                    print(f"Raw Bytes: {str([lb, hb]).rjust(10, ' ')}, Sample: {str(sample).rjust(10, ' ')}") 

                    self.samples.append(sample)
                    if len(self.samples) > 200:  # Keep the sample buffer size constant
                        self.samples.pop(0)

                    i += 4  # Move past this sample in the buffer
                else:
                    i += 1  # Structure not matched, shift by one and try again

            # Remove processed data up to the last checked position, keeping potential partial sample
            self.data_buffer = self.data_buffer[i:]

            self.update()  # Update UI or processing state as needed


    def paintEvent(self, event):
        painter = QPainter(self)  # Assuming you want to paint directly on this widget
        pen = QPen(Qt.blue, 2)
        painter.setPen(pen)

        w, h = self.width(), self.height()
        prev_x, prev_y = 0, h // 2
        for i, sample in enumerate(self.samples):
            x = i * (w / len(self.samples))
            # Adjusting sample normalization for signed 16-bit audio
            y = (h / 2) + (sample / 65535.0) * (h*1.3)  # Normalize sample to window height
            painter.drawLine(prev_x, prev_y, int(x), int(y))
            prev_x, prev_y = int(x), int(y)
        painter.end()  # Good practice

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioVisualizer()
    window.show()
    sys.exit(app.exec())
