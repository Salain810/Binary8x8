"""Matrix controller for Binary Matrix 8x8 HDMI Switcher."""
import asyncio
import logging
from typing import Dict, Optional

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

    async def connect(self) -> None:
        """Connect to the matrix and authenticate."""
        try:
            _LOGGER.debug("Connecting to %s:%d", self._host, self._port)

            # Open connection
            reader, writer = await asyncio.open_connection(self._host, self._port)
            self._reader = reader
            self._writer = writer

            # Initial connection check
            initial_data = await self._read_available()
            _LOGGER.debug("Initial data received: %s", initial_data)

            if "Login:" not in initial_data:
                # Send newline and check for login prompt
                await self._write("\r\n")
                await asyncio.sleep(0.5)
                initial_data = await self._read_available()
                _LOGGER.debug("Data after newline: %s", initial_data)

            if "Login:" not in initial_data:
                raise MatrixConnectionError("No login prompt received")

            # Send username
            _LOGGER.debug("Sending username: %s", self._username)
            await self._write(f"{self._username}\r\n")
            await asyncio.sleep(0.5)

            # Check for password prompt
            response = await self._read_available()
            _LOGGER.debug("Response after username: %s", response)

            if "Password:" not in response:
                raise MatrixConnectionError("No password prompt received")

            # Send password
            _LOGGER.debug("Sending password")
            await self._write(f"{self._password}\r\n")
            await asyncio.sleep(0.5)

            # Verify login success
            response = await self._read_available()
            _LOGGER.debug("Login response: %s", response)

            if ">" not in response:
                raise MatrixAuthError("Login failed")

            self._connected = True
            _LOGGER.info("Successfully connected to matrix")

            # Get initial state
            await self.update_state()

        except Exception as err:
            _LOGGER.error("Connection failed: %s", err)
            if self._writer:
                self._writer.close()
                await self._writer.wait_closed()
            self._reader = None
            self._writer = None
            self._connected = False
            raise

    async def disconnect(self) -> None:
        """Disconnect from the matrix."""
        if self._connected and self._writer:
            try:
                await self._write("q\r\n")
            except Exception:
                pass
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception:
                pass
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
            await self._write(f"{command}\r\n")
            response = await self._read_available()
            return response

        except Exception as err:
            _LOGGER.error("Command failed: %s", err)
            raise MatrixConnectionError(f"Command failed: {err}")

    async def _write(self, data: str) -> None:
        """Write data to the connection."""
        if not self._writer:
            raise MatrixConnectionError("Not connected")
        try:
            self._writer.write(data.encode('utf-8'))
            await self._writer.drain()
        except Exception as err:
            _LOGGER.error("Write error: %s", err)
            raise MatrixConnectionError(f"Write failed: {err}")

    async def _read_available(self, timeout: float = 2.0) -> str:
        """Read all available data with timeout."""
        if not self._reader:
            raise MatrixConnectionError("Not connected")

        try:
            chunks = []
            try:
                while True:
                    chunk = await asyncio.wait_for(
                        self._reader.read(1024),
                        timeout=timeout
                    )
                    if not chunk:
                        break
                    chunks.append(chunk.decode('utf-8', errors='replace'))
                    if not self._reader.at_eof() and len(self._reader._buffer) == 0:
                        break
            except asyncio.TimeoutError:
                pass

            return "".join(chunks)

        except Exception as err:
            _LOGGER.error("Read error: %s", err)
            raise MatrixConnectionError(f"Read failed: {err}")

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

    @property
    def connected(self) -> bool:
        """Return True if connected to the matrix."""
        return self._connected

    @property
    def state(self) -> Dict[int, int]:
        """Return the current matrix state."""
        return self._state.copy()