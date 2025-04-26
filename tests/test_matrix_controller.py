"""Test the matrix controller."""
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from custom_components.binary_matrix.matrix_controller import (
    MatrixController,
    MatrixConnectionError,
    MatrixAuthError,
)

@pytest.fixture
def matrix():
    """Create a matrix controller instance."""
    return MatrixController(
        host="192.168.4.200",
        username="admin",
        password="123",
    )

@pytest.fixture
def mock_telnet():
    """Mock telnetlib3 connection."""
    with patch("telnetlib3.open_connection") as mock_open:
        reader = AsyncMock()
        writer = AsyncMock()
        mock_open.return_value = (reader, writer)
        yield mock_open, reader, writer

async def test_connect_success(matrix, mock_telnet):
    """Test successful connection."""
    mock_open, reader, writer = mock_telnet
    
    # Mock login sequence responses
    reader.read.side_effect = [
        b"Login: ",
        b"Password: ",
        b"Logged in successfully\n>",
        b"STMAP\no01i02\no02i01\no03i03\no04i04\no05i05\no06i06\no07i07\no08i08\n>",
    ]
    
    await matrix.connect()
    
    assert matrix.connected is True
    writer.write.assert_any_call(b"admin\n")
    writer.write.assert_any_call(b"123\n")

async def test_connect_auth_failure(matrix, mock_telnet):
    """Test authentication failure."""
    mock_open, reader, writer = mock_telnet
    
    reader.read.side_effect = [
        b"Login: ",
        b"Password: ",
        b"Authentication failed\n>",
    ]
    
    with pytest.raises(MatrixAuthError):
        await matrix.connect()
    
    assert matrix.connected is False

async def test_connect_network_error(matrix):
    """Test network connection error."""
    with patch("telnetlib3.open_connection", side_effect=ConnectionError):
        with pytest.raises(MatrixConnectionError):
            await matrix.connect()
    
    assert matrix.connected is False

async def test_switch_input(matrix, mock_telnet):
    """Test switching input."""
    mock_open, reader, writer = mock_telnet
    
    # Mock connection and command responses
    reader.read.side_effect = [
        b"Login: ",
        b"Password: ",
        b"Logged in successfully\n>",
        b"STMAP\no01i02\no02i01\no03i03\no04i04\no05i05\no06i06\no07i07\no08i08\n>",
        b"0102\n>",  # Switch command response
        b"STMAP\no01i02\no02i01\no03i03\no04i04\no05i05\no06i06\no07i07\no08i08\n>",
    ]
    
    await matrix.connect()
    await matrix.switch_input(1, 2)
    
    writer.write.assert_any_call(b"0102\n")
    assert matrix.state[1] == 2

async def test_parse_state_map(matrix):
    """Test parsing state map response."""
    response = "STMAP\no01i02\no02i05\no03i01\no04i02\no05i01\no06i05\no07i07\no08i03\n>"
    state = matrix._parse_state_map(response)
    
    assert state == {
        1: 2,
        2: 5,
        3: 1,
        4: 2,
        5: 1,
        6: 5,
        7: 7,
        8: 3,
    }

async def test_disconnect(matrix, mock_telnet):
    """Test disconnection."""
    mock_open, reader, writer = mock_telnet
    
    reader.read.side_effect = [
        b"Login: ",
        b"Password: ",
        b"Logged in successfully\n>",
        b"STMAP\no01i02\no02i01\no03i03\no04i04\no05i05\no06i06\no07i07\no08i08\n>",
    ]
    
    await matrix.connect()
    await matrix.disconnect()
    
    assert matrix.connected is False
    writer.close.assert_called_once()
    writer.wait_closed.assert_called_once()