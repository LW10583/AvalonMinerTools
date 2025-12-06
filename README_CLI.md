# Avalon Miner CLI Tool

A comprehensive command-line interface for controlling and monitoring Avalon cryptocurrency miners (Nano 3S, Q models).

## Features

- Monitor miner status, hash rates, temperatures, and pool information
- Configure fan speed, work modes, and target temperatures
- Manage multiple mining pools (configure, enable, disable, switch)
- Reboot miner and perform maintenance tasks
- Get voltage information
- JSON output support for scripting
- Input validation and safety confirmations
- Detailed help for every command

## Requirements

- Python 3.6 or higher
- Network access to Avalon miner on local network
- No external dependencies (uses only Python standard library)

## Installation

1. Make the script executable:
```bash
chmod +x avalon_miner_cli.py
```

2. Optionally, move to a directory in your PATH:
```bash
sudo cp avalon_miner_cli.py /usr/local/bin/avalon-miner
```

## Basic Usage

```bash
python3 avalon_miner_cli.py <MINER_IP> <COMMAND> [OPTIONS]
```

Or if installed in PATH:
```bash
avalon-miner <MINER_IP> <COMMAND> [OPTIONS]
```

## Global Options

- `--port PORT` - API port (default: 4028)
- `--timeout SECONDS` - Connection timeout (default: 5)

## Commands

### Information Commands

#### Get Comprehensive Miner Info
```bash
python3 avalon_miner_cli.py 192.168.1.100 info
```
Combines multiple API calls to show all essential miner information.

#### Get Version Information
```bash
python3 avalon_miner_cli.py 192.168.1.100 version
python3 avalon_miner_cli.py 192.168.1.100 version --json
```
Shows model, serial number, firmware version, MAC address, etc.

#### Get Summary Statistics
```bash
python3 avalon_miner_cli.py 192.168.1.100 summary
```
Shows hash rates (5s, 1m, 5m, 15m, average) and pool statistics.

#### Get Extended Statistics
```bash
python3 avalon_miner_cli.py 192.168.1.100 estats --json
```
Retrieves raw extended statistics (best viewed with --json).

#### Get LCD/Active Pool Information
```bash
python3 avalon_miner_cli.py 192.168.1.100 lcd
```
Shows currently active pool, user, shares, and work information.

#### Get All Pool Configurations
```bash
python3 avalon_miner_cli.py 192.168.1.100 pools
python3 avalon_miner_cli.py 192.168.1.100 pools --json
```
Lists all configured pools with statistics.

### Control Commands

#### Set Fan Speed

**Auto mode (let device control fan):**
```bash
python3 avalon_miner_cli.py 192.168.1.100 set-fan --auto
```

**Exact speed (25-100%):**
```bash
python3 avalon_miner_cli.py 192.168.1.100 set-fan --speed 80
```

**Range mode (min-max):**
```bash
python3 avalon_miner_cli.py 192.168.1.100 set-fan --min-speed 30 --max-speed 100
```

#### Set Work Mode

```bash
# 0 = Low/Eco mode
python3 avalon_miner_cli.py 192.168.1.100 set-work-mode --mode 0

# 1 = Medium/Standard mode
python3 avalon_miner_cli.py 192.168.1.100 set-work-mode --mode 1

# 2 = High/Super mode
python3 avalon_miner_cli.py 192.168.1.100 set-work-mode --mode 2
```

**Work Mode Reference:**
- Mode 0: Low/Eco - Lower power consumption, cooler operation
- Mode 1: Medium/Standard - Balanced performance
- Mode 2: High/Super - Maximum hash rate, higher power/heat

#### Set Target Temperature

```bash
python3 avalon_miner_cli.py 192.168.1.100 set-target-temp --temperature 75
```

Valid range: 50-90°C

**Note:** Target temperature resets to default when miner restarts or work mode changes.

**Default Temperatures:**
- Nano3S Mode 0: 80°C, Mode 1: 85°C, Mode 2: 90°C
- Q Mode 0: 65°C, Mode 1: 80°C, Mode 2: 85°C

#### Get Voltage Information

```bash
python3 avalon_miner_cli.py 192.168.1.100 get-voltage
python3 avalon_miner_cli.py 192.168.1.100 get-voltage --json
```

#### Set Voltage (Advanced - Use with Caution!)

```bash
python3 avalon_miner_cli.py 192.168.1.100 set-voltage --voltage 1150
python3 avalon_miner_cli.py 192.168.1.100 set-voltage --voltage 1150 --force
```

**WARNING:** Setting incorrect voltage can damage your miner! Use --force to skip confirmation.

#### Reboot Miner

```bash
# Immediate reboot
python3 avalon_miner_cli.py 192.168.1.100 reboot

# Reboot with delay (0-300 seconds)
python3 avalon_miner_cli.py 192.168.1.100 reboot --delay 10

# Skip confirmation prompt
python3 avalon_miner_cli.py 192.168.1.100 reboot --force
```

#### Reset Filter Clean Reminder

```bash
python3 avalon_miner_cli.py 192.168.1.100 reset-filter-clean
```

### Pool Management Commands

#### Configure a Pool (Requires Authentication)

```bash
python3 avalon_miner_cli.py 192.168.1.100 set-pool \
  --pool-id 0 \
  --url "stratum+tcp://pool.example.com:3333" \
  --username "worker1" \
  --pool-password "x" \
  --password "admin_password"
```

- `--pool-id`: Pool index (0, 1, or 2)
- `--url`: Pool URL in stratum format
- `--username`: Worker/username for the pool
- `--pool-password`: Pool password (use "x" if not required)
- `--password`: Miner admin password for authentication

