#!/bin/bash
#
# Example usage script for Avalon Miner CLI
# Demonstrates various commands and use cases
#

# Configuration
MINER_IP="192.168.1.100"
CLI="python3 avalon_miner_cli.py"

echo "======================================================================"
echo "Avalon Miner CLI - Example Usage"
echo "======================================================================"
echo ""
echo "Note: This is a demonstration script. Adjust MINER_IP before running."
echo "Current MINER_IP: $MINER_IP"
echo ""

# Example 1: Get comprehensive miner information
echo "Example 1: Get Miner Info"
echo "Command: $CLI $MINER_IP info"
echo ""
# $CLI $MINER_IP info

# Example 2: Check version
echo "Example 2: Get Version Information"
echo "Command: $CLI $MINER_IP version"
echo ""
# $CLI $MINER_IP version

# Example 3: Get hash rate summary
echo "Example 3: Get Hash Rate Summary"
echo "Command: $CLI $MINER_IP summary"
echo ""
# $CLI $MINER_IP summary

# Example 4: View all pools
echo "Example 4: View Pool Configuration"
echo "Command: $CLI $MINER_IP pools"
echo ""
# $CLI $MINER_IP pools

# Example 5: Set fan to auto mode
echo "Example 5: Set Fan to Auto Mode"
echo "Command: $CLI $MINER_IP set-fan --auto"
echo ""
# $CLI $MINER_IP set-fan --auto

# Example 6: Set fan to exact speed
echo "Example 6: Set Fan to 80%"
echo "Command: $CLI $MINER_IP set-fan --speed 80"
echo ""
# $CLI $MINER_IP set-fan --speed 80

# Example 7: Set work mode to eco
echo "Example 7: Set Work Mode to Eco (0)"
echo "Command: $CLI $MINER_IP set-work-mode --mode 0"
echo ""
# $CLI $MINER_IP set-work-mode --mode 0

# Example 8: Set target temperature
echo "Example 8: Set Target Temperature to 75°C"
echo "Command: $CLI $MINER_IP set-target-temp --temperature 75"
echo ""
# $CLI $MINER_IP set-target-temp --temperature 75

# Example 9: Switch to pool 1
echo "Example 9: Switch to Pool 1"
echo "Command: $CLI $MINER_IP switch-pool --pool-id 1"
echo ""
# $CLI $MINER_IP switch-pool --pool-id 1

# Example 10: Get JSON output
echo "Example 10: Get Version as JSON"
echo "Command: $CLI $MINER_IP version --json | jq '.VERSION[0].MODEL'"
echo ""
# $CLI $MINER_IP version --json | jq '.VERSION[0].MODEL'

echo ""
echo "======================================================================"
echo "Batch Operations Examples"
echo "======================================================================"
echo ""

# Example 11: Monitor multiple miners
echo "Example 11: Monitor Multiple Miners"
cat << 'EOF'
#!/bin/bash
MINERS=("192.168.1.100" "192.168.1.101" "192.168.1.102")

for miner in "${MINERS[@]}"; do
    echo "=== Miner: $miner ==="
    python3 avalon_miner_cli.py "$miner" info
    echo ""
done
EOF
echo ""

# Example 12: Set all miners to eco mode
echo "Example 12: Set All Miners to Eco Mode"
cat << 'EOF'
#!/bin/bash
MINERS=("192.168.1.100" "192.168.1.101" "192.168.1.102")

for miner in "${MINERS[@]}"; do
    echo "Configuring $miner for eco mode..."
    python3 avalon_miner_cli.py "$miner" set-work-mode --mode 0
    python3 avalon_miner_cli.py "$miner" set-fan --auto
    python3 avalon_miner_cli.py "$miner" set-target-temp --temperature 70
    echo "Done: $miner"
    echo ""
done
EOF
echo ""

# Example 13: Export hash rates to CSV
echo "Example 13: Export Hash Rates to CSV"
cat << 'EOF'
#!/bin/bash
echo "IP,Model,Serial,HashRate_Avg_TH" > miners_hashrate.csv

for ip in 192.168.1.{100..110}; do
    echo "Checking $ip..."

    # Get version info
    version_json=$(python3 avalon_miner_cli.py "$ip" version --json 2>/dev/null)
    if [ $? -ne 0 ]; then
        continue
    fi

    model=$(echo "$version_json" | jq -r '.VERSION[0].MODEL // "N/A"')
    serial=$(echo "$version_json" | jq -r '.VERSION[0].DNA // "N/A"')

    # Get summary
    summary_json=$(python3 avalon_miner_cli.py "$ip" summary --json 2>/dev/null)
    if [ $? -ne 0 ]; then
        continue
    fi

    mhs_avg=$(echo "$summary_json" | jq -r '.SUMMARY."MHS av" // 0')
    ths_avg=$(echo "scale=2; $mhs_avg / 1000000" | bc)

    echo "$ip,$model,$serial,$ths_avg" >> miners_hashrate.csv
    echo "  Model: $model, Hash Rate: ${ths_avg} TH/s"
done

echo ""
echo "Export complete: miners_hashrate.csv"
EOF
echo ""

# Example 14: Health check with alerts
echo "Example 14: Health Check with Temperature Alert"
cat << 'EOF'
#!/bin/bash
MINERS=("192.168.1.100" "192.168.1.101")
TEMP_THRESHOLD=85

for miner in "${MINERS[@]}"; do
    # Get extended stats (contains temperature)
    lcd_json=$(python3 avalon_miner_cli.py "$miner" lcd --json 2>/dev/null)

    if [ $? -eq 0 ]; then
        # Note: Actual temperature extraction depends on estats parsing
        # This is a simplified example
        echo "Miner $miner: OK"
    else
        echo "Miner $miner: ERROR - Cannot connect"
    fi
done
EOF
echo ""

# Example 15: Scheduled reboot
echo "Example 15: Schedule Delayed Reboot (30 seconds)"
echo "Command: $CLI $MINER_IP reboot --delay 30 --force"
echo ""
# $CLI $MINER_IP reboot --delay 30 --force

echo ""
echo "======================================================================"
echo "JSON Processing Examples (requires jq)"
echo "======================================================================"
echo ""

echo "Extract Model:"
echo "  $CLI $MINER_IP version --json | jq -r '.VERSION[0].MODEL'"
echo ""

echo "Extract Serial Number:"
echo "  $CLI $MINER_IP version --json | jq -r '.VERSION[0].DNA'"
echo ""

echo "Extract Average Hash Rate (MH/s):"
echo "  $CLI $MINER_IP summary --json | jq -r '.SUMMARY.\"MHS av\"'"
echo ""

echo "Extract Pool Rejected %:"
echo "  $CLI $MINER_IP summary --json | jq -r '.SUMMARY.\"Pool Rejected%\"'"
echo ""

echo "List all pool URLs:"
echo "  $CLI $MINER_IP pools --json | jq -r '.POOLS[].URL'"
echo ""

echo ""
echo "======================================================================"
echo "End of Examples"
echo "======================================================================"
echo ""
echo "To use these examples:"
echo "1. Uncomment the command lines (remove leading #)"
echo "2. Set MINER_IP to your actual miner IP address"
echo "3. Run: bash example_usage.sh"
echo ""
echo "For help on any command:"
echo "  $CLI $MINER_IP <command> --help"
echo ""
