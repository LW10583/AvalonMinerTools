# Avalon Fleet Monitor

Real-time monitoring dashboard for multiple Avalon cryptocurrency miners. Continuously displays status for your entire mining fleet in a refreshing table format.

## Features

- 📊 **Real-time Monitoring** - Live status updates for all miners
- 🔄 **Auto-refresh** - Configurable refresh interval (default: 10 seconds)
- 📋 **Comprehensive Display** - 13 metrics per miner
- 🎨 **Color-coded Status** - Active (green), StandBy (yellow), Error (red)
- ⚡ **Multi-threaded** - Fast parallel data collection
- 📁 **Flexible Configuration** - Command-line or JSON config file
- 🌐 **IP Ranges** - Support for IP range notation (e.g., 192.168.1.100-110)
- 📈 **Fleet Summary** - Total hash rate and status counts

## Requirements

- Python 3.6 or higher
- No external dependencies (uses Python standard library only)
- Network access to Avalon miners

## Installation

```bash
# Make the script executable
chmod +x avalon_fleet.py

# Optional: Install to system path
sudo cp avalon_fleet.py /usr/local/bin/avalon-fleet
```

## Quick Start

### Command-line Usage

```bash
# Monitor specific miners
python3 avalon_fleet.py --ips 192.168.1.100 192.168.1.101 192.168.1.102

# Monitor IP range
python3 avalon_fleet.py --ips 192.168.1.100-110

# Custom refresh interval (30 seconds)
python3 avalon_fleet.py --ips 192.168.1.100-105 --interval 30
```

### Config File Usage

```bash
# Monitor from config file
python3 avalon_fleet.py --config fleet.json

# Override interval from command line
python3 avalon_fleet.py --config fleet.json --interval 20
```

## Configuration File Format

Create a JSON file (e.g., `fleet.json`) with your miner configuration:

### Simple Configuration

```json
{
  "miners": [
    "192.168.1.100",
    "192.168.1.101",
    "192.168.1.102"
  ],
  "interval": 10,
  "port": 4028
}
```

### Using IP Ranges

```json
{
  "miners": [
    "192.168.1.100-110"
  ],
  "interval": 15,
  "port": 4028
}
```

### Mixed Configuration

```json
{
  "miners": [
    "192.168.1.100",
    "192.168.1.101-105",
    "192.168.1.200",
    "192.168.1.210-215"
  ],
  "interval": 20,
  "port": 4028
}
```

## Display Columns

The monitoring table shows the following information for each miner:

| Column | Description | Example |
|--------|-------------|---------|
| **IP Address** | Miner IP address | 192.168.1.100 |
| **Model** | Miner model | Nano3S, Q |
| **Status** | Operational status | Active, StandBy, Error |
| **Mode** | Work mode | Eco, Standard, Super |
| **Power** | Max power output | 1200W |
| **HR Cur** | Current hash rate (TH/s) | 25.50 |
| **HR Avg** | Average hash rate (TH/s) | 25.30 |
| **Temp** | ASIC temperature (max) | 85°C |
| **Pool** | Active pool domain | btc.pool.com |
| **Last** | Last share difficulty | 1.2T |
| **Best** | Best share achieved | 5.8T |
| **Rej%** | Rejected share percentage | 0.15% |
| **Uptime** | Miner uptime | 5d12h, 3h45m |

## Status Colors

The **Status** column is color-coded:

- 🟢 **Green (Active)** - Miner is operating normally
- 🟡 **Yellow (StandBy)** - Miner is in standby mode (SoftOFF)
- 🔴 **Red (Error)** - Cannot connect or error occurred

## Fleet Summary

At the bottom of the display:

```
Total: 10 | Active: 8 | StandBy: 1 | Error: 1 | Fleet Hash Rate: 203.45 TH/s
```

- **Total** - Total number of miners being monitored
- **Active** - Miners currently mining (green)
- **StandBy** - Miners in standby mode (yellow)
- **Error** - Miners with errors (red)
- **Fleet Hash Rate** - Combined hash rate of all miners

## Command-line Options

