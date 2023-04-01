"""
Simple utility to monitor current CPU,Network,RAM usage.

Author:  ChatGpt
"""


from . import logger

import asyncio
import psutil

from threading import Thread

async def monitor_network():
    elapsed_time = 60

    while True:
        # Wait for 60 seconds
        await asyncio.sleep(elapsed_time)

        # Get the current network counters
        net_io_counters = psutil.net_io_counters()

        # Calculate the upload and download speeds in bytes/sec
          # seconds
        upload_speed = (net_io_counters.bytes_sent - monitor_network.bytes_sent) / elapsed_time
        download_speed = (net_io_counters.bytes_recv - monitor_network.bytes_recv) / elapsed_time


        # Convert the speeds to human-readable format
        upload_speed = f"{upload_speed/1024:.2f} KB/s"
        download_speed = f"{download_speed/1024:.2f} KB/s"

        logger.log(f"CPU: {psutil.cpu_percent()}% RAM: {psutil.virtual_memory().percent}% Upload: {upload_speed} Download: {download_speed}")

        # Update the counters
        monitor_network.bytes_sent = net_io_counters.bytes_sent
        monitor_network.bytes_recv = net_io_counters.bytes_recv

async def reset_counters():
    while True:
        # Wait for 2+2 minutes
        await asyncio.sleep(120 + 120)

        # Reset the network counters for each network interface separately
        psutil.net_io_counters(pernic=True)

def main():
    # Initialize the counters
    net_io_counters = psutil.net_io_counters()
    monitor_network.bytes_sent = net_io_counters.bytes_sent
    monitor_network.bytes_recv = net_io_counters.bytes_recv

    # Start the network monitoring and counter resetting coroutines
    loop = asyncio.new_event_loop()

    # Start the event loop in a separate thread
    t = Thread(target=loop.run_forever)
    t.start()

    # Schedule the coroutines in the event loop
    asyncio.run_coroutine_threadsafe(monitor_network(), loop=loop)
    asyncio.run_coroutine_threadsafe(reset_counters(), loop=loop)

