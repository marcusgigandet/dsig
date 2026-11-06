import json
import socket
import subprocess
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import usb


def port(device, *, vid=0x10C4, serial="0001", location="1-1"):
    return types.SimpleNamespace(device=device, vid=vid, pid=0xEA60,
                                 serial_number=serial, location=location)


class DiscoveryTests(unittest.TestCase):
    def discover(self, ports, explicit=None):
        with patch("serial.tools.list_ports.comports", return_value=ports):
            return usb.discover(explicit)

    def test_duplicate_serial_numbers_still_identify_two_boards(self):
        detected = self.discover([port("COM3"), port("COM4", location="1-2")])
        self.assertEqual(len({identity for identity, _ in detected}), 2)

    def test_missing_usb_location_falls_back_to_device(self):
        detected = self.discover([port("COM3", location=None), port("COM4", location=None)])
        self.assertEqual(len({identity for identity, _ in detected}), 2)

    def test_ignore_non_usb_and_unrelated_devices(self):
        detected = self.discover([port("/dev/cu.debug-console", vid=None),
                                  port("/dev/ttyACM0", vid=0x1234), port("/dev/ttyUSB0")])
        self.assertEqual([device for _, device in detected], ["/dev/ttyUSB0"])

    def test_explicit_ports_keep_order_and_support_other_adapters(self):
        detected = self.discover([port("COM3", vid=0x1234), port("COM4")], ["COM4", "COM3"])
        self.assertEqual([device for _, device in detected], ["COM4", "COM3"])


class AssignmentTests(unittest.TestCase):
    def test_reconnect_with_new_device_name_preserves_board_number(self):
        slots = usb.reconcile([], [("a", "/dev/ttyUSB0"), ("b", "/dev/ttyUSB1")])
        usb.reconcile(slots, [("b", "/dev/ttyUSB0")])
        usb.reconcile(slots, [("b", "/dev/ttyUSB0"), ("a", "/dev/ttyUSB2")])
        self.assertEqual([slot["device"] for slot in slots], ["/dev/ttyUSB2", "/dev/ttyUSB0"])

    def test_new_adapter_does_not_take_disconnected_boards_slot(self):
        slots = usb.reconcile([], [("a", "COM3"), ("b", "COM4")])
        usb.reconcile(slots, [("b", "COM4"), ("c", "COM5")])
        self.assertEqual([slot["identity"] for slot in slots], ["a", "b"])


class SupervisorTests(unittest.TestCase):
    def test_status_handles_supervisor_closing_during_connection(self):
        with patch("socket.create_connection", side_effect=ConnectionResetError):
            self.assertIsNone(usb.request("status"))

    def test_restart_preserves_explicit_slots_and_rejects_another_checkouts_stop(self):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            control = listener.getsockname()
        server = (
            "import json, sys; from pathlib import Path; import usb; "
            "usb.STATE = Path(sys.argv[1]); "
            "usb.CONTROL = ('127.0.0.1', int(sys.argv[2])); "
            "usb.discover = lambda ports: []; usb.serve(json.loads(sys.argv[3]))"
        )
        with tempfile.TemporaryDirectory() as state, patch.object(usb, "CONTROL", control):
            for ports in [["COM4", "COM3"], None]:
                child = subprocess.Popen(
                    [sys.executable, "-c", server, state, str(control[1]), json.dumps(ports)],
                    cwd=Path(__file__).parent,
                )
                try:
                    status = None
                    for _ in range(100):
                        status = usb.request("status")
                        if status:
                            break
                        time.sleep(0.05)
                    self.assertIsNotNone(status)
                    self.assertEqual([board["device"] for board in status["boards"]],
                                     ["COM4", "COM3"])
                    self.assertTrue(all(not board["connected"] for board in status["boards"]))
                    with patch.object(usb, "ROOT", usb.ROOT / "other"):
                        with self.assertRaisesRegex(RuntimeError, "another checkout"):
                            usb.request("stop")
                    self.assertIsNotNone(usb.request("status"))
                    usb.request("stop")
                    self.assertEqual(child.wait(timeout=5), 0)
                finally:
                    if child.poll() is None:
                        child.terminate()
                        child.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