```
usage: avalon_fleet.py [-h] [--ips IP [IP ...]] [--config FILE]
                       [--interval SECONDS] [--port PORT]

options:
  --ips IP [IP ...]     IP addresses of miners (can use ranges)
  --config FILE, -c     Load configuration from JSON file
  --interval SECONDS    Refresh interval in seconds (default: 10)
  --port PORT          API port (default: 4028)
  -h, --help           Show help message
```

## Examples

### Example 1: Monitor Small Fleet

```bash
python3 avalon_fleet.py \
  --ips 192.168.1.100 192.168.1.101 192.168.1.102 \
  --interval 15
```

### Example 2: Monitor IP Range

```bash
# Monitor miners from 192.168.1.100 to 192.168.1.110
python3 avalon_fleet.py --ips 192.168.1.100-110
```

### Example 3: Multiple IP Ranges

```bash
python3 avalon_fleet.py \
  --ips 192.168.1.100-110 192.168.1.200-205
```

### Example 4: Use Config File

Create `my_fleet.json`:
```json
{
  "miners": ["192.168.1.100-120"],
  "interval": 30
}
```

Run:
```bash
python3 avalon_fleet.py --config my_fleet.json
```

### Example 5: Override Config Settings

```bash
# Use config file but override interval
python3 avalon_fleet.py --config fleet.json --interval 5
```

## Sample Display Output

```
=================================================================================================================
AVALON FLEET MONITOR
=================================================================================================================
Monitoring 5 miners | Refresh interval: 10s | Last update: 2025-12-06 08:30:15
=================================================================================================================
IP Address      Model    Status   Mode     Power  HR Cur  HR Avg  Temp   Pool                 Last     Best     Rej%    Uptime
-----------------------------------------------------------------------------------------------------------------
192.168.1.100   Nano3S   Active   Standard 1200W  25.50   25.30   85°C   btc.pool.com         1.2T     5.8T     0.15%   5d12h
192.168.1.101   Nano3S   Active   Eco      800W   18.20   18.15   75°C   btc.pool.com         980.5G   4.2T     0.12%   5d11h
192.168.1.102   Q        Active   Super    1800W  45.80   45.60   82°C   mining.example.com   2.5T     12.3T    0.18%   3d08h
192.168.1.103   Nano3S   StandBy  Eco      N/A    N/A     N/A     N/A    N/A                  N/A      N/A      N/A     5d10h
192.168.1.104   Nano3S   Error    N/A      N/A    N/A     N/A     N/A    N/A                  N/A      N/A      N/A     N/A
  └─ Error: Connection timeout
=================================================================================================================
Total: 5 | Active: 3 | StandBy: 1 | Error: 1 | Fleet Hash Rate: 89.45 TH/s

Press Ctrl+C to exit
```

## How It Works

1. **Initialization**
   - Loads miner list from command-line or config file
   - Expands IP ranges into individual addresses
   - Validates all IP addresses

2. **Data Collection Loop**
   - Spawns parallel threads (one per miner)
   - Each thread fetches data via API calls:
     - `version` - Model information
     - `estats` - Custom Avalon data (work mode, power, temps, etc.)
     - `summary` - Hash rates and rejection stats
     - `lcd` - Active pool and share information
   - Collects results with timeout protection

3. **Display Update**
   - Clears screen
   - Renders formatted table
   - Shows color-coded status
   - Displays fleet summary
   - Waits for next interval

## Performance Considerations

### Recommended Settings

- **Small Fleet (1-10 miners)**: 5-10 second interval
- **Medium Fleet (10-50 miners)**: 10-20 second interval
- **Large Fleet (50+ miners)**: 20-30 second interval

### Timeout Settings

The tool uses a 3-second timeout per miner API call. Total update time depends on:
- Number of miners
- Network latency
- Miner responsiveness

Multi-threading ensures all miners are queried in parallel for best performance.

## Troubleshooting

### Miners Show "Scanning"

**Cause**: Initial scan in progress or slow network

**Solution**: Wait for first refresh cycle to complete

### Miners Show "Error"

**Causes**:
- Miner is offline or unreachable
- Network connectivity issues
- Firewall blocking port 4028
- Wrong IP address

**Solutions**:
- Verify miner is powered on and connected
- Check network connectivity: `ping <miner_ip>`
- Test API manually: `python3 avalon_miner_cli.py <miner_ip> version`
- Check firewall rules

### Display Doesn't Refresh

