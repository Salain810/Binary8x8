# Binary Matrix 8x8 HDMI Switcher Integration for Home Assistant

This integration allows you to control a Binary Matrix 8x8 HDMI switcher through Home Assistant.

## Features

- Control and monitor 8x8 HDMI matrix switching
- Telnet-based communication
- Auto-reconnect on connection loss
- User-friendly configuration through Home Assistant UI
- Service calls for automation integration
- Real-time state updates

## Installation

1. Copy the `binary_matrix` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Go to Configuration -> Integrations
4. Click the "+" button and search for "Binary Matrix 8x8 HDMI Switcher"
5. Enter your device's connection details

## Configuration

The following parameters are required for setup:

- **Name**: A name for your matrix switcher
- **Host**: IP address of your matrix switcher (e.g., 192.168.4.200)
- **Port**: Telnet port (default: 23)
- **Username**: Login username (default: admin)
- **Password**: Login password

## Usage

### Entities

The integration creates number entities for each output, allowing you to:

- View current input selection for each output
- Change input selection through the Home Assistant UI
- Monitor connection status

### Services

#### binary_matrix.switch_input

Switch a specific output to a specific input.

Parameters:
- `output`: Output number (1-8)
- `input`: Input number (1-8)

Example service call:
```yaml
service: binary_matrix.switch_input
data:
  output: 1
  input: 2
```

## Troubleshooting

### Common Issues

1. **Cannot Connect**
   - Verify the IP address is correct
   - Ensure the matrix switcher is powered on and connected to the network
   - Check if telnet port (23) is accessible

2. **Authentication Failed**
   - Verify username and password
   - Try power cycling the matrix switcher

3. **Connection Lost**
   - The integration will automatically attempt to reconnect
   - Check network connectivity
   - Verify the matrix switcher is still powered on and responsive

## Support

For issues and feature requests, please use the GitHub issue tracker.

## License

This integration is licensed under the MIT License. See the LICENSE file for details.