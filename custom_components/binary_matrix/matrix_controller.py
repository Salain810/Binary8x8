"""Matrix controller for Binary Matrix 8x8 HDMI Switcher."""
import asyncio
import logging
import telnetlib3
from typing import Dict, Optional

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)  # Enable debug logging

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
            _LOGGER.info("Starting connection to %s:%d", self._host, self._port)
            
            # Try to reach the host first
            try:
                _LOGGER.debug("Testing connection to host")
                transport, _ = await asyncio.wait_for(
                    asyncio.get_event_loop().create_connection(
                        lambda: asyncio.Protocol(), self._host, self._port
                    ),
                    timeout=5
                )
                transport.close()
                _LOGGER.debug("Host is reachable")
            except Exception as err:
                _LOGGER.error("Host connection test failed: %s", err)
                raise MatrixConnectionError(f"Host unreachable: {err}") from err

            # Open telnet connection
            _LOGGER.debug("Opening telnet connection")
            try:
                self._reader, self._writer = await asyncio.wait_for(
                    telnetlib3.open_connection(self._host, self._port),
                    timeout=5
                )
            except Exception as err:
                _LOGGER.error("Telnet connection failed: %s", err)
                raise MatrixConnectionError(f"Telnet connection failed: {err}") from err

            # Wait for login prompt
            _LOGGER.debug("Waiting for login prompt")
            try:
                data = await self._read_until(b"Login:", timeout=3)
                _LOGGER.debug("Received login prompt: %r", data)
            except Exception as err:
                _LOGGER.error("No login prompt received: %s", err)
                raise MatrixConnectionError("No login prompt") from err

            # Send username
            _LOGGER.debug("Sending username: %s", self._username)
            await self._write(f"{self._username}\n")
            await asyncio.sleep(0.5)

            # Wait for password prompt
            _LOGGER.debug("Waiting for password prompt")
            try:
                data = await self._read_until(b"Password:", timeout=3)
                _LOGGER.debug("Received password prompt: %r", data)
            except Exception as err:
                _LOGGER.error("No password prompt received: %s", err)
                raise MatrixConnectionError("No password prompt") from err

            # Send password
            _LOGGER.debug("Sending password")
            await self._write(f"{self._password}\n")
            await asyncio.sleep(0.5)

            # Wait for successful login
            _LOGGER.debug("Waiting for login response")
            try:
                data = await self._read_until(b">", timeout=10)
                _LOGGER.debug("Received login response: %r", data)
            except Exception as err:
                _LOGGER.error("No login response received: %s", err)
                raise MatrixConnectionError("No login confirmation") from err

            if b"Logged in successfully" not in data:
                _LOGGER.error("Login failed. Response: %r", data)
                raise MatrixAuthError("Invalid credentials")

            self._connected = True
            _LOGGER.info("Successfully connected to matrix")

            # Get initial state
            await self.update_state()

        except Exception as err:
            _LOGGER.exception("Connection failed with error: %s", err)
            if isinstance(err, MatrixError):
                raise
            raise MatrixConnectionError(f"Connection failed: {err}") from err

    async def disconnect(self) -> None:
        """Disconnect from the matrix."""
        if self._connected and self._writer is not None:
            try:
                await self._write("q\n")
            except Exception as err:
                _LOGGER.debug("Error sending quit command: %s", err)
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception as err:
                _LOGGER.debug("Error closing connection: %s", err)
        self._connected = False
        self._reader = None
        self._writer = None
        _LOGGER.debug("Disconnected from matrix")

    async def _write(self, data: str) -> None:
        """Write data to the telnet connection."""
        if self._writer is None:
            raise MatrixConnectionError("Not connected")
        try:
            _LOGGER.debug("Writing data: %r", data)
            self._writer.write(data.encode())
            await self._writer.drain()
        except Exception as err:
            _LOGGER.error("Write error: %s", err)
            raise MatrixConnectionError(f"Write failed: {err}") from err

    async def _read_until(self, expected: bytes, timeout: float) -> bytes:
        """Read data until the expected bytes are found."""
        if self._reader is None:
            raise MatrixConnectionError("Not connected")

        try:
            _LOGGER.debug("Reading until %r with timeout %s", expected, timeout)
            start_time = asyncio.get_event_loop().time()
            data = b""

            while True:
                if (asyncio.get_event_loop().time() - start_time) > timeout:
                    _LOGGER.error("Read timeout after %s seconds", timeout)
                    raise asyncio.TimeoutError(f"Timeout waiting for {expected!r}")

                chunk = await asyncio.wait_for(self._reader.read(1024), timeout=1.0)
                if not chunk:
                    _LOGGER.error("Connection closed while reading")
                    raise MatrixConnectionError("Connection closed while reading")
                
                _LOGGER.debug("Received chunk: %r", chunk)
                data += chunk
                if expected in data:
                    return data

        except asyncio.TimeoutError as err:
            _LOGGER.error("Read timeout: %s", err)
            raise MatrixConnectionError("Read timeout") from err
        except Exception as err:
            _LOGGER.error("Read error: %s", err)
            raise MatrixConnectionError(f"Read failed: {err}") from err

    # Rest of the class implementation remains the same...