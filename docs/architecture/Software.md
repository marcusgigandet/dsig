# Software Architecture

```mermaid
swimlane-beta LR
    subgraph Pi_1["Raspberry Pi Private Server"]
        ImageDetection
        Encryption
        UART_1["UART"]

        ImageDetection --> Encryption --> UART_1
    end

    subgraph ESP_1["ESP-32 Transmitter"]
        UART_2["UART"]
        RF_1["ESP-NOW"]
        UART_1 <--> UART_2
        UART_2 --> RF_1
    end

    subgraph ESP_2["ESP-32 Receiver"]
        UART_3["UART"]
        RF_2["ESP-NOW"]
        RF_1 <--> RF_2
        RF_2 --> UART_3
    end

    subgraph Pi_2["Raspberry Pi Rebel Server"]
        UART_4["UART"]
        BACK["Web backend"]
        
        UART_3 <--> UART_4
        UART_4 --> Decryption
    end

    subgraph MBL["Mobile Device"]
        BROWSE["Web browser"]
        AUTH["Authentication App"]

        BACK -- Web page code --> BROWSE
        BROWSE --> BACK
    end
```
