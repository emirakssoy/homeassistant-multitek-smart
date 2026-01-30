# Multitek Smart Home Integration for Home Assistant

A custom Home Assistant integration for controlling Multitek smart home devices through the Multitek Smart Tablet.

> **Note:** This is a demonstration version showcasing the integration architecture. It was developed during my internship at [Multitek](https://www.multitek.com.tr/) to learn Home Assistant integration development patterns and IoT device communication.

## Features

- **Device Control**: Control various smart home devices including:
  - Lights
  - Shutters/Blinds
  - On/Off switches
  - Gas valves
  - Electric switches
  - Water valves

- **Real-time Status**: Automatic polling for device state updates
- **Config Flow**: Easy setup through Home Assistant UI
- **Authentication Support**: Optional API key authentication
- **Device Registry**: Full integration with Home Assistant's device registry

## Architecture

This integration follows Home Assistant's modern integration patterns:

- **Coordinator Pattern**: Uses `DataUpdateCoordinator` for efficient API polling
- **Config Flow**: UI-based configuration with validation
- **Entity Platforms**: Separate switch and sensor platforms
- **Async/Await**: Fully asynchronous for optimal performance

## Installation

### Manual Installation

1. Copy the `custom_components/multitek_smart` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Go to **Settings** → **Devices & Services** → **Add Integration**
4. Search for "Multitek Smart Home"
5. Enter your tablet's IP address and port

### Directory Structure

```
custom_components/
└── multitek_smart/
    ├── __init__.py          # Integration setup
    ├── const.py             # Constants and configuration
    ├── coordinator.py       # Data update coordinator
    ├── config_flow.py       # Configuration flow
    ├── switch.py            # Switch entities
    ├── sensor.py            # Sensor entities
    ├── manifest.json        # Integration manifest
    └── translations/
        └── en.json          # English translations
```

## Entities

### Switches
Each controllable device is exposed as a switch entity with:
- Device type-specific icons
- Room and flat information as attributes
- Optimistic state updates

### Sensors
- **Connected Devices**: Shows the count of connected devices
- **Connection Status**: Shows tablet connection status

## Technical Details

| Property | Value |
|----------|-------|
| IoT Class | Local Polling |
| Update Interval | 30 seconds |
| Platforms | Switch, Sensor |

## Development

This integration was built using:
- Python 3.11+
- Home Assistant Core APIs
- aiohttp for async HTTP requests
- voluptuous for config validation

## Author

**Emir Aksoy**
- GitHub: [@emirakssoy](https://github.com/emirakssoy)
- LinkedIn: [Emir Aksoy](https://www.linkedin.com/in/emir-aksoy-02a695180/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Developed during my internship at Multitek (July - August 2025)
- Thanks to the Home Assistant community for excellent documentation
