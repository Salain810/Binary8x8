"""Matrix controller for Binary Matrix 8x8 HDMI Switcher."""
import asyncio
import logging
import telnetlib3
from typing import Dict, Optional

from .const import DOMAIN

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
        port: int = 23,
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
            _LOGGER.debug("Connecting to %s:%d", self._host, self._port)
            
            # Open connection
            self._reader, self._writer = await telnetlib3.open_connection(
                self._host, self._port
            )

            # Wait for login prompt
            data = await self._read_until(b"Login:", timeout=3)
            _LOGGER.debug("Got login prompt: %s", data)

            # Send username
            await self._write(f"{self._username}\n")

            # Wait for password prompt
            data = await self._read_until(b"Password:", timeout=3)
            _LOGGER.debug("Got password prompt: %s", data)

            # Send password
            await self._write(f"{self._password}\n")

            # Wait for successful login
            data = await self._read_until(b">", timeout=10)
            _LOGGER.debug("Login response: %s", data)

            if b"Logged in successfully" not in data:
                raise MatrixAuthError("Invalid credentials")

            self._connected = True
            _LOGGER.info("Successfully connected to matrix")

            # Get initial state
            await self.update_state()

        except asyncio.TimeoutError as err:
            _LOGGER.error("Connection timed out")
            raise MatrixConnectionError("Connection timed out") from err
        except Exception as err:
            _LOGGER.error("Connection failed: %s", str(err))
            if isinstance(err, MatrixError):
                raise
            raise MatrixConnectionError(f"Failed to connect: {err}") from err

    async def disconnect(self) -> None:
        """Disconnect from the matrix."""
        if self._connected and self._writer is not None:
            try:
                await self._write("q\n")
            except Exception:
                pass
            self._writer.close()
            await self._writer.wait_closed()
        self._connected = False
        self._reader = None
        self._writer = None

    async def update_state(self) -> Dict[int, int]:
        """Update the current matrix state."""
        response = await self._send_command("STMAP")
        self._state = self._parse_state_map(response)
        return self.state

    async def switch_input(self, output: int, input_: int) -> None:
        """Switch an output to an input."""
        if not (1 <= output <= 8 and 1 <= input_ <= 8):
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
            response = await self._read_until(b">", timeout=5)
            return response.decode().strip()
        except Exception as err:
            self._connected = False
            raise MatrixConnectionError(f"Command failed: {err}") from err

    async def _write(self, data: str) -> None:
        """Write data to the telnet connection."""
        if self._writer is None:
            raise MatrixConnectionError("Not connected")
        try:
            self._writer.write(data.encode())
            await self._writer.drain()
        except Exception as err:
            raise MatrixConnectionError(f"Write failed: {err}") from err

    async def _read_until(self, expected: bytes, timeout: float) -> bytes:
        """Read data until the expected bytes are found."""
        if self._reader is None:
            raise MatrixConnectionError("Not connected")

        try:
            data = b""
            while True:
                chunk = await asyncio.wait_for(
                    self._reader.read(1024),
                    timeout=timeout
                )
                if not chunk:
                    raise MatrixConnectionError("Connection closed")
                
                data += chunk
                if expected in data:
                    return data
        except asyncio.TimeoutError as err:
            raise MatrixConnectionError("Read timeout") from err

    def _parse_state_map(self, response: str) -> Dict[int, int]:
        """Parse the STMAP response into a state dictionary."""
        state = {}
        for line in response.splitlines():
            if line.startswith("o") and len(line) >= 6:
                try:
                    output = int(line[1:3])
                    input_ = int(line[4:6])
                    state[output] = input_
                except ValueError:
                    continue
        return state

    async def __aenter__(self) -> "MatrixController":
        """Enter the async context manager."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context manager."""
        await self.disconnect()