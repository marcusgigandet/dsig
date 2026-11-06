"""Register the project's RFC2217 client for ESP-IDF tools."""

import serial

# Insert the module into the serial packages
if __name__ not in serial.protocol_handler_packages:
    serial.protocol_handler_packages.insert(0, __name__)
