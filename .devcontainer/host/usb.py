"""Discover and share two ESP32 serial adapters with the dev container.

Each detected adapter is bridged into the dev container over RFC 2217
(``rfc2217://host.docker.internal:4000+board``) by a background supervisor
process that is controlled through a local TCP socket.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import venv
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

ROOT: Path = Path(__file__).resolve().parents[2]
"""Repository root directory."""

STATE: Path = ROOT / ".cache" / "esp32-usb"
"""State directory holding the venv, bridge log, and board mapping."""

CONTROL: Tuple[str, int] = ("127.0.0.1", 3999)
"""Control socket address of the bridge supervisor."""

VENDORS: Set[int] = {0x10C4, 0x1A86, 0x0403, 0x303A}
"""USB vendor IDs treated as ESP32-capable serial adapters
(CP210x, CH34x, FTDI, Espressif).
"""


Detection = Tuple[str, str]
"""``(identity, host serial device)`` pair produced by discovery."""

Assignment = Dict[str, str]
"""Board slot mapping ``{"identity": ..., "device": ...}``."""

BoardStatus = Dict[str, Any]
"""One entry of the supervisor's status list."""

BridgeStatus = Dict[str, Any]
"""Full supervisor response."""


def bootstrap() -> None:
    """Keep host dependencies separate from any installed ESP-IDF toolchain.

    Re-executes this script inside a dedicated virtualenv under ``.cache`` so
    the pyserial dependency never leaks into (or clashes with) the ESP-IDF
    environment.
    """
    env = STATE / "venv"
    python = env / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if Path(sys.prefix) == env:
        return
    requirements = Path(__file__).with_name("requirements.txt")
    stamp = STATE / "requirements.txt"
    if not python.exists():
        venv.create(env, with_pip=True)
    if not stamp.exists() or stamp.read_bytes() != requirements.read_bytes():
        subprocess.run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "-r",
                str(requirements),
            ],
            check=True,
        )
        stamp.write_bytes(requirements.read_bytes())
    raise SystemExit(subprocess.call([str(python), __file__, *sys.argv[1:]]))


def request(command: str) -> Optional[BridgeStatus]:
    """Send a control command to the running USB bridge supervisor.

    :param command: The command to send, e.g. ``"status"`` or ``"stop"``.
    :return: The decoded JSON response from the supervisor, or ``None`` when
        no bridge is listening on the control port.
    :raises RuntimeError: If the control port is owned by a different checkout.
    """
    try:
        with socket.create_connection(CONTROL, timeout=2) as connection:
            message = {"project": str(ROOT), "command": command}
            connection.sendall((json.dumps(message) + "\n").encode())
            with connection.makefile() as response:
                line = response.readline()
                if not line:
                    return None
                result: BridgeStatus = json.loads(line)
        if result["project"] != str(ROOT):
            raise RuntimeError(
                "Port 3999 belongs to another checkout; stop its USB bridge first."
            )
        return result
    except (ConnectionRefusedError, ConnectionResetError, BrokenPipeError):
        return None


def discover(ports: Optional[List[str]]) -> List[Detection]:
    """Enumerate the ESP32 serial adapters currently attached to the host.

    :param ports: Explicit host serial devices to use instead of USB discovery.
    :return: Sorted ``(identity, device)`` pairs. The identity is
        ``"port:<device>"`` for explicit ports, otherwise
        ``"vid:pid:serial:location"``.
    """
    from serial.tools.list_ports import comports

    available = {port.device: port for port in comports()}
    if ports:
        return [("port:" + device, device) for device in ports if device in available]
    return sorted(
        (
            f"{port.vid:04x}:{port.pid:04x}:{port.serial_number}:"
            f"{port.location or port.device}",
            port.device,
        )
        for port in available.values()
        if port.vid in VENDORS
    )


def reconcile(
    assignments: List[Assignment], detected: List[Detection]
) -> List[Assignment]:
    """Reserve disconnected slots so reconnecting never selects the other board.

    :param assignments: Persistent board slots, updated in place.
    :param detected: Currently detected ``(identity, device)`` pairs.
    :return: The updated assignments (the same list as *assignments*).
    """
    for identity, device in detected:
        match = next(
            (slot for slot in assignments if slot["identity"] == identity), None
        )
        if match:
            match["device"] = device
        elif len(assignments) < 2:
            assignments.append({"identity": identity, "device": device})
    return assignments


