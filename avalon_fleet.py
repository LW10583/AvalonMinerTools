#!/usr/bin/env python3
"""
Avalon Fleet Monitor

Real-time monitoring dashboard for multiple Avalon cryptocurrency miners.
Displays continuously refreshing status table for your entire mining fleet.

Copyright (c) 2025
SPDX-License-Identifier: Apache-2.0
"""

import sys
import json
import socket
import argparse
import ipaddress
import time
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from threading import Thread, Lock
from queue import Queue


@dataclass
class MinerStatus:
    """Data class for miner status"""
    ip: str
    model: str = "N/A"
    status: str = "Unknown"
    work_mode: str = "N/A"
    power: str = "N/A"
    hashrate_current: str = "N/A"
    hashrate_average: str = "N/A"
    temp_asic: str = "N/A"
    active_pool: str = "N/A"
    last_share_diff: str = "N/A"
    best_share: str = "N/A"
    rejected_pct: str = "N/A"
    uptime: str = "N/A"
    last_update: float = field(default_factory=time.time)
    error: Optional[str] = None


class AvalonMinerAPI:
    """Handle communication with Avalon Miner API"""

    def __init__(self, ip: str, port: int = 4028, timeout: int = 3):
        self.ip = ip
        self.port = port
        self.timeout = timeout

    def send_command(self, command: str, params: str = '') -> Optional[Dict[str, Any]]:
        """Send a command to the miner API"""
        if params:
            json_cmd = json.dumps({
                "command": command,
                "parameter": params
            }, separators=(',', ':'))
        else:
            json_cmd = json.dumps({
                "command": command
            }, separators=(',', ':'))

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.ip, self.port))
            sock.sendall(json_cmd.encode('utf-8'))
            time.sleep(0.05)  # Shorter delay for fleet monitoring

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

            # Parse JSON response (strip null bytes and whitespace)
            response_str = response.decode('utf-8').rstrip('\x00').strip()
            return json.loads(response_str)

        except (socket.timeout, socket.error, json.JSONDecodeError, Exception):
            return None


