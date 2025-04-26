# Binary Matrix 8x8 HDMI Switcher Integration for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]
[![GitHub issues](https://img.shields.io/github/issues/Salain810/Binary8x8)](https://github.com/Salain810/Binary8x8/issues)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Control your Binary Matrix 8x8 HDMI switcher through Home Assistant with an intuitive interface.

## Features

- ✨ Control and monitor 8x8 HDMI matrix switching
- 🔄 Real-time state updates
- 🛡️ Secure telnet-based communication
- 🔌 Auto-reconnect on connection loss
- 🎯 User-friendly configuration through Home Assistant UI
- 🤖 Service calls for automation integration

## Installation

### Quick Installation (Recommended)

Click this button to open HACS and add the repository:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.][add-repo-shield]][add-repo]

### Manual HACS Installation

1. Ensure [HACS](https://hacs.xyz) is installed in your Home Assistant instance
2. Add this repository as a custom repository in HACS:
   - Open HACS in Home Assistant
   - Click on the three dots in the top right corner
   - Select "Custom repositories"
   - Add `https://github.com/Salain810/Binary8x8` as URL
   - Select "Integration" as category
3. Click Install
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/binary_matrix` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Configuration -> Integrations
2. Click the "+" button and search for "Binary Matrix 8x8 HDMI Switcher"
3. Enter your device's details:
   - **Name**: A name for your matrix switcher
   - **Host**: IP address of your matrix switcher (e.g., 192.168.4.200)
   - **Port**: Telnet port (default: 23)
   - **Username**: Login username (default: admin)
   - **Password**: Login password

## Dashboard Configuration

### Prerequisites

1. Install [Button Card](https://github.com/custom-cards/button-card) from HACS:
   - Open HACS -> Frontend
   - Search for "Button Card"
   - Install and restart Home Assistant

### Installation

1. Copy the contents of [example-dashboard.yaml](example-dashboard.yaml) 
2. In Home Assistant:
   - Go to Overview
   - Click the three dots menu in top right
   - Select "Edit Dashboard"
   - Click the three dots menu again
   - Select "Raw configuration editor"
   - Paste the configuration
   - Click Save

The dashboard provides:
- 8x8 grid layout matching your matrix
- Click to cycle through inputs for each output
- Current input status display
- Responsive design that works on mobile and desktop

### Customizing the Dashboard

You can modify the example-dashboard.yaml to:
- Change button colors and styles
- Add labels for your devices
- Modify the layout
- Add additional controls

## Usage

### Entities

The integration creates number entities for each output, allowing you to:
- View current input selection for each output
- Change input selection through sliders
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

### Automations Example

```yaml
automation:
  - alias: "Switch HDMI Input on TV Power On"
    trigger:
      - platform: state
        entity_id: switch.tv_power
        to: "on"
    action:
      - service: binary_matrix.switch_input
        data:
          output: 1  # TV
          input: 2   # Gaming Console
```

## Support

Got issues or questions? Here's how to get help:

- 🐛 Found a bug? [Open an issue](https://github.com/Salain810/Binary8x8/issues)
- 💡 Have an idea? [Submit a feature request](https://github.com/Salain810/Binary8x8/issues)
- 🤔 Need help? [Check existing issues](https://github.com/Salain810/Binary8x8/issues?q=is%3Aissue)

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the Home Assistant community
- Special thanks to all contributors

---

[releases-shield]: https://img.shields.io/github/release/Salain810/Binary8x8.svg
[releases]: https://github.com/Salain810/Binary8x8/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/Salain810/Binary8x8.svg
[commits]: https://github.com/Salain810/Binary8x8/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg
[license-shield]: https://img.shields.io/github/license/Salain810/Binary8x8.svg
[add-repo-shield]: https://my.home-assistant.io/badges/hacs_repository.svg
[add-repo]: https://my.home-assistant.io/redirect/hacs_repository/?owner=Salain810&repository=Binary8x8&category=integration