# Avalon Crypto Miner API Documentation

## Overview

This document describes the API commands used to interact with Avalon cryptocurrency miners (e.g., Avalon Nano 3S, Avalon Q). The API is based on CGMiner's API protocol and uses TCP socket connections on port 4028 (default).

## Connection Details

- **Protocol**: TCP Socket
- **Default Port**: 4028
- **Format**: JSON
- **IP Address**: Local network IPv4 (10.x.x.x, 192.168.x.x, or 172.16-31.x.x)
- **Response Termination**: Null byte (`\x00`) appended to response

## API Request Format

Commands are sent as JSON objects over a TCP connection:

```json
{
  "command": "command_name"
}
```

For commands with parameters:

```json
{
  "command": "command_name",
  "parameter": "param1,param2,param3"
}
```

## Response Format and Parsing

### General Response Structure

All API responses follow this structure:

```json
{
  "STATUS": [
    {
      "STATUS": "S",
      "When": 1765004019,
      "Code": 22,
      "Msg": "Message text",
      "Description": "cgminer 4.11.1"
    }
  ],
  "RESPONSE_TYPE": [
    { ...response data... }
  ],
  "id": 1
}
```

### Important Response Characteristics

**Tested with Avalon Nano3s (Firmware: 25021401_56abae7, CGMiner 4.11.1, API 3.7)**

1. **Null Byte Termination**
   - Responses are terminated with a null byte (`\x00`)
   - **Critical**: Must strip this before JSON parsing
   - Failing to remove the null byte causes JSON decode errors

   ```python
   # Correct parsing
   response_str = response.decode('utf-8').rstrip('\x00').strip()
   data = json.loads(response_str)
   ```

2. **Array-based Response Fields**
   - Most response fields are **arrays**, not direct objects
   - Even single-item responses use array format
   - **Must access first element** `[0]` to get data

   Affected fields:
   - `STATUS` - Always an array (single element)
   - `VERSION` - Array (single element)
   - `SUMMARY` - Array (single element)
   - `LCD` - Array (single element)
   - `POOLS` - Array (multiple elements for multiple pools)

   ```python
   # Correct access pattern
   version = response['VERSION'][0]  # Not response['VERSION']
   summary = response['SUMMARY'][0]  # Not response['SUMMARY']
   lcd = response['LCD'][0]          # Not response['LCD']
   ```

3. **Response Timing**
   - Recommended delay after send: 50-100ms
   - Socket read timeout: 3-5 seconds recommended
   - Response is typically immediate (<100ms) for healthy miners

4. **Connection Handling**
   - One request per connection
   - Close connection after receiving response
   - No keep-alive or connection pooling

## Information Retrieval Commands (Read-Only)

### 1. version

**Description**: Retrieves hardware and software version information about the miner.

**Command**: `version`

**Parameters**: None

**Response Fields**:
- `PROD` - Product name
- `MODEL` - Model identifier
- `HWTYPE` - Hardware type
- `SWTYPE` - Software type
- `CGMiner` - CGMiner version
- `API` - API version
- `LVERSION` / `BVERSION` / `CGVERSION` - Firmware version
- `DNA` - Serial number (unique device identifier)
- `MAC` - MAC address

**Request Example**:
```json
{"command": "version"}
```

**Real Response Example** (Avalon Nano3s):
```json
{
  "STATUS": [
    {
      "STATUS": "S",
      "When": 1765004019,
      "Code": 22,
      "Msg": "CGMiner versions",
      "Description": "cgminer 4.11.1"
    }
  ],
  "VERSION": [
    {
      "CGMiner": "4.11.1",
      "API": "3.7",
      "PROD": "Avalon Nano3s",
      "MODEL": "Nano3s",
      "HWTYPE": "N_MM1v1_X1",
      "SWTYPE": "MM319",
      "LVERSION": "25021401_56abae7",
      "BVERSION": "25021401_56abae7",
      "CGVERSION": "25021401_56abae7",
      "DNA": "020100003cbe4d15",
      "MAC": "e0e1a93f3053",
      "UPAPI": "2"
    }
  ],
  "id": 1
}
```

