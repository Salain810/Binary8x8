# Binary Matrix 8x8 HDMI Switcher Integration for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]
[![GitHub issues](https://img.shields.io/github/issues/Salain810/Binary8x8)](https://github.com/Salain810/Binary8x8/issues)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Semantic Versioning](https://img.shields.io/badge/Semantic%20Versioning-2.0.0-brightgreen)](https://semver.org/)

Control your Binary Matrix 8x8 HDMI switcher through Home Assistant with an intuitive interface.

## Features

- ✨ Control and monitor 8x8 HDMI matrix switching
- 🔄 Real-time state updates
- 🛡️ Secure telnet-based communication
- 🔌 Auto-reconnect on connection loss
- 🎯 User-friendly configuration through Home Assistant UI
- 🤖 Service calls for automation integration
- 📦 Automatic semantic versioning

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

1. Install [button-card](https://github.com/custom-cards/button-card) from HACS:
   ```yaml
   # In your configuration.yaml
   frontend:
     extra_module_url:
       - /hacsfiles/button-card/button-card.js
   ```

2. Add the custom card to your resources:
   - Go to Configuration -> Dashboards
   - Click the three dots menu in the top right
   - Select "Resources"
   - Click "Add Resource"
   - Add `/hacsfiles/button-card/button-card.js`
   - Select "JavaScript Module" as Resource Type

### Quick Dashboard Setup

1. Copy the contents of [example-dashboard.yaml](example-dashboard.yaml)
2. In Home Assistant:
   - Go to Overview
   - Click the three dots menu in top right
   - Select "Edit Dashboard"
   - Click the three dots menu again
   - Select "Raw configuration editor"
   - Paste the configuration
   - Click Save

### Customizing the Dashboard

The dashboard uses a template to create consistent buttons for each output. You can customize:

1. Button Appearance:
   ```yaml
   styles:
     card:
       - height: 100px  # Adjust button size
       - background-color: var(--card-background-color)  # Change background
   ```

2. Input Labels:
   ```yaml
   # Add custom names for your inputs
   name: '[[[ 
     const names = {
       "1": "Apple TV",
       "2": "PlayStation",
       "3": "Xbox",
       "4": "Nintendo",
       "5": "Chromecast",
       "6": "PC",
       "7": "Cable Box",
       "8": "Camera"
     };
     return `${names[entity.state] || `Input ${entity.state}`}`;
   ]]]'
   ```

3. Output Labels:
   ```yaml
   # Add custom names for your outputs
   name: '[[[ 
     const names = {
       "1": "Living Room TV",
       "2": "Bedroom TV",
       "3": "Office Monitor",
       "4": "Kitchen TV"
     };
     return names[entity.split("_")[1]] || `Output ${entity.split("_")[1]}`;
   ]]]'
   ```

## Usage

### Entities

The integration creates number entities for each output:
- `number.output_1` through `number.output_8`
- Values 1-8 represent the current input
- Can be controlled via service calls or UI

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
  output: 1  # Living Room TV
  input: 2   # PlayStation
```

### Automations Example

```yaml
automation:
  - alias: "Game Night Mode"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      # Route PlayStation to Living Room TV
      - service: binary_matrix.switch_input
        data:
          output: 1  # Living Room TV
          input: 2   # PlayStation
      # Route Cable Box to Kitchen TV
      - service: binary_matrix.switch_input
        data:
          output: 4  # Kitchen TV
          input: 7   # Cable Box
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