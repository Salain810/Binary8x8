"""Matrix controller for Binary Matrix 8x8 HDMI Switcher."""
import asyncio
import logging
import re
from typing import Dict, Optional, Tuple

import telnetlib3

from .const import (
    CMD_QUIT,
    CMD_STMAP,
    DEFAULT_PORT,
    ERROR_CANNOT_CONNECT,
    ERROR_INVALID_AUTH,
    ERROR_UNKNOWN,
    MATRIX_SIZE,
)

_LOGGER = logging.getLogger(__name__)

class MatrixError(Exception):
    """Matrix controller error."""

class MatrixConnectionError(MatrixError):
    """Matrix connection error."""

class MatrixAuthError(MatrixError):
    """Matrix authentication error."""

class MatrixController:
    """Controller class for Binary Matrix 8x8 HDMI Switcher."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = DEFAULT_PORT,
    ) -> None:
        """Initialize the matrix controller."""
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._connected = False
        self._state: Dict[int, int] = {}  # output -> input mapping

    @property
    def connected(self) -> bool:
        """Return True if connected to the matrix."""
        return self._connected

    @property
    def state(self) -> Dict[int, int]:
        """Return the current matrix state."""
        return self._state.copy()

    async def connect(self) -> None:
        """Connect to the matrix and authenticate."""
        try:
            self._reader, self._writer = await telnetlib3.open_connection(
                self._host, self._port
            )
        except Exception as err:
            raise MatrixConnectionError(ERROR_CANNOT_CONNECT) from err

        try:
            # Wait for login prompt
            data = await self._read_until("Login: ")
            _LOGGER.debug("Received login prompt: %s", data)

            # Send username
            await self._write(f"{self._username}\n")
            
            # Wait for password prompt
            data = await self._read_until("Password: ")
            _LOGGER.debug("Received password prompt: %s", data)

            # Send password
            await self._write(f"{self._password}\n")

            # Check for successful login
            data = await self._read_until(">")
            if "Logged in successfully" not in data:
                raise MatrixAuthError(ERROR_INVALID_AUTH)

            self._connected = True
            await self.update_state()

        except Exception as err:
            self._connected = False
            await self.disconnect()
            if isinstance(err, MatrixError):
                raise
            raise MatrixError(ERROR_UNKNOWN) from err

    async def disconnect(self) -> None:
        """Disconnect from the matrix."""
        if self._connected and self._writer is not None:
            try:
                await self._write(f"{CMD_QUIT}\n")
            except Exception:
                pass
            self._writer.close()
            await self._writer.wait_closed()
        self._connected = False
        self._reader = None
        self._writer = None

    async def update_state(self) -> Dict[int, int]:
        """Update the current matrix state."""
        response = await self._send_command(CMD_STMAP)
        self._state = self._parse_state_map(response)
        return self.state

    async def switch_input(self, output: int, input_: int) -> None:
        """Switch an output to an input."""
        if not (1 <= output <= MATRIX_SIZE and 1 <= input_ <= MATRIX_SIZE):
            raise ValueError("Output and input must be between 1 and 8")

        command = f"{output:02d}{input_:02d}"
        await self._send_command(command)
        await self.update_state()

    async def _send_command(self, command: str) -> str:
        """Send a command and return the response."""
        if not self._connected:
            raise MatrixConnectionError("Not connected")

        try:
            await self._write(f"{command}\n")
            response = await self._read_until(">")
            return response.strip()
        except Exception as err:
            self._connected = False
            raise MatrixConnectionError("Lost connection") from err

    async def _write(self, data: str) -> None:
        """Write data to the telnet connection."""
        if self._writer is None:
            raise MatrixConnectionError("Not connected")
        self._writer.write(data.encode())
        await self._writer.drain()

    async def _read_until(self, expected: str, timeout: float = 5.0) -> str:
        """Read data until the expected string is found."""
        if self._reader is None:
            raise MatrixConnectionError("Not connected")

        try:
            data = ""
            while True:
                byte_data = await asyncio.wait_for(
                    self._reader.read(1024),
                    timeout=timeout
                )
                if not byte_data:
                    raise MatrixConnectionError("Connection closed")
                
                data += byte_data.decode()
                if expected in data:
                    return data
        except asyncio.TimeoutError as err:
            raise MatrixConnectionError("Timeout waiting for response") from err

    def _parse_state_map(self, response: str) -> Dict[int, int]:
        """Parse the STMAP response into a state dictionary."""
        state = {}
        pattern = r"o(\d{2})i(\d{2})"
        
        for line in response.splitlines():
            match = re.search(pattern, line)
            if match:
                output = int(match.group(1))
                input_ = int(match.group(2))
                state[output] = input_

        return state

    async def __aenter__(self) -> "MatrixController":
        """Enter the async context manager."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context manager."""
        await self.disconnect()