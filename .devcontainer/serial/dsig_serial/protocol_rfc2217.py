"""Avoid renegotiating remote settings for local timeout changes.

Without this fix, the commands may take significantly longer to execute.
"""

from serial.rfc2217 import Serial as RFC2217Serial


class Serial(RFC2217Serial):
    def open(self) -> None:
        """Reset settings to ensure each connection renogotiates its settings."""
        self._remote_settings = None
        return super().open()

    def _reconfigure_port(self) -> None:    
        """Updates the serial connection setttings."""    
        
        # Get current settings snapshot
        settings = self.get_settings()
        settings.pop("timeout")
        settings.pop("inter_byte_timeout")
        
        if settings != self._remote_settings:
            # A failed negotiation can leave the server partially configured.
            self._remote_settings = None
            super()._reconfigure_port()
            self._remote_settings = settings
