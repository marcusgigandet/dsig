import unittest
from unittest.mock import patch

import serial
from dsig_serial.protocol_rfc2217 import Serial
from serial.rfc2217 import Serial as RFC2217Serial

original_reconfigure = RFC2217Serial._reconfigure_port


class RFC2217Tests(unittest.TestCase):
    def setUp(self):
        self.client = Serial()
        self.negotiate = self.enterContext(patch.object(RFC2217Serial, "_reconfigure_port"))
        self.enterContext(patch.object(RFC2217Serial, "open",
                                      side_effect=self.client._reconfigure_port))
        self.client.open()
        self.client.is_open = True
        self.addCleanup(self.client.close)

    def test_local_timeout_changes_do_not_negotiate(self):
        for timeout in [0.1, 3, None, 0]:
            self.client.timeout = timeout
            self.client.inter_byte_timeout = timeout
        self.negotiate.assert_called_once()

    def test_remote_setting_changes_still_negotiate(self):
        changes = [("baudrate", 460800), ("bytesize", 7), ("parity", "E"), ("stopbits", 2),
                   ("xonxoff", True), ("xonxoff", False), ("rtscts", True), ("dsrdtr", True)]
        for name, value in changes:
            with self.subTest(setting=name, value=value):
                self.negotiate.reset_mock()
                setattr(self.client, name, value)
                self.negotiate.assert_called_once()

    def test_failed_negotiation_is_retried(self):
        self.negotiate.side_effect = serial.SerialException("rejected settings")
        with self.assertRaises(serial.SerialException):
            self.client.baudrate = 460800
        self.negotiate.reset_mock(side_effect=True)
        self.client.timeout = 3
        self.negotiate.assert_called_once()

    def test_reconnect_negotiates_even_with_unchanged_settings(self):
        self.client.close()
        self.client.open()
        self.assertEqual(self.negotiate.call_count, 2)

    def test_unsupported_write_timeout_still_raises(self):
        self.client._socket = object()
        try:
            with patch.object(RFC2217Serial, "_reconfigure_port",
                              side_effect=lambda: original_reconfigure(self.client)):
                with self.assertRaises(NotImplementedError):
                    self.client.write_timeout = 1
        finally:
            self.client._socket = None

    def test_url_handler_registration_preserves_other_ports(self):
        remote = serial.serial_for_url("rfc2217://localhost:4000", do_not_open=True)
        self.assertIsInstance(remote, Serial)
        native = serial.serial_for_url("/dev/ttyUSB0", do_not_open=True)
        self.assertIsInstance(native, serial.Serial)
        with serial.serial_for_url("loop://") as loop:
            loop.write(b"test")
            self.assertEqual(loop.read(4), b"test")


if __name__ == "__main__":
    unittest.main()