**Note**: Response includes null byte terminator. Access via `response['VERSION'][0]`.

---

### 2. summary

**Description**: Retrieves summary statistics about the miner's operation.

**Command**: `summary`

**Parameters**: None

**Response Fields**:
- `MHS av` - Average hash rate (MH/s)
- `MHS 5s` - Hash rate over last 5 seconds (MH/s)
- `MHS 1m` - Hash rate over last 1 minute (MH/s)
- `MHS 5m` - Hash rate over last 5 minutes (MH/s)
- `MHS 15m` - Hash rate over last 15 minutes (MH/s)
- `Pool Rejected%` - Percentage of rejected shares
- `Pool Stale%` - Percentage of stale shares

**Request Example**:
```json
{"command": "summary"}
```

**Real Response Example** (Avalon Nano3s, partial):
```json
{
  "STATUS": [
    {
      "STATUS": "S",
      "When": 1765004063,
      "Code": 11,
      "Msg": "Summary",
      "Description": "cgminer 4.11.1"
    }
  ],
  "SUMMARY": [
    {
      "Elapsed": 133923,
      "MHS av": 6564727.78,
      "MHS 5s": 5443351.11,
      "MHS 1m": 6649033.64,
      "MHS 5m": 6306581.2,
      "MHS 15m": 6380441.6,
      "Found Blocks": 0,
      "Accepted": 2612,
      "Rejected": 2,
      "Hardware Errors": 0,
      "Utility": 1.17,
      "Stale": 14,
      "Best Share": 224199508,
      "Device Rejected%": 0.0861,
      "Pool Rejected%": 0.0875,
      "Pool Stale%": 0.2778,
      "Difficulty Accepted": 200844480.0,
      "Difficulty Rejected": 176384.0
    }
  ],
  "id": 1
}
```

**Note**:
- Hash rates in MH/s (divide by 1,000,000 for TH/s)
- Example shows 6.56 TH/s average hash rate
- Access via `response['SUMMARY'][0]`

---

### 3. estats

**Description**: Retrieves extended statistics including custom Avalon-specific data embedded in the response.

**Command**: `estats`

**Parameters**: None

**Response Contains**: A special custom data format embedded in `STATS['MM ID0']` or `STATS['MM ID0:Summary']` with key-value pairs in the format `Key[Value]`.

**Custom Data Fields** (parsed from response):
- `Ver` - Model version
- `Core` - Core identifier
- `BVer` - Board version / firmware
- `SoftOFF` - Soft power state (0 = Active, >0 = StandBy)
- `WORKMODE` - Work mode (0 = Low/Eco, 1 = Medium/Standard, 2 = High/Super)
- `MPO` - Max Power Output (Watts)
- `Elapsed` - Uptime in seconds
- `GHSavg` - Average hash rate (GH/s)
- `GHSmm` - Momentary hash rate (GH/s)
- `GHSspd` - Current hash rate (GH/s)
- `MGHS` - Measured hash rate (GH/s)
- `FanR` - Fan speed percentage
- `Fan1`, `Fan2`, `Fan3`, `Fan4` - Individual fan speeds (RPM)
- `ITemp` - Case inlet temperature (°C)
- `HBITemp` - Hashboard inlet temperature (°C)
- `HBOTemp` - Hashboard outlet temperature (°C)
- `TarT` - Target ASIC temperature (°C)
- `TAvg` - Average ASIC temperature (°C)
- `TMax` - Maximum ASIC temperature (°C)
- `PING` - Pool ping time (ms)

**Example**:
```json
{"command": "estats"}
```

---

### 4. lcd

**Description**: Retrieves LCD display information about the active pool.

**Command**: `lcd`

**Parameters**: None

