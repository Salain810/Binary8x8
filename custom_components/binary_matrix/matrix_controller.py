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
            _LOGGER.debug("Attempting direct socket connection to %s:%d", self._host, self._port)
            reader, writer = await asyncio.open_connection(self._host, self._port)
            self._reader = reader
            self._writer = writer

            # Wait a moment for any initial data
            await asyncio.sleep(1)
            
            # Try to read any initial data
            initial_data = await self._read_available()
            _LOGGER.debug("Initial data received: %r", initial_data)

            # Send a newline to trigger login prompt if needed
            _LOGGER.debug("Sending initial newline")
            await self._write("\n")
            await asyncio.sleep(1)

            # Read response
            login_data = await self._read_available()
            _LOGGER.debug("Response after newline: %r", login_data)

            if b"Login:" not in login_data and b"login:" not in login_data.lower():
                # Try sending username directly
                _LOGGER.debug("No login prompt, trying direct username")
                await self._write(f"{self._username}\n")
                await asyncio.sleep(1)
                
                response = await self._read_available()
                _LOGGER.debug("Response after username: %r", response)
                
                if b"Password:" in response or b"password:" in response.lower():
                    _LOGGER.debug("Got password prompt")
                else:
                    raise MatrixConnectionError("No password prompt after username")
            else:
                # Normal login sequence
                _LOGGER.debug("Sending username: %s", self._username)
                await self._write(f"{self._username}\n")
                await asyncio.sleep(1)

                password_prompt = await self._read_available()
                _LOGGER.debug("Response after username: %r", password_prompt)

                if b"Password:" not in password_prompt and b"password:" not in password_prompt.lower():
                    raise MatrixConnectionError("No password prompt")

            # Send password
            _LOGGER.debug("Sending password")
            await self._write(f"{self._password}\n")
            await asyncio.sleep(1)

            # Check login response
            login_response = await self._read_available()
            _LOGGER.debug("Login response: %r", login_response)

            if b">" in login_response:
                self._connected = True
                _LOGGER.info("Successfully connected to matrix")
                return
            else:
                raise MatrixAuthError("Login failed")

        except Exception as err:
            _LOGGER.error("Connection failed: %s", err)
            if self._writer:
                self._writer.close()
                await self._writer.wait_closed()
            self._reader = None
            self._writer = None
            self._connected = False
            raise

    async def _read_available(self, timeout: float = 2.0) -> bytes:
        """Read all available data with timeout."""
        if not self._reader:
            raise MatrixConnectionError("Not connected")

        try:
            data = b""
            while True:
                try:
                    chunk = await asyncio.wait_for(
                        self._reader.read(1024),
                        timeout=timeout
                    )
                    if not chunk:
                        break
                    data += chunk
                    if not self._reader.at_eof() and self._reader._buffer.empty():
                        # No more data immediately available
                        break
                except asyncio.TimeoutError:
                    break
            return data
        except Exception as err:
            _LOGGER.error("Read error: %s", err)
            raise MatrixConnectionError(f"Read failed: {err}") from err

    async def _write(self, data: str) -> None:
        """Write data to the connection."""
        if not self._writer:
            raise MatrixConnectionError("Not connected")
        
        try:
            self._writer.write(data.encode())
            await self._writer.drain()
        except Exception as err:
            _LOGGER.error("Write error: %s", err)
            raise MatrixConnectionError(f"Write failed: {err}") from err

    async def disconnect(self) -> None:
        """Disconnect from the matrix."""
        if self._connected and self._writer:
            try:
                await self._write("q\n")
            except Exception:
                pass
            self._writer.close()
            await self._writer.wait_closed()
        self._connected = False
        self._reader = None
        self._writer = None

    @property
    def connected(self) -> bool:
        """Return True if connected to the matrix."""
        return self._connected

    @property
    def state(self) -> Dict[int, int]:
        """Return the current matrix state."""
        return self._state.copy()

    # Rest of the methods remain the same...