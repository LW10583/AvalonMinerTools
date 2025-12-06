# Avalon Miner CLI - Quick Reference

## Syntax
```
python3 avalon_miner_cli.py <IP> <COMMAND> [OPTIONS]
```

## Common Commands

### Monitor
```bash
# Quick overview
python3 avalon_miner_cli.py 192.168.1.100 info

# Hash rates
python3 avalon_miner_cli.py 192.168.1.100 summary

# Pools
python3 avalon_miner_cli.py 192.168.1.100 pools

# Version
python3 avalon_miner_cli.py 192.168.1.100 version
```

### Fan Control
```bash
# Auto
python3 avalon_miner_cli.py 192.168.1.100 set-fan --auto

# Exact 80%
python3 avalon_miner_cli.py 192.168.1.100 set-fan --speed 80

# Range 30-100%
python3 avalon_miner_cli.py 192.168.1.100 set-fan --min-speed 30 --max-speed 100
```

### Work Mode
```bash
# Eco (0)
python3 avalon_miner_cli.py 192.168.1.100 set-work-mode --mode 0

# Standard (1)
python3 avalon_miner_cli.py 192.168.1.100 set-work-mode --mode 1

# Super (2)
python3 avalon_miner_cli.py 192.168.1.100 set-work-mode --mode 2
```

### Temperature
```bash
# Set target temp to 75°C
python3 avalon_miner_cli.py 192.168.1.100 set-target-temp --temperature 75
```

### Pool Management
```bash
# View pools
python3 avalon_miner_cli.py 192.168.1.100 pools

# Switch to pool 1
python3 avalon_miner_cli.py 192.168.1.100 switch-pool --pool-id 1

# Enable pool 2
python3 avalon_miner_cli.py 192.168.1.100 enable-pool --pool-id 2

# Disable pool 0
python3 avalon_miner_cli.py 192.168.1.100 disable-pool --pool-id 0

# Set priority (pool 1 primary, pool 0 backup)
python3 avalon_miner_cli.py 192.168.1.100 set-pool-priority --priority "1,0"

# Configure pool (requires admin password)
python3 avalon_miner_cli.py 192.168.1.100 set-pool \
  --pool-id 0 \
  --url "stratum+tcp://pool.example.com:3333" \
  --username "worker1" \
  --pool-password "x" \
  --password "admin_password"
```

### Maintenance
```bash
# Reboot
python3 avalon_miner_cli.py 192.168.1.100 reboot

# Reboot in 30 seconds
python3 avalon_miner_cli.py 192.168.1.100 reboot --delay 30

# Reset filter reminder
python3 avalon_miner_cli.py 192.168.1.100 reset-filter-clean

# Get voltage info
python3 avalon_miner_cli.py 192.168.1.100 get-voltage
```

## Work Modes

| Mode | Name | Description |
|------|------|-------------|
| 0 | Low/Eco | Lower power, cooler, less hash rate |
| 1 | Medium/Standard | Balanced performance |
| 2 | High/Super | Maximum hash rate, higher power/heat |

## Temperature Defaults

| Model | Mode 0 | Mode 1 | Mode 2 |
|-------|--------|--------|--------|
| Nano3S | 80°C | 85°C | 90°C |
| Q | 65°C | 80°C | 85°C |

## Pool IDs

- Pool 0: First pool slot
- Pool 1: Second pool slot
- Pool 2: Third pool slot

## JSON Output

Add `--json` to any command for raw JSON:
```bash
python3 avalon_miner_cli.py 192.168.1.100 version --json
python3 avalon_miner_cli.py 192.168.1.100 summary --json | jq '.SUMMARY."MHS av"'
```

## Help

```bash
# Main help
python3 avalon_miner_cli.py --help

# Command-specific help
python3 avalon_miner_cli.py 192.168.1.1 set-fan --help
python3 avalon_miner_cli.py 192.168.1.1 set-pool --help
```

## Common Options

- `--port PORT` - API port (default: 4028)
- `--timeout SECONDS` - Connection timeout (default: 5)
- `--json` - Output raw JSON (most commands)
- `--force` - Skip confirmation (reboot, set-voltage)

## Error Codes

- Connection timeout: Check IP/network/firewall
- Invalid IP: Only private IPs allowed (10.x, 192.168.x, 172.16-31.x)
- Invalid parameter: Check value ranges

## Safety Notes

- Use `--force` carefully with reboot and voltage commands
- Setting incorrect voltage can damage hardware
- Monitor temperatures after work mode changes
- Target temperature resets on reboot or mode change
