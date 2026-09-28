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
    PI_TX->>PI_TX: Encrypt data
    PI_TX->>ESP_TX: Send binary data over UART

    Note over ESP_TX: Packet Preparation
    ESP_TX->>ESP_TX: Receive binary data
    ESP_TX->>ESP_TX: Split into sequential packets
    ESP_TX->>ESP_TX: Add checksum (CRC-32)

    Note over ESP_TX,ESP_RX: ESP-NOW Transmission Phase
    loop For each packet
        ESP_TX->>RF: Transmit packet via ESP-NOW
        RF->>ESP_RX: Deliver packet

        alt Checksum valid
            ESP_RX->>ESP_RX: Verify checksum (CRC-32)
            ESP_RX->>ESP_RX: Check sequence number
            ESP_RX->>ESP_RX: Buffer packet
            ESP_RX->>RF: Transmit ACK
            RF->>ESP_TX: Deliver ACK
            ESP_TX->>ESP_TX: Remove packet from retransmission queue

            alt Missing packets detected
                ESP_RX->>RF: Transmit NACKs
                RF->>ESP_TX: Deliver NACKs
                ESP_TX->>RF: Retransmit missing packets
                RF->>ESP_RX: Deliver retransmitted packets
            end

        else Checksum invalid
            ESP_RX->>RF: Transmit NACK
            RF->>ESP_TX: Deliver NACK
            ESP_TX->>RF: Retransmit packet
            RF->>ESP_RX: Deliver retransmitted packet
        end
    end

    Note over ESP_TX,ESP_RX: Timeout Handling
    alt ACK timeout expires
        ESP_TX->>RF: Retransmit missing packets
        RF->>ESP_RX: Deliver retransmission
    end

    Note over ESP_RX: Data Reconstruction
    ESP_RX->>ESP_RX: Verify all packets received
    ESP_RX->>ESP_RX: Reorder packets by sequence number
    ESP_RX->>ESP_RX: Reconstruct original encrypted data
    ESP_RX->>PI_RX: Send encrypted data over UART

    Note over PI_RX: Data Processing
    PI_RX->>PI_RX: Decrypt data
    PI_RX->>PI_RX: Validate final checksum
    PI_RX->>PI_RX: Form original image
```