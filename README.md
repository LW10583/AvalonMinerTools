# Avalon Miner Tools

Python CLI tools for controlling and monitoring Avalon cryptocurrency miners (Nano 3S, Q models).

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)
[![Tested](https://img.shields.io/badge/Tested-Avalon%20Nano3s-green.svg)](https://canaan.io/)

## Features

### 🎛️ Single Miner Control (`avalon_miner_cli.py`)
- Control and configure individual Avalon miners
- 18 commands covering all API functionality
- Fan speed, work mode, temperature control
- Pool management (configure, enable, disable, switch)
- JSON output for scripting and automation
- Safety confirmations and input validation

### 📊 Fleet Monitoring (`avalon_fleet.py`)
- Real-time dashboard for multiple miners
- Continuously refreshing status table
- 13 metrics per miner (hash rate, temp, pool, etc.)
- Color-coded status indicators
- Multi-threaded parallel data collection
- IP range support (e.g., `192.168.1.100-110`)
- JSON configuration files

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/avalon-miner-tools.git
cd avalon-miner-tools

# Make scripts executable
chmod +x avalon_miner_cli.py avalon_fleet.py

# Optional: Install to system path
sudo cp avalon_miner_cli.py /usr/local/bin/avalon-miner
sudo cp avalon_fleet.py /usr/local/bin/avalon-fleet
```

### Requirements

- Python 3.6 or higher
- No external dependencies (uses Python standard library only)
- Network access to Avalon miners on local network

### Basic Usage

#### Single Miner Control

```bash
# Get miner information
python3 avalon_miner_cli.py 192.168.1.100 info

# Check hash rates
python3 avalon_miner_cli.py 192.168.1.100 summary

# Set fan speed to 80%
python3 avalon_miner_cli.py 192.168.1.100 set-fan --speed 80

# Set work mode to Eco
python3 avalon_miner_cli.py 192.168.1.100 set-work-mode --mode 0

# Get help
python3 avalon_miner_cli.py --help
```

#### Fleet Monitoring

```bash
# Monitor specific miners
python3 avalon_fleet.py --ips 192.168.1.100 192.168.1.101 192.168.1.102

# Monitor IP range
python3 avalon_fleet.py --ips 192.168.1.100-110

# Use config file
python3 avalon_fleet.py --config fleet_config_example.json

# Custom refresh interval (30 seconds)
python3 avalon_fleet.py --config fleet.json --interval 30
```

## Documentation

- **[README_CLI.md](README_CLI.md)** - Complete guide for single miner control
- **[README_FLEET.md](README_FLEET.md)** - Complete guide for fleet monitoring
- **[AVALON_MINER_API_DOCUMENTATION.md](AVALON_MINER_API_DOCUMENTATION.md)** - Full API reference
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick command reference

## Supported Miners

✅ **Tested and Verified:**
- Avalon Nano 3S (Firmware: 25021401_56abae7)

🟢 **Expected to Work:**
- Avalon Q
- Other Avalon models with CGMiner API

## Example Configuration

Create a `fleet.json` file for fleet monitoring:

```json
{
  "miners": [
    "192.168.1.100",
    "192.168.1.101-110"
  ],
  "interval": 10,
  "port": 4028
}
```

See [fleet_config_example.json](fleet_config_example.json) for more examples.

## Available Commands

### Information Commands
- `version` - Hardware/software version info
- `summary` - Hash rates and statistics
- `info` - Comprehensive overview
- `lcd` - Active pool information
- `pools` - All pool configurations
- `estats` - Extended statistics

### Control Commands
- `set-fan` - Fan speed control (auto/exact/range)
- `set-work-mode` - Performance mode (Eco/Standard/Super)
- `set-target-temp` - Target ASIC temperature
- `get-voltage` - Voltage information
- `reboot` - Reboot miner

### Pool Management
- `set-pool` - Configure pool settings
- `enable-pool` - Enable a pool
- `disable-pool` - Disable a pool
- `switch-pool` - Switch active pool
- `set-pool-priority` - Set pool priority order

## Screenshots

### Single Miner Info
```
================================================================================
AVALON MINER INFORMATION
================================================================================

IP Address       : 192.168.0.154
Model            : Nano3s
Hash Rate (avg)  : 6.56 TH/s
Temperature      : 99°C
Work Mode        : Super
Pool             : fr1.letsmine.it
```

### Fleet Monitor
```
═══════════════════════════════════════════════════════════════════════════
Monitoring 5 miners | Refresh: 10s | Hash Rate: 32.80 TH/s
═══════════════════════════════════════════════════════════════════════════
IP Address      Model    Status   Mode     HR Avg  Temp   Pool
192.168.1.100   Nano3s   Active   Standard 6.56    85°C   pool.example.com
192.168.1.101   Nano3s   Active   Eco      6.20    78°C   pool.example.com
...
```

## API Protocol

- **Protocol**: TCP Socket (CGMiner-based)
- **Port**: 4028 (default)
- **Format**: JSON
- **Response**: Null-byte terminated (handled automatically)

See [AVALON_MINER_API_DOCUMENTATION.md](AVALON_MINER_API_DOCUMENTATION.md) for complete API details.

## Use Cases

### Development & Testing
- Control individual miners during setup
- Test different configurations
- Debug mining issues

### Operations
- Monitor entire fleet in real-time
- Quick health checks
- Identify problem miners
- Track total hash rate

### Automation
- Batch configuration changes
- Scripting with JSON output
- Integration with monitoring systems

## Advanced Examples

### Batch Operation
```bash
#!/bin/bash
# Set all miners to eco mode
for ip in 192.168.1.{100..110}; do
    python3 avalon_miner_cli.py "$ip" set-work-mode --mode 0
    python3 avalon_miner_cli.py "$ip" set-fan --auto
done
```

### Data Export
```bash
# Export hash rates to CSV
python3 avalon_miner_cli.py 192.168.1.100 summary --json | \
    jq -r '.SUMMARY[0]."MHS av"'
```

### Background Monitoring
```bash
# Run fleet monitor in screen
screen -S fleet
python3 avalon_fleet.py --config fleet.json
# Detach: Ctrl+A, D
```

## Troubleshooting

### Connection Issues
```
Error: Connection timeout
```
- Verify miner IP address
- Check network connectivity (`ping`)
- Confirm API port 4028 is open
- Check firewall rules

### Invalid IP Error
```
Error: IP address must be private network
```
- Tool only accepts private IPs (security feature)
- Use 10.x, 192.168.x, or 172.16-31.x ranges

See documentation for more troubleshooting tips.

## Safety Notes

⚠️ **Important:**
- Some commands can affect miner operation
- Monitor temperatures after changes
- Use `--force` flag carefully
- Incorrect voltage settings can damage hardware

## Contributing

Contributions welcome! Please:
1. Test thoroughly with your hardware
2. Update documentation
3. Follow existing code style
4. Submit pull requests

## Credits

This project was inspired by and extracted API knowledge from [AvalonPS7](https://github.com/Gr33nDrag0n69/AvalonPS7) by Gr33nDrag0n69.

The Python implementation is a complete rewrite with additional features:
- Multi-miner fleet monitoring
- Enhanced error handling
- Real-time displays
- IP range support

## License

Apache License 2.0 - See [LICENSE](LICENSE) file for details.

## Version

**Version**: 1.0.0
**Status**: Production Ready ✅
**Tested**: Avalon Nano3s (Firmware 25021401_56abae7)
**Date**: December 2025

## Support

- 📖 Read the [documentation](README_CLI.md)
- 🐛 [Report issues](https://github.com/yourusername/avalon-miner-tools/issues)
- 💬 [Discussions](https://github.com/yourusername/avalon-miner-tools/discussions)

---

**Disclaimer**: Use at your own risk. Always monitor your miners after configuration changes. The authors are not responsible for any hardware damage resulting from use of these tools.