**Response Fields**:
- `Current Pool` - Currently active pool address
- `User` - Pool username
- `Last Valid Work` - Unix timestamp of last valid work
- `Last Share Difficulty` - Difficulty of last submitted share
- `Best Share` - Best share difficulty achieved
- `Found Blocks` - Number of blocks found

**Request Example**:
```json
{"command": "lcd"}
```

**Real Response Example** (Avalon Nano3s):
```json
{
  "STATUS": [
    {
      "STATUS": "S",
      "When": 1765004151,
      "Code": 125,
      "Msg": "LCD",
      "Description": "cgminer 4.11.1"
    }
  ],
  "LCD": [
    {
      "Elapsed": 134010,
      "GHS av": 6564.14,
      "GHS 5m": 6158.25,
      "GHS 5s": 6477.09,
      "Temperature": 0.0,
      "Last Share Difficulty": 40000.0,
      "Last Share Time": 1765004143,
      "Best Share": 224199508,
      "Last Valid Work": 1765004143,
      "Found Blocks": 0,
      "Current Pool": "stratum+tcp://fr1.letsmine.it:3339",
      "User": "myt1qnw6vzu0thguwtw6rlj4lz7f02vmlk9k5e7h4hy.Nano3s-01"
    }
  ],
  "id": 1
}
```

**Note**:
- Hash rates in GH/s (divide by 1,000 for TH/s)
- Timestamps are Unix epoch times
- Access via `response['LCD'][0]`

---

### 5. pools

**Description**: Retrieves configuration and statistics for all configured mining pools (0-2).

**Command**: `pools`

**Parameters**: None

**Response Fields** (per pool):
- `POOL` - Pool index (0, 1, or 2)
- `URL` - Pool URL
- `Status` - Pool status (Alive, Dead, etc.)
- `Priority` - Pool priority
- `Getworks` - Number of getworks received
- `Accepted` - Number of accepted shares
- `Rejected` - Number of rejected shares
- `Works` - Total works
- `Discarded` - Discarded shares
- `Stale` - Stale shares
- `Get Failures` - Number of get failures
- `Remote Failures` - Number of remote failures
- `User` - Pool username
- `Last Share Time` - Unix timestamp of last share
- `Has Stratum` - Whether pool supports Stratum
- `Stratum Active` - Whether Stratum is active
- `Stratum URL` - Stratum URL
- `Stratum Difficulty` - Current Stratum difficulty
- `Best Share` - Best share difficulty for this pool
- `Pool Rejected%` - Rejection percentage for this pool
- `Pool Stale%` - Stale percentage for this pool
- `Bad Work` - Count of bad work
- `Current Block Height` - Current blockchain height
- `Current Block Version` - Current block version

**Example**:
```json
{"command": "pools"}
```

---

## Configuration Commands (Write Operations)

### 6. ascset - Fan Speed Control

**Description**: Sets the fan speed of the miner.

**Command**: `ascset`

**Parameters**: `0,fan-spd,<value>`

**Value Options**:
- `-1` - Auto mode (device auto-adjusts)
- `25-100` - Exact speed percentage
- `25..100` - Range format (min..max)

**Examples**:
```json
{"command": "ascset", "parameter": "0,fan-spd,-1"}
{"command": "ascset", "parameter": "0,fan-spd,80"}
{"command": "ascset", "parameter": "0,fan-spd,30..100"}
```

**Valid Range**: 25-100%

---

### 7. ascset - Work Mode

**Description**: Sets the operating work mode of the miner.

**Command**: `ascset`

**Parameters**: `0,workmode,set,<mode>`

**Mode Values**:
- `0` - Low / Eco mode
- `1` - Medium / Standard mode
- `2` - High / Super mode

**Example**:
```json
{"command": "ascset", "parameter": "0,workmode,set,1"}
```

---

### 8. ascset - Target Temperature

**Description**: Sets the target ASIC temperature.