**Cause**: Terminal doesn't support clear screen

**Solution**: Use a modern terminal (bash, zsh, PowerShell)

### High CPU Usage

**Cause**: Refresh interval too short for large fleet

**Solution**: Increase interval (`--interval 30`)

### "N/A" Values

**Causes**:
- Miner firmware doesn't support that metric
- API response format difference
- Miner in standby mode

**Solutions**:
- Check miner status
- Update miner firmware
- Some values only available when mining actively

## Keyboard Controls

- **Ctrl+C** - Exit the monitor gracefully

## Integration Examples

### Run as Background Service

```bash
# Using screen
screen -S fleet-monitor
python3 avalon_fleet.py --config fleet.json
# Detach with Ctrl+A, D

# Reattach later
screen -r fleet-monitor
```

### Run in tmux

```bash
# Create tmux session
tmux new -s fleet
python3 avalon_fleet.py --config fleet.json
# Detach with Ctrl+B, D

# Reattach later
tmux attach -t fleet
```

### Systemd Service (Linux)

Create `/etc/systemd/system/avalon-fleet.service`:

```ini
[Unit]
Description=Avalon Fleet Monitor
After=network.target

[Service]
Type=simple
User=miner
WorkingDirectory=/home/miner/avalon
ExecStart=/usr/bin/python3 /usr/local/bin/avalon_fleet.py --config /home/miner/avalon/fleet.json
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable avalon-fleet
sudo systemctl start avalon-fleet
sudo systemctl status avalon-fleet
```

## Comparison with Single Miner Tool

| Feature | avalon_miner_cli.py | avalon_fleet.py |
|---------|---------------------|-----------------|
| Purpose | Control single miner | Monitor multiple miners |
| Display | One-time output | Continuous refresh |
| Commands | All 18 API commands | Read-only monitoring |
| Usage | Configuration changes | Status monitoring |
| Output | Detailed per command | Summary table |
| Threading | Single | Multi-threaded |

**Use Cases**:
- **avalon_miner_cli.py** - For configuring individual miners, making changes, detailed investigation
- **avalon_fleet.py** - For monitoring overall fleet health, quick status overview, NOC displays

## Tips & Best Practices

1. **Start Small**: Test with 1-2 miners before monitoring entire fleet
2. **Adjust Interval**: Balance between real-time updates and network load
3. **Use IP Ranges**: Simplifies configuration for sequential IPs
4. **Config Files**: Better for permanent setups, easier to manage
5. **Screen/tmux**: Keep monitor running in background
6. **Large Displays**: Works best on wide terminals (165+ columns)
7. **Network Placement**: Run on same network segment as miners for best performance

## Advanced Configuration

### Custom Port

If your miners use a non-standard API port:

```json
{
  "miners": ["192.168.1.100-110"],
  "interval": 10,
  "port": 8080
}
```

### Multiple Subnets

```json
{
  "miners": [
    "192.168.1.100-110",
    "192.168.2.100-110",
    "10.0.0.100-110"
  ],
  "interval": 15
}
```

## Known Limitations

1. **Terminal Size**: Requires ~165 columns for full display
2. **API Only**: Cannot configure miners (use `avalon_miner_cli.py` for that)
3. **Polling Based**: Not real-time push notifications
4. **Network Dependent**: Performance limited by network latency
5. **No Historical Data**: Shows current status only (no logging/graphing)

## Future Enhancements (Potential)

- Historical data logging
- Alert notifications (email, Telegram, Discord)
- Web dashboard interface
- Temperature/hash rate warnings
- Export to CSV/JSON
- Sorting options
- Filter by status
- Summary statistics

## Version

- **Version**: 1.0.0
- **Python**: 3.6+
- **License**: Apache-2.0

## See Also

- [avalon_miner_cli.py](README_CLI.md) - Single miner control tool
- [API Documentation](AVALON_MINER_API_DOCUMENTATION.md) - Complete API reference
- [Quick Reference](QUICK_REFERENCE.md) - Command cheat sheet

---

**Need Help?**

1. Run with `--help` flag: `python3 avalon_fleet.py --help`
2. Check your config file JSON syntax
3. Test individual miners with `avalon_miner_cli.py` first
4. Verify network connectivity with `ping`