class FleetMonitor:
    """Monitor multiple miners and display status table"""

    def __init__(self, miner_ips: List[str], interval: int = 10, port: int = 4028):
        self.miner_ips = miner_ips
        self.interval = interval
        self.port = port
        self.miner_data: Dict[str, MinerStatus] = {}
        self.data_lock = Lock()
        self.running = True

    def format_hashrate(self, mhs: float, from_mhs: bool = True) -> str:
        """Format hash rate in TH/s"""
        try:
            if from_mhs:
                ths = mhs / 1_000_000
            else:
                ths = mhs / 1_000
            return f"{ths:.2f}"
        except (ValueError, TypeError):
            return "N/A"

    def format_difficulty(self, diff: float) -> str:
        """Format difficulty with appropriate unit"""
        try:
            diff = float(diff)
            if diff >= 1e15:
                return f"{diff / 1e15:.2f}P"
            elif diff >= 1e12:
                return f"{diff / 1e12:.2f}T"
            elif diff >= 1e9:
                return f"{diff / 1e9:.2f}G"
            elif diff >= 1e6:
                return f"{diff / 1e6:.2f}M"
            elif diff >= 1e3:
                return f"{diff / 1e3:.2f}K"
            else:
                return f"{diff:.0f}"
        except (ValueError, TypeError):
            return "N/A"

    def format_uptime(self, seconds: int) -> str:
        """Format uptime in human-readable format"""
        try:
            seconds = int(seconds)
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            minutes = (seconds % 3600) // 60
            if days > 0:
                return f"{days}d{hours:02d}h"
            elif hours > 0:
                return f"{hours}h{minutes:02d}m"
            else:
                return f"{minutes}m"
        except (ValueError, TypeError):
            return "N/A"

    def parse_custom_data(self, estats_response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse custom Avalon data from estats response"""
        custom_data = {}

        if 'STATS' not in estats_response:
            return custom_data

        # Try different patterns for custom data
        custom_data_raw = None

        # Pattern 1: Avalon Nano 3S
        for stat in estats_response.get('STATS', []):
            if 'MM ID0' in stat and stat['MM ID0']:
                custom_data_raw = stat['MM ID0']
                break

        # Pattern 2: Avalon Q
        if not custom_data_raw and 'MM ID0:Summary' in estats_response.get('STATS', {}):
            custom_data_raw = estats_response['STATS'].get('MM ID0:Summary', '')
            custom_data_raw = re.sub(r'(\w+):\[([^\]]+)\]', r'\1[\2]', custom_data_raw)

        if custom_data_raw:
            matches = re.findall(r'(\w+)\[([^\]]+)\]', custom_data_raw)
            for key, value in matches:
                # Try to convert to appropriate type
                try:
                    if '.' in value:
                        custom_data[key] = float(value)
                    else:
                        custom_data[key] = int(value)
                except ValueError:
                    custom_data[key] = value

        return custom_data

    def fetch_miner_status(self, ip: str) -> MinerStatus:
        """Fetch status for a single miner"""
        status = MinerStatus(ip=ip)

        try:
            api = AvalonMinerAPI(ip, self.port, timeout=3)

            # Fetch version
            version_response = api.send_command('version')
            if version_response and 'VERSION' in version_response:
                ver = version_response['VERSION'][0] if version_response['VERSION'] else {}
                status.model = ver.get('MODEL', 'N/A')

            # Fetch estats for custom data
            estats_response = api.send_command('estats')
            custom_data = {}
            if estats_response:
                custom_data = self.parse_custom_data(estats_response)

                # Extract data from custom fields
                if 'SoftOFF' in custom_data:
                    status.status = 'StandBy' if custom_data['SoftOFF'] > 0 else 'Active'
                else:
                    status.status = 'Active'

                if 'WORKMODE' in custom_data:
                    mode_map = {0: 'Eco', 1: 'Standard', 2: 'Super'}
                    status.work_mode = mode_map.get(custom_data['WORKMODE'], 'N/A')

                if 'MPO' in custom_data:
                    status.power = f"{custom_data['MPO']}W"

                if 'GHSspd' in custom_data:
                    status.hashrate_current = self.format_hashrate(custom_data['GHSspd'], from_mhs=False)

                if 'GHSavg' in custom_data:
                    status.hashrate_average = self.format_hashrate(custom_data['GHSavg'], from_mhs=False)

                if 'TMax' in custom_data:
                    status.temp_asic = f"{custom_data['TMax']}°C"
                elif 'TAvg' in custom_data:
                    status.temp_asic = f"{custom_data['TAvg']}°C"

                if 'Elapsed' in custom_data:
                    status.uptime = self.format_uptime(custom_data['Elapsed'])

            # Fetch summary for additional stats
            summary_response = api.send_command('summary')
            if summary_response and 'SUMMARY' in summary_response:
                summary_list = summary_response['SUMMARY']
                summary = summary_list[0] if isinstance(summary_list, list) and len(summary_list) > 0 else {}

                # Fallback hash rates if not in custom data
                if status.hashrate_average == "N/A" and 'MHS av' in summary:
                    status.hashrate_average = self.format_hashrate(summary['MHS av'], from_mhs=True)

                if status.hashrate_current == "N/A" and 'MHS 5s' in summary:
                    status.hashrate_current = self.format_hashrate(summary['MHS 5s'], from_mhs=True)

                if 'Pool Rejected%' in summary:
                    status.rejected_pct = f"{summary['Pool Rejected%']:.2f}%"

            # Fetch LCD for pool info
            lcd_response = api.send_command('lcd')
            if lcd_response and 'LCD' in lcd_response:
                lcd_list = lcd_response['LCD']
                lcd = lcd_list[0] if isinstance(lcd_list, list) and len(lcd_list) > 0 else {}

                pool_url = lcd.get('Current Pool', 'N/A')
                # Shorten pool URL for display
                if pool_url != 'N/A':
                    # Extract domain from URL
                    match = re.search(r'://([^:]+)', pool_url)
                    if match:
                        status.active_pool = match.group(1)[:20]  # Limit length
                    else:
                        status.active_pool = pool_url[:20]

                if 'Last Share Difficulty' in lcd:
                    status.last_share_diff = self.format_difficulty(lcd['Last Share Difficulty'])

                if 'Best Share' in lcd:
                    status.best_share = self.format_difficulty(lcd['Best Share'])

            status.last_update = time.time()
            status.error = None

        except Exception as e:
            status.status = "Error"
            status.error = str(e)[:30]

        return status

    def update_miner(self, ip: str, queue: Queue):
        """Worker thread to update a single miner"""
        status = self.fetch_miner_status(ip)
        queue.put((ip, status))

    def update_all_miners(self):
        """Update status for all miners using threads"""
        queue = Queue()
        threads = []

        # Start a thread for each miner
        for ip in self.miner_ips:
            thread = Thread(target=self.update_miner, args=(ip, queue))
            thread.daemon = True
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete (with timeout)
        for thread in threads:
            thread.join(timeout=5)

        # Collect results from queue
        while not queue.empty():
            ip, status = queue.get()
            with self.data_lock:
                self.miner_data[ip] = status

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')

    def draw_table(self):
        """Draw the status table"""
        self.clear_screen()

        # Header
        print("=" * 165)
        print("AVALON FLEET MONITOR")
        print("=" * 165)
        print(f"Monitoring {len(self.miner_ips)} miners | Refresh interval: {self.interval}s | Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 165)

        # Table header
        header = (
            f"{'IP Address':<15} "
            f"{'Model':<8} "
            f"{'Status':<8} "
            f"{'Mode':<8} "
            f"{'Power':<6} "
            f"{'HR Cur':<7} "
            f"{'HR Avg':<7} "
            f"{'Temp':<6} "
            f"{'Pool':<20} "
            f"{'Last':<8} "
            f"{'Best':<8} "
            f"{'Rej%':<7} "
            f"{'Uptime':<8}"
        )
        print(header)
        print("-" * 165)

        # Sort miners by IP
        sorted_ips = sorted(self.miner_ips, key=lambda x: [int(p) for p in x.split('.')])

        with self.data_lock:
            for ip in sorted_ips:
                if ip in self.miner_data:
                    m = self.miner_data[ip]

                    # Color coding based on status
                    status_color = ""
                    reset_color = ""

                    if m.status == "Active":
                        status_color = "\033[92m"  # Green
                        reset_color = "\033[0m"
                    elif m.status == "StandBy":
                        status_color = "\033[93m"  # Yellow
                        reset_color = "\033[0m"
                    elif m.status == "Error":
                        status_color = "\033[91m"  # Red
                        reset_color = "\033[0m"

                    row = (
                        f"{m.ip:<15} "
                        f"{m.model:<8} "
                        f"{status_color}{m.status:<8}{reset_color} "
                        f"{m.work_mode:<8} "
                        f"{m.power:<6} "
                        f"{m.hashrate_current:<7} "
                        f"{m.hashrate_average:<7} "
                        f"{m.temp_asic:<6} "
                        f"{m.active_pool:<20} "
                        f"{m.last_share_diff:<8} "
                        f"{m.best_share:<8} "
                        f"{m.rejected_pct:<7} "
                        f"{m.uptime:<8}"
                    )
                    print(row)

                    # Show error if present
                    if m.error:
                        print(f"  └─ Error: {m.error}")
                else:
                    # Miner not yet scanned
                    row = (
                        f"{ip:<15} "
                        f"{'...':<8} "
                        f"{'Scanning':<8} "
                        f"{'...':<8} "
                        f"{'...':<6} "
                        f"{'...':<7} "
                        f"{'...':<7} "
                        f"{'...':<6} "
                        f"{'...':<20} "
                        f"{'...':<8} "
                        f"{'...':<8} "
                        f"{'...':<7} "
                        f"{'...':<8}"
                    )
                    print(row)

        print("=" * 165)

        # Summary stats
        with self.data_lock:
            total_miners = len(self.miner_ips)
            active_miners = sum(1 for m in self.miner_data.values() if m.status == "Active")
            standby_miners = sum(1 for m in self.miner_data.values() if m.status == "StandBy")
            error_miners = sum(1 for m in self.miner_data.values() if m.status == "Error")

            # Calculate total hashrate
            total_hashrate = 0.0
            for m in self.miner_data.values():
                if m.hashrate_average != "N/A":
                    try:
                        total_hashrate += float(m.hashrate_average)
                    except ValueError:
                        pass

            print(f"Total: {total_miners} | Active: \033[92m{active_miners}\033[0m | "
                  f"StandBy: \033[93m{standby_miners}\033[0m | "
                  f"Error: \033[91m{error_miners}\033[0m | "
                  f"Fleet Hash Rate: \033[96m{total_hashrate:.2f} TH/s\033[0m")

        print("\nPress Ctrl+C to exit")

    def run(self):
        """Main monitoring loop"""
        print("Starting Avalon Fleet Monitor...")
        print(f"Monitoring {len(self.miner_ips)} miners with {self.interval}s refresh interval")
        time.sleep(1)

        try:
            while self.running:
                self.update_all_miners()
                self.draw_table()
                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\n\nShutting down Fleet Monitor...")
            self.running = False


def load_config_file(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to load configuration file: {e}")
        sys.exit(1)


def validate_ip(ip: str) -> bool:
    """Validate IP address"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def parse_ip_range(ip_range: str) -> List[str]:
    """Parse IP range like 192.168.1.100-110 into list of IPs"""
    ips = []

    # Check if it's a range
    match = re.match(r'^(\d+\.\d+\.\d+\.)(\d+)-(\d+)$', ip_range)
    if match:
        prefix = match.group(1)
        start = int(match.group(2))
        end = int(match.group(3))

        for i in range(start, end + 1):
            ips.append(f"{prefix}{i}")
    else:
        # Single IP
        if validate_ip(ip_range):
            ips.append(ip_range)

    return ips


def main():
    parser = argparse.ArgumentParser(
        description='Avalon Fleet Monitor - Real-time monitoring for multiple Avalon miners',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Monitor miners from command line
  %(prog)s --ips 192.168.1.100 192.168.1.101 192.168.1.102

  # Monitor with IP range
  %(prog)s --ips 192.168.1.100-110

  # Monitor from config file
  %(prog)s --config fleet.json

  # Custom refresh interval (30 seconds)
  %(prog)s --config fleet.json --interval 30

Config file format (fleet.json):
  {
    "miners": [
      "192.168.1.100",
      "192.168.1.101",
      "192.168.1.102"
    ],
    "interval": 10,
    "port": 4028
  }

Or with IP ranges:
  {
    "miners": ["192.168.1.100-110"],
    "interval": 15
  }
        """
    )

    parser.add_argument('--ips', nargs='+', metavar='IP',
                       help='IP addresses of miners (can use ranges like 192.168.1.100-110)')
    parser.add_argument('--config', '-c', metavar='FILE',
                       help='Load configuration from JSON file')
    parser.add_argument('--interval', '-i', type=int, metavar='SECONDS',
                       help='Refresh interval in seconds (default: 10)')
    parser.add_argument('--port', '-p', type=int, default=4028, metavar='PORT',
                       help='API port (default: 4028)')

    args = parser.parse_args()

    # Determine configuration source
    miner_ips = []
    interval = 10
    port = 4028

    if args.config:
        # Load from config file
        config = load_config_file(args.config)

        # Parse miners (can be list of IPs or ranges)
        if 'miners' in config:
            for entry in config['miners']:
                miner_ips.extend(parse_ip_range(entry))
        else:
            print("Error: Configuration file must contain 'miners' array")
            sys.exit(1)

        # Get interval from config or override with command line
        if args.interval:
            interval = args.interval
        elif 'interval' in config:
            interval = config['interval']

        # Get port from config
        if 'port' in config:
            port = config['port']

    elif args.ips:
        # Load from command line
        for entry in args.ips:
            miner_ips.extend(parse_ip_range(entry))

        if args.interval:
            interval = args.interval

    else:
        print("Error: Must specify either --ips or --config")
        parser.print_help()
        sys.exit(1)

    # Override port if specified on command line
    if args.port != 4028:
        port = args.port

    # Validate we have miners
    if not miner_ips:
        print("Error: No valid miner IP addresses specified")
        sys.exit(1)

    # Remove duplicates and validate IPs
    miner_ips = list(set(miner_ips))
    invalid_ips = [ip for ip in miner_ips if not validate_ip(ip)]

    if invalid_ips:
        print(f"Error: Invalid IP addresses: {', '.join(invalid_ips)}")
        sys.exit(1)

    # Validate interval
    if interval < 1:
        print("Error: Interval must be at least 1 second")
        sys.exit(1)

    # Start monitoring
    monitor = FleetMonitor(miner_ips, interval, port)
    monitor.run()


if __name__ == '__main__':
    main()