**Command**: `ascset`

**Parameters**: `0,target-temp,<temperature>`

**Temperature Range**: 50-90°C

**Default Temperatures by Model and Mode**:
- Nano3S Mode 0: 80°C
- Nano3S Mode 1: 85°C
- Nano3S Mode 2: 90°C
- Q Mode 0: 65°C
- Q Mode 1: 80°C
- Q Mode 2: 85°C

**Example**:
```json
{"command": "ascset", "parameter": "0,target-temp,75"}
```

**Note**: Target temperature resets to default when miner restarts or work mode changes.

---

### 9. ascset - Voltage Control

**Description**: Retrieves (GET) or sets (SET) PSU/power voltage information.

**Command**: `ascset`

**Parameters (GET)**: `0,voltage`

**Parameters (SET)**: `0,voltage,<value>`

**Response Format** (GET): Returns a string `PS[n0 n1 n2 n3 n4 n5 n6 n7 n8]` where:
- Index 0: Error code (0 = OK)
- Index 1: Reserved
- Index 2: Output voltage (raw device units, often mV)
- Index 3: Output current (raw units)
- Index 4: Reserved
- Index 5: Commanded voltage
- Index 6: Output power (raw, likely watts)
- Index 7: Minimum allowed voltage (for validation)
- Index 8: Maximum allowed voltage (for validation)

**Examples**:
```json
{"command": "ascset", "parameter": "0,voltage"}
{"command": "ascset", "parameter": "0,voltage,1150"}
```

**Note**: Valid voltage range is device-specific and read from the device's allowed range.

---

### 10. ascset - Reboot

**Description**: Reboots the miner.

**Command**: `ascset`

**Parameters**: `0,reboot,<delay>`

**Delay Range**: 0-300 seconds

**Example**:
```json
{"command": "ascset", "parameter": "0,reboot,0"}
{"command": "ascset", "parameter": "0,reboot,10"}
```

---

### 11. ascset - Filter Clean Reset

**Description**: Resets the filter clean reminder.

**Command**: `ascset`

**Parameters**: `0,filter-clean,1`

**Example**:
```json
{"command": "ascset", "parameter": "0,filter-clean,1"}
```

---

## Pool Management Commands

### 12. setpool

**Description**: Configures (replaces) a pool entry.

**Command**: `setpool`

**Parameters**: `admin,<password>,<pool_id>,<url>,<username>,<pool_password>`

**Parameter Details**:
- `admin` - Fixed string literal
- `password` - Miner admin password (required for authentication)
- `pool_id` - Pool index: 0, 1, or 2
- `url` - Pool URL (e.g., `stratum+tcp://example.com:3333`)
- `username` - Pool worker username
- `pool_password` - Pool password (use 'x' if none required)

**Example**:
```json
{
  "command": "setpool",
  "parameter": "admin,myAdminPass,0,stratum+tcp://pool.example.com:3333,worker1,x"
}
```

**Authentication**: Required (admin password)

---

### 13. enablepool

**Description**: Enables a specific mining pool.

**Command**: `enablepool`

**Parameters**: `<pool_id>`

**Pool ID Range**: 0-2

**Example**:
```json
{"command": "enablepool", "parameter": "1"}
```

---

### 14. disablepool

**Description**: Disables a specific mining pool.

**Command**: `disablepool`

**Parameters**: `<pool_id>`

**Pool ID Range**: 0-2

**Example**:
```json
{"command": "disablepool", "parameter": "0"}
```

---

### 15. switchpool

**Description**: Switches to a specific pool as the active pool.

**Command**: `switchpool`

**Parameters**: `<pool_id>`

**Pool ID Range**: 0-2

**Example**:
```json
{"command": "switchpool", "parameter": "1"}
```

---

### 16. poolpriority

**Description**: Sets the priority ordering of pools.

**Command**: `poolpriority`

**Parameters**: `<priority_list>`

