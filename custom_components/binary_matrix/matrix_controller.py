"""Matrix controller for Binary Matrix 8x8 HDMI Switcher."""
import asyncio
import logging
from typing import Dict, Optional, Tuple

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
            self._reader, self._writer = await asyncio.open_connection(
                self._host, self._port
            )
        except (OSError, ConnectionError) as err:
            _LOGGER.error("Failed to connect to %s:%d - %s", self._host, self._port, err)
            raise MatrixConnectionError("Cannot connect to the device") from err

        try:
            # Wait for login prompt with timeout
            try:
                data = await asyncio.wait_for(self._read_until("Login: "), timeout=5.0)
                _LOGGER.debug("Received login prompt: %s", data)
            except asyncio.TimeoutError as err:
                raise MatrixConnectionError("Timeout waiting for login prompt") from err

            # Send username
            await self._write(f"{self._username}\n")
            
            # Wait for password prompt with timeout
            try:
                data = await asyncio.wait_for(self._read_until("Password: "), timeout=5.0)
                _LOGGER.debug("Received password prompt: %s", data)
            except asyncio.TimeoutError as err:
                raise MatrixConnectionError("Timeout waiting for password prompt") from err

            # Send password
            await self._write(f"{self._password}\n")

            # Check for successful login
            try:
                data = await asyncio.wait_for(self._read_until(">"), timeout=5.0)
                if "Logged in successfully" not in data:
                    raise MatrixAuthError("Invalid username or password")
                _LOGGER.debug("Login successful")
            except asyncio.TimeoutError as err:
                raise MatrixConnectionError("Timeout waiting for login response") from err

            self._connected = True
            await self.update_state()

        except Exception as err:
            self._connected = False
            await self.disconnect()
            if isinstance(err, (MatrixConnectionError, MatrixAuthError)):
                raise
            _LOGGER.error("Unexpected error during connection: %s", err)
            raise MatrixError("Unknown error occurred during connection") from err

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
            raise MatrixConnectionError("Not connected to the device")

        try:
            await self._write(f"{command}\n")
            response = await self._read_until(">")
            return response.strip()
        except Exception as err:
            self._connected = False
            _LOGGER.error("Error sending command %s: %s", command, err)
            raise MatrixConnectionError("Lost connection to the device") from err

    async def _write(self, data: str) -> None:
        """Write data to the telnet connection."""
        if self._writer is None:
            raise MatrixConnectionError("Not connected")
        try:
            self._writer.write(data.encode())
            await self._writer.drain()
        except Exception as err:
            _LOGGER.error("Error writing to device: %s", err)
            raise MatrixConnectionError("Failed to send data to device") from err

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
                    raise MatrixConnectionError("Connection closed by device")
                
                data += byte_data.decode()
                if expected in data:
                    return data
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout waiting for response")
            raise MatrixConnectionError("Timeout waiting for device response") from err
        except Exception as err:
            _LOGGER.error("Error reading from device: %s", err)
            raise MatrixConnectionError("Failed to read from device") from err

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
                    _LOGGER.warning("Invalid state map line: %s", line)
                    continue
        return state

    async def __aenter__(self) -> "MatrixController":
        """Enter the async context manager."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context manager."""
        await self.disconnect()