# Death Star Intelligence Gathering

DSIG, or Death Star Intelligence Gathering, is our senior project at Wright State University, for Fall 2026/Spring 2027.

## Team Members

|         Major          | Name                   |
| :--------------------: | ---------------------- |
| Electrical Engineering | Kwaku Nhyira Sefa-Badu |
|  Computer Engineering  | Marcus Gigandet        |
|    Computer Science    | Sean McMeans           |
|    Computer Science    | Joseph Smith           |
|    Computer Science    | Prince Patel           |

## Building the Project

### RCP

The RCP is split into two executables, the ESP32 and Raspberry Pi, and uses libraries for sharing code between the two devices. The dev container was made specifically for creating a pre-defined environment for the ESP32. This dev container may be used to build the ESP32 firmware, erase the firmware, and flash it onto the ESP32s.

#### ESP32

The dev container starts without either ESP32 attached. To flash or erase a board, attach it to the host and start the optional serial bridge from a **host terminal** in the repository root:

```bash
python3 .devcontainer/host/usb.py start
```

The bridge detects up to two ESP32 serial adapters. Run `python3 .devcontainer/host/usb.py status` on the host to see which board is connected.

Inside the dev container, build with the `esp32-debug` or `esp32-release` CMake preset. Use the `flash-1`, `flash-2`, `erase-1`, or `erase-2` CMake targets for connected boards. The targets `flash-all` and `erase-all` may be used to perform the task on both boards.

#### Raspberry Pi

The Raspberry Pi portion of the project can be built in or outside of the devcontainer. It may be built using the `rpi-debug` or `rpi-release` CMake presets.