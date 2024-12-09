import os
import asyncio
from aiohttp import web
from pyrogram import idle
from server import web_server
from tgServices import BotClient
from datetime import datetime
import json
import variables as var
import time
from utils2.database import Database

# Constants for cleanup
TEMP_DIR = "temp"
CLEANUP_INTERVAL = 500

os.makedirs(TEMP_DIR, exist_ok=True)
db = Database()
# Log file path
LOG_FILE = "log.txt"


def write_log(message):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"Logging failed: {e}")


async def cleanup_temp_files():
    try:
        """Periodically delete temporary files older than 5 minutes."""
        while True:
            try:
                now = time.time()
                # delete database messages

                db.delete_all_messages()

                for file_name in os.listdir(TEMP_DIR):
                    file_path = os.path.join(TEMP_DIR, file_name)
                    if file_name.endswith(".json"):
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            timestamp = data.get("_timestamp", now)
                        # Delete files older than 5 minutes
                        if now - timestamp > CLEANUP_INTERVAL:
                            os.remove(file_path)
                            write_log(f"Deleted expired file: {file_name}")
                await asyncio.sleep(CLEANUP_INTERVAL)
            except Exception as e:
                write_log(f"Error during cleanup: {e}")
    except Exception as e:
        write_log(f"Unexpected error in cleanup_temp_files: {e}")


async def main():
    try:
        await BotClient.start()

        app = web.AppRunner(await web_server())
        await app.setup()

        bind_address = var.BIND_ADDRESS
        bind_port = int(os.getenv("PORT", 8001))
        await web.TCPSite(app, bind_address, bind_port).start()

        write_log("--------Bot Started----------------")

        await asyncio.gather(
            cleanup_temp_files(),
            idle(),
        )
    except Exception as error:
        write_log(f"Error in main: {error}")


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        write_log("Bot stopped by KeyboardInterrupt.")
        BotClient.stop()
    except Exception as error:
        write_log(f"Unhandled exception: {error}")
