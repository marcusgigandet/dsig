# Software Architecture

```mermaid
swimlane-beta TB
    subgraph Pi_1["Raspberry Pi Private Server"]
        IMAGE_DETECTION["Image Detection"]
        Encryption

        IMAGE_DETECTION --> Encryption
    end

    subgraph ESP_1["ESP-32 Transmitter"]
        TX["RCP"]
    end

    subgraph ESP_2["ESP-32 Receiver"]
        RX["RCP"]
    end

    subgraph Pi_2["Raspberry Pi Rebel Server"]
        Decryption
        BACKEND["`**Web Backend**`"]

        Decryption -- Images --> BACKEND
    end

    subgraph MBL["Mobile Device"]
        BROWSE["Web browser"]
        AUTH["`**Authentication App**`"]

        BROWSE -- Secret key --> AUTH
        AUTH -- TOTP --> BROWSE
    end

    Encryption <-- UART --> TX
    TX <-. ESP-NOW .-> RX
    RX <-- UART --> Decryption

    BACKEND -- Web page source code --> BROWSE
    BROWSE -- HTTP Request --> BACKEND
```
