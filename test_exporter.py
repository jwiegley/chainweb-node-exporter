#!/usr/bin/env python3
"""
Test script for the Kadena exporter.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kadena_exporter import KadenaExporter

def test_fetch_cut_height():
    """Test fetching the cut height from the API."""
    exporter = KadenaExporter('https://api.chainweb.com/chainweb/0.0/mainnet01/cut')
    height = exporter.fetch_cut_height()

    if height is not None:
        print(f"✓ Successfully fetched cut height: {height}")
        print(f"✓ Height is a valid number: {isinstance(height, (int, float))}")
        return True
    else:
        print("✗ Failed to fetch cut height")
        return False

if __name__ == '__main__':
    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    print("Testing Kadena Exporter...")
    if test_fetch_cut_height():
        print("\nAll tests passed! The exporter is working correctly.")
        print("\nYou can now run the exporter with:")
        print("  python3 kadena_exporter.py")
        print("\nMetrics will be available at:")
        print("  http://localhost:9100/metrics")
    else:
        print("\nTests failed. Please check the error messages above.")
        sys.exit(1)