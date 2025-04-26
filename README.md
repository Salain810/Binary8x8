# Binary Matrix 8x8 HDMI Switcher Integration for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

This integration allows you to control a Binary Matrix 8x8 HDMI switcher through Home Assistant.

## Features

- Control and monitor 8x8 HDMI matrix switching
- Telnet-based communication
- Auto-reconnect on connection loss
- User-friendly configuration through Home Assistant UI
- Service calls for automation integration
- Real-time state updates
- HACS compatible

## Installation

### HACS (Recommended)

1. Install HACS if you haven't already (see [HACS installation guide](https://hacs.xyz/docs/installation/manual))
2. Add this repository to HACS:
   - Go to HACS in your Home Assistant instance
   - Click on "Integrations"
   - Click the three dots in the top right
   - Click "Custom repositories"
   - Add the URL of this repository
   - Select "Integration" as the category
3. Click "Download"
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/binary_matrix` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Configuration -> Integrations
2. Click the "+" button and search for "Binary Matrix 8x8 HDMI Switcher"
3. Enter the following details:
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

## Contributing

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

***

[commits-shield]: https://img.shields.io/github/commit-activity/y/custom-components/binary_matrix.svg
[commits]: https://github.com/custom-components/binary_matrix/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg
[license-shield]: https://img.shields.io/github/license/custom-components/binary_matrix.svg
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40yourusername-blue.svg
[releases-shield]: https://img.shields.io/github/release/custom-components/binary_matrix.svg
[releases]: https://github.com/custom-components/binary_matrix/releases