def serve(ports: Optional[List[str]]) -> None:
    """Run the USB bridge supervisor loop.

    Binds the control socket (which also prevents duplicate supervisors),
    reconciles detected boards into stable slots, and spawns one
    ``esp_rfc2217_server`` child per connected board.

    :param ports: Explicit host serial devices to bridge, or ``None`` to use
        USB discovery (falling back to the persisted mapping).
    """
    # Binding the control socket also prevents duplicate supervisors.
    with socket.socket() as listener:
        option = socket.SO_EXCLUSIVEADDRUSE if os.name == "nt" else socket.SO_REUSEADDR
        listener.setsockopt(socket.SOL_SOCKET, option, 1)
        listener.bind(CONTROL)
        listener.listen()
        listener.settimeout(1)
        mapping = STATE / "boards.json"
        saved: Dict[str, Any] = (
            json.loads(mapping.read_text()) if mapping.exists() else {}
        )
        ports = ports or saved.get("ports")
        assignments: List[Assignment] = saved.get("boards", [])
        if ports:
            assignments = [
                {"identity": "port:" + device, "device": device} for device in ports
            ]
        children: Dict[int, subprocess.Popen] = {}
        try:
            while True:
                detected = discover(ports)
                reconcile(assignments, detected)
                mapping.write_text(
                    json.dumps({"ports": ports, "boards": assignments}, indent=2) + "\n"
                )
                connected = dict(detected)
                status: List[BoardStatus] = []
                for index, slot in enumerate(assignments, start=1):
                    device = connected.get(slot["identity"])
                    child = children.get(index)
                    if child and (not device or child.args[-1] != device):
                        if child.poll() is None:
                            child.terminate()
                        child.wait(timeout=5)
                        children.pop(index)
                        child = None
                    if device and (child is None or child.poll() is not None):
                        children[index] = subprocess.Popen(
                            [
                                sys.executable,
                                "-m",
                                "esp_rfc2217_server",
                                "-p",
                                str(3999 + index),
                                device,
                            ],
                        )
                    status.append(
                        {
                            "board": index,
                            "device": slot["device"],
                            "connected": device is not None,
                            "port": 3999 + index,
                        }
                    )
                try:
                    connection, _ = listener.accept()
                except TimeoutError:
                    continue
                with connection:
                    connection.settimeout(2)
                    try:
                        with connection.makefile() as incoming:
                            message: Dict[str, Any] = json.loads(
                                incoming.readline(4096)
                            )
                        response: BridgeStatus = {
                            "project": str(ROOT),
                            "boards": status,
                        }
                        connection.sendall((json.dumps(response) + "\n").encode())
                    except (OSError, ValueError):
                        continue
                    if (
                        message.get("project") == str(ROOT)
                        and message.get("command") == "stop"
                    ):
                        break
        finally:
            for child in children.values():
                if child.poll() is None:
                    child.terminate()
                child.wait(timeout=5)


def show(status: Optional[BridgeStatus]) -> None:
    """Print the current bridge status in human-readable form.

    :param status: Supervisor response from :func:`request`, or ``None`` when
        the bridge is stopped.
    """
    if not status:
        print("ESP32 USB bridge is stopped.")
        return
    if not status["boards"]:
        print("ESP32 USB bridge is waiting for boards.")
    for board in status["boards"]:
        state = "connected" if board["connected"] else "disconnected"
        print(
            f"Board {board['board']}: {board['device']} ({state}) -> "
            f"rfc2217://host.docker.internal:{board['port']}?ign_set_control"
        )


def main() -> None:
    """Parse arguments and dispatch the requested bridge command."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=["start", "status", "stop", "reset", "serve"]
    )
    parser.add_argument(
        "--ports",
        nargs=2,
        metavar=("BOARD_1", "BOARD_2"),
        help="Use explicit host serial ports instead of USB discovery.",
    )
    args = parser.parse_args()
    bootstrap()
    if args.command == "serve":
        serve(args.ports)
        return
    status = request("stop" if args.command in {"stop", "reset"} else "status")
    if args.command in {"stop", "reset"}:
        if status:
            for _ in range(50):
                if request("status") is None:
                    break
                time.sleep(0.1)
            else:
                raise RuntimeError(
                    "USB bridge did not stop; check .cache/esp32-usb/bridge.log."
                )
        if args.command == "reset":
            (STATE / "boards.json").unlink(missing_ok=True)
        show(None)
        return
    if args.command == "start" and status is None:
        command = [sys.executable, __file__, "serve"]
        if args.ports:
            command.extend(["--ports", *args.ports])
        options: Dict[str, Any] = (
            {
                "creationflags": subprocess.DETACHED_PROCESS
                | subprocess.CREATE_NEW_PROCESS_GROUP
            }
            if os.name == "nt"
            else {"start_new_session": True}
        )
        with (STATE / "bridge.log").open("a") as log:
            child = subprocess.Popen(
                command, stdin=subprocess.DEVNULL, stdout=log, stderr=log, **options
            )
        for _ in range(50):
            status = request("status")
            if status:
                break
            if child.poll() is not None:
                raise RuntimeError(
                    "USB bridge failed; check .cache/esp32-usb/bridge.log."
                )
            time.sleep(0.1)
        if status is None:
            raise RuntimeError(
                "USB bridge did not start; check .cache/esp32-usb/bridge.log."
            )
    show(status)


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        sys.exit(str(error))