**Priority List Format**: Comma-separated pool IDs in priority order

**Examples**:
- `1,0` - Pool 1 as default, Pool 0 as backup, Pool 2 disabled
- `0,1,2` - Pool 0 as default, Pool 1 as first backup, Pool 2 as second backup
- `2,1` - Pool 2 as default, Pool 1 as backup, Pool 0 disabled

**Example**:
```json
{"command": "poolpriority", "parameter": "1,0"}
```

---

## Response Format

All API responses follow this general structure:

```json
{
  "STATUS": {
    "Msg": "Status message",
    "Code": 0,
    "Description": "Success"
  },
  "RESPONSE_TYPE": {
    ...response data...
  }
}
```

For successful `ascset` commands:
```json
{
  "STATUS": {
    "Msg": "ASC 0 set OK",
    ...
  }
}
```

For errors, the `STATUS.Msg` field will contain error details.

---

## Implementation Notes

1. **Connection Handling**:
   - Create TCP socket connection to miner IP on port 4028
   - Send JSON command as UTF-8 string
   - Wait 100ms after sending
   - Read response until end
   - Close connection

2. **Hash Rate Conversions**:
   - Custom Data fields (GHSavg, etc.): Divide by 1000 to convert GH/s to TH/s
   - Summary fields (MHS av, etc.): Divide by 1,000,000 to convert MH/s to TH/s

3. **Temperature Units**: All temperatures are in Celsius (°C)

4. **Time Conversions**: Unix timestamps (e.g., `Last Valid Work`) should be converted to local datetime

5. **Difficulty Display**: Large difficulty values should be formatted with appropriate units (K, M, G, T, P)

6. **Model Differences**:
   - Nano 3S: Single fan (Fan1 only)
   - Q Model: Four fans (Fan1-4), additional temperature sensors (ITemp, HBITemp, HBOTemp)

7. **Security**:
   - Pool configuration changes require admin password authentication
   - Only local network IP addresses are supported
   - Validate IP addresses are in private ranges (10.x, 192.168.x, 172.16-31.x)

---

## Quick Reference Table

| Command | Type | Authentication | Description |
|---------|------|----------------|-------------|
| `version` | Read | No | Get version info |
| `summary` | Read | No | Get summary statistics |
| `estats` | Read | No | Get extended statistics |
| `lcd` | Read | No | Get LCD/active pool info |
| `pools` | Read | No | Get all pool configurations |
| `ascset` (fan-spd) | Write | No | Set fan speed |
| `ascset` (workmode) | Write | No | Set work mode |
| `ascset` (target-temp) | Write | No | Set target temperature |
| `ascset` (voltage) | Read/Write | No | Get/Set voltage |
| `ascset` (reboot) | Write | No | Reboot miner |
| `ascset` (filter-clean) | Write | No | Reset filter reminder |
| `setpool` | Write | Yes | Configure pool |
| `enablepool` | Write | No | Enable pool |
| `disablepool` | Write | No | Disable pool |
| `switchpool` | Write | No | Switch active pool |
| `poolpriority` | Write | No | Set pool priority order |

---

## Code Example (PowerShell Implementation)

```powershell
function Invoke-AvalonAPI {
    param (
        [string] $IP,
        [int] $Port = 4028,
        [string] $Command,
        [string] $Params = ''
    )

    $client = New-Object System.Net.Sockets.TcpClient
    $client.Connect($IP, $Port)

    if ($Params -ne '') {
        $JsonCommand = @{
            command   = "$Command"
            parameter = "$Params"
        } | ConvertTo-Json -Compress
    } else {
        $JsonCommand = @{
            command = "$Command"
        } | ConvertTo-Json -Compress
    }

    $stream = $client.GetStream()
    $writer = New-Object System.IO.StreamWriter($stream)
    $reader = New-Object System.IO.StreamReader($stream)

    $writer.AutoFlush = $true
    $writer.Write($JsonCommand)
    $writer.Flush()
    Start-Sleep -Milliseconds 100
    $response = $reader.ReadToEnd()
    $client.Close()

    $response | ConvertFrom-Json
}

# Example usage:
$result = Invoke-AvalonAPI -IP "192.168.1.100" -Command "version"
$result = Invoke-AvalonAPI -IP "192.168.1.100" -Command "ascset" -Params "0,fan-spd,80"
```

