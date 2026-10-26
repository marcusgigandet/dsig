# Radio Communication Protocol (RCP)

The RCP is designed to operate on the Raspberry Pi 4B and interact with the ESP-32 over UART, using ESP-NOW to perform the radio communication.

## Packet Design

The RCP uses a structured packet format to perform reliable data transmission between devices. Each packet contains a standardized header followed by a variable-length data field.

The packet format is outlined below:

```mermaid
---
title: "RF Packet"
---
packet
0-15: "Sequence Number"
16-31: "Acknowledgment Number"
32-35: "Data Offset"
36-43: "Flags"
44-51: "Type"
52-63: "Reserved"
64-79: "Reserved"
80-95: "Payload Length"
96-127: "CRC-32"
128-255: "Data (variable length)"
```

The section marked reserved is designed to allow future design implementations.

## RF Link Analysis

The following sequence illustrates the transmission and reception process. The transmitter splits the payload into packets and generates header information, including but not limited to the sequence number and  checksum.

**Note**: Some logic may need to be refined when we actually implement this.

```mermaid
sequenceDiagram
    participant PI_TX as Raspberry Pi 1
    participant ESP_TX as ESP32 Transmitter
    participant RF as ESP-NOW RF Link
    participant ESP_RX as ESP32 Receiver
    participant PI_RX as Raspberry Pi 2

    Note over PI_TX: Data Preparation
    PI_TX->>PI_TX: Calculate image checksum
    PI_TX->>PI_TX: Encrypt and segment image data

    Note over PI_TX,ESP_TX: UART Transfer

    loop While data remains
        ESP_TX->>PI_TX: Advertise available buffer capacity
        PI_TX->>ESP_TX: Send bounded batch of UART frames
        Note over PI_TX,ESP_TX: Final data frame carries EOI flag
        ESP_TX->>ESP_TX: Validate UART CRC
        ESP_TX->>ESP_TX: Build RF packets with CRC
    end
    
    Note over ESP_TX,ESP_RX: ESP-NOW Transmission
    loop For each queued packet
        ESP_TX->>RF: Transmit packet
        RF->>ESP_RX: Deliver packet

        ESP_RX->>ESP_RX: Verify CRC-32

        alt Checksum valid
            ESP_RX->>ESP_RX: Check sequence number

            alt New packet
                ESP_RX->>PI_RX: Forward packet over UART
                Note over ESP_RX,PI_RX: Final data frame carries EOI flag
                PI_RX->>PI_RX: Validate UART CRC
                PI_RX->>PI_RX: Store by sequence number
            end

            ESP_RX->>RF: Send ACK
            RF->>ESP_TX: Deliver ACK
            ESP_TX->>ESP_TX: Remove from retransmission queue

            opt Missing sequence detected
                ESP_RX->>RF: Send NACK for missing packet
                RF->>ESP_TX: Deliver NACK
            end

        else Checksum invalid
            ESP_RX->>RF: Send NACK
            RF->>ESP_TX: Deliver NACK
        end

        opt NACK received or ACK timeout
            ESP_TX->>RF: Retransmit affected packet
        end
    end

    Note over PI_RX: Image Reconstruction
    PI_RX->>PI_RX: Reorder packets
    PI_RX->>PI_RX: Reconstruct and decrypt image
    PI_RX->>PI_RX: Validate final image checksum
```