#### Enable a Pool

```bash
python3 avalon_miner_cli.py 192.168.1.100 enable-pool --pool-id 1
```

#### Disable a Pool

```bash
python3 avalon_miner_cli.py 192.168.1.100 disable-pool --pool-id 0
```

#### Switch Active Pool

```bash
python3 avalon_miner_cli.py 192.168.1.100 switch-pool --pool-id 1
```

#### Set Pool Priority Order

```bash
# Pool 1 as default, Pool 0 as backup, Pool 2 disabled
python3 avalon_miner_cli.py 192.168.1.100 set-pool-priority --priority "1,0"

# All pools in order: 0, 1, 2
python3 avalon_miner_cli.py 192.168.1.100 set-pool-priority --priority "0,1,2"

# Pool 2 as default, Pool 1 as backup, Pool 0 disabled
python3 avalon_miner_cli.py 192.168.1.100 set-pool-priority --priority "2,1"
```

## Command Reference Table

| Command | Description | Authentication |
|---------|-------------|----------------|
| `info` | Comprehensive miner info | No |
| `version` | Version and hardware info | No |
| `summary` | Hash rate and statistics | No |
| `estats` | Extended statistics | No |
| `lcd` | Active pool information | No |
| `pools` | All pool configurations | No |
| `set-fan` | Control fan speed | No |
| `set-work-mode` | Set work mode (0/1/2) | No |
| `set-target-temp` | Set target temperature | No |
| `get-voltage` | Get voltage info | No |
| `set-voltage` | Set voltage (dangerous!) | No |
| `reboot` | Reboot miner | No |
| `reset-filter-clean` | Reset filter reminder | No |
| `set-pool` | Configure pool | Yes |
| `enable-pool` | Enable a pool | No |
| `disable-pool` | Disable a pool | No |
| `switch-pool` | Switch active pool | No |
| `set-pool-priority` | Set pool priority | No |

## JSON Output

Most commands support `--json` flag for raw JSON output, useful for scripting:

```bash
python3 avalon_miner_cli.py 192.168.1.100 version --json | jq '.VERSION[0].MODEL'
python3 avalon_miner_cli.py 192.168.1.100 summary --json | jq '.SUMMARY."MHS av"'
```

## Examples

### Monitoring Script

```bash
#!/bin/bash
# Monitor multiple miners

MINERS=("192.168.1.100" "192.168.1.101" "192.168.1.102")

for miner in "${MINERS[@]}"; do
    echo "=== Miner $miner ==="
    python3 avalon_miner_cli.py "$miner" info
    echo ""
done
```

### Set All Miners to Eco Mode

```bash
#!/bin/bash
MINERS=("192.168.1.100" "192.168.1.101" "192.168.1.102")

for miner in "${MINERS[@]}"; do
    echo "Setting $miner to Eco mode..."
    python3 avalon_miner_cli.py "$miner" set-work-mode --mode 0
    python3 avalon_miner_cli.py "$miner" set-fan --auto
done
```

### Export Hash Rates to CSV

```bash
#!/bin/bash
echo "Miner,Model,HashRate_Avg,HashRate_5s,HashRate_1m" > hashrates.csv

for miner in 192.168.1.{100..110}; do
    model=$(python3 avalon_miner_cli.py "$miner" version --json 2>/dev/null | jq -r '.VERSION[0].MODEL // "N/A"')
    summary=$(python3 avalon_miner_cli.py "$miner" summary --json 2>/dev/null)

    if [ $? -eq 0 ]; then
        avg=$(echo "$summary" | jq -r '.SUMMARY."MHS av" // 0')
        hs5s=$(echo "$summary" | jq -r '.SUMMARY."MHS 5s" // 0')
        hs1m=$(echo "$summary" | jq -r '.SUMMARY."MHS 1m" // 0')

        echo "$miner,$model,$avg,$hs5s,$hs1m" >> hashrates.csv
    fi
done
```

## Error Handling

The tool includes comprehensive error handling:

- **Invalid IP addresses**: Only accepts private network IPs (10.x, 192.168.x, 172.16-31.x)
- **Connection timeouts**: Configurable with `--timeout`
- **Invalid parameters**: Validates ranges and formats
- **Confirmations**: Prompts for dangerous operations (reboot, voltage changes)

## Network Security

- Only works with private network IP addresses
- Default port 4028 (CGMiner API)
- No encryption (use on trusted local networks only)
- Authentication required only for pool configuration changes

## Troubleshooting

### Connection Refused
```
Error: Connection timeout to 192.168.1.100:4028
```
- Check miner IP address is correct
- Verify miner is powered on and network connected
- Confirm API is enabled on miner
- Check firewall rules

### Invalid IP Address
```
Error: IP address 8.8.8.8 is not a private network address
```
- Tool only accepts local network IPs for security
- Verify you're using the correct local IP

### Command Not Successful
```
Command response: ASC 0 set error
```
- Check parameter values are in valid ranges
- Some commands may not be supported on all models
- Verify miner firmware version

## API Documentation

For detailed API documentation, see: `AVALON_MINER_API_DOCUMENTATION.md`

## Version

- **Version**: 1.0.0
- **Python**: 3.6+
- **License**: Apache-2.0

## Author

Based on AvalonPS7 PowerShell module

## Contributing

Contributions welcome! Please test thoroughly before submitting pull requests.

## Disclaimer

Use this tool at your own risk. Incorrect settings (especially voltage and work mode) can damage your mining hardware. Always monitor your miners after making changes.
