# Multitek Smart Home Integration for Home Assistant

Custom Home Assistant integration for Multitek smart home devices.

> **Note:** This is a mock/demo version. The actual API endpoints and implementation details differ from the production version used at Multitek. This version demonstrates the integration architecture developed during my internship.

## Features

- Control smart home devices (lights, shutters, switches, valves)
- Real-time status updates via polling
- UI-based setup through Config Flow
- Optional API key authentication

## Installation

1. Copy `custom_components/multitek_smart` to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Add integration via Settings → Devices & Services

## Supported Devices

- Lights
- Shutters/Blinds
- On/Off switches
- Gas/Water/Electric valves

## License

MIT License - see [LICENSE](LICENSE)