---

## Real-World Testing Results

**Tested Configuration:**
- **Device**: Avalon Nano3s
- **Firmware**: 25021401_56abae7
- **CGMiner**: 4.11.1
- **API Version**: 3.7
- **Test Date**: December 6, 2025

### Key Findings

1. **Response Termination**
   - All responses terminate with null byte (`\x00`)
   - This MUST be stripped before JSON parsing
   - Python: `response.decode('utf-8').rstrip('\x00').strip()`

2. **Array Format**
   - All major response fields are arrays, even for single items
   - Always use `[0]` to access: `response['VERSION'][0]`
   - Applies to: VERSION, SUMMARY, LCD, STATUS

3. **Performance**
   - Response time: <100ms for healthy miner
   - Recommended socket timeout: 3-5 seconds
   - Post-send delay: 50-100ms

4. **Hash Rate Units**
   - SUMMARY: MH/s (divide by 1,000,000 for TH/s)
   - LCD: GH/s (divide by 1,000 for TH/s)
   - Example miner: ~6.56 TH/s average

5. **Temperature Reporting**
   - LCD `Temperature` field may be 0.0 (use estats for accurate temps)
   - Custom data in estats provides detailed temperature metrics

6. **Pool Information**
   - Full stratum URLs returned (e.g., `stratum+tcp://fr1.letsmine.it:3339`)
   - Worker names included in LCD `User` field
   - Best Share stored as raw difficulty value (e.g., 224199508 = 224.20M)

### Common Pitfalls

❌ **Incorrect**: Direct object access
```python
summary = response['SUMMARY']  # Returns array!
hashrate = summary['MHS av']    # Error: list has no attribute 'get'
```

✅ **Correct**: Array access
```python
summary = response['SUMMARY'][0]  # Get first element
hashrate = summary['MHS av']      # Works correctly
```

❌ **Incorrect**: No null byte handling
```python
data = json.loads(response.decode('utf-8'))  # Fails with "Extra data"
```

✅ **Correct**: Strip null byte
```python
data = json.loads(response.decode('utf-8').rstrip('\x00').strip())
```

### Recommended Implementation Pattern

```python
import socket
import json
import time

def send_avalon_command(ip, port, command, params=''):
    # Build JSON command
    if params:
        json_cmd = json.dumps({
            "command": command,
            "parameter": params
        }, separators=(',', ':'))
    else:
        json_cmd = json.dumps({
            "command": command
        }, separators=(',', ':'))

    # Connect and send
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((ip, port))
    sock.sendall(json_cmd.encode('utf-8'))

    # Wait for response
    time.sleep(0.1)

    # Receive data
    response = b''
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        except socket.timeout:
            break

    sock.close()

    # Parse (critical: strip null byte)
    response_str = response.decode('utf-8').rstrip('\x00').strip()
    data = json.loads(response_str)

    return data

# Usage
response = send_avalon_command('192.168.0.154', 4028, 'version')
version_info = response['VERSION'][0]  # Note: array access
print(f"Model: {version_info['MODEL']}")
```

---

## Version Information

- **Document Version**: 1.1.0
- **Based on**: AvalonPS7 PowerShell Module
- **API Protocol**: CGMiner-based
- **Supported Models**: Avalon Nano 3S, Avalon Q
- **Testing**: Verified with Avalon Nano3s (Firmware 25021401_56abae7)
- **Date**: December 2025

---

## License

Copyright (c) 2025 Gr33nDrag0n69
SPDX-License-Identifier: Apache-2.0
