import time, asyncio, random, json, os, re, random, time
from datetime import datetime, timedelta
from tgServices import BotClient
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from pyrogram import filters, enums
from utils import genKeys, getFilesList2, streamData
from utils2.database import Database
import variables

TEMP_DIR = "temp"

os.makedirs(TEMP_DIR, exist_ok=True)

LOG_FILE = "log.txt"

db = Database()


# Define a logging function
def write_log(message):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        # If logging fails, we might want to print to stdout as a fallback
        print(f"Logging failed: {e}")


def parseLink(link):
    try:
        if "/s/" in link:
            link = link.split("/s/")[1]
        elif "?surl=" in link:
            link = link.split("?surl=")[1]

        if link.startswith("1"):
            link = link[1:]
    except:
        pass
    finally:
        return link


def save_to_temp(file_id, data):
    """Save data to a temporary JSON file with a timestamp."""
    temp_path = os.path.join(TEMP_DIR, f"{file_id}.json")
    data["_timestamp"] = time.time()  # Add the current time as a timestamp
    with open(temp_path, "w") as f:
        json.dump(data, f)


def load_from_temp(file_id):
    """Load data from a temporary JSON file."""
    temp_path = os.path.join(TEMP_DIR, f"{file_id}.json")
    if not os.path.exists(temp_path):
        return None
    with open(temp_path, "r") as f:
        return json.load(f)


def delete_temp(file_id):
    """Delete the temporary JSON file."""
    temp_path = os.path.join(TEMP_DIR, f"{file_id}.json")
    if os.path.exists(temp_path):
        os.remove(temp_path)


def getPemission(messageId):
    try:
        # delay_ms = random.randint(1, 500) / 1000
        randomNum = random.randint(1000000, 999999999)
        stored = db.store_messagev2(messageId=messageId, randomNum=randomNum)
        # delay_ms = random.randint(1, 1000) / 1000
        # await asyncio.sleep(delay_ms)
        gotPermission = db.get_messagev2(messageId=messageId)
        if gotPermission == randomNum:
            return True
        else:
            return False

    except:
        return True


@BotClient.on_message(filters.command("alive"))
async def alive_command(_, message: Message):
    # stored = db.store_messagev2(messageId=message.id)
    # gotPermission = db.get_messagev2(messageId=message.id)
    # if not stored or not gotPermission:
    #     return

    await message.reply("<b>Bot is alive and running!</b>")


@BotClient.on_message(filters.command("start"))
async def on_start_msg(_, message: Message):
    # stored = db.store_messagev2(messageId=message.id)
    # delay_ms = random.randint(1, 1000) / 1000
    # await asyncio.sleep(delay_ms)
    # gotPermission = db.get_messagev2(messageId=message.id)
    if not getPemission(message.id):
        return

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Check bot is alive - /alive", callback_data="alive"
                )
            ],
        ]
    )
    caption = f"<b>Welcome {message.chat.first_name}!</b>\nI am Terabox Downloader, send any link to stream/download for free without any ads :) vm0"
    await message.reply(text=caption, reply_markup=buttons)

    if not db.store_user(message.chat.id):
        await BotClient.send_message(
            chat_id=variables.ADMIN_ID,
            text=f"New User : {message.chat.id} - {message.chat.first_name} {message.chat.last_name} @{message.chat.username}",
        )


@BotClient.on_callback_query(filters.regex("alive"))
async def alive_callback(_, callback_query):
    if not getPemission(callback_query.id):
        return

    await callback_query.answer("Bot is alive and running!")
    await callback_query.message.reply("Bot is alive and running!")


async def sendFile(file_id, message: Message):
    try:
        file_data = load_from_temp(file_id)
        if not file_data:
            await message.reply("File information not found.")
            return
        buttons = [
            [InlineKeyboardButton("Stream", callback_data=f"stream_{file_id}")],
        ]
        if "dlink" in file_data:
            buttons.append([InlineKeyboardButton("Download", url=file_data["dlink"])])
        await message.reply_photo(
            caption="Your file is ready.",
            photo=file_data["thumb"],
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    except:
        pass


@BotClient.on_callback_query()
async def handle_callback_query(client, callback_query: CallbackQuery):
    try:
        if not getPemission(callback_query.id):
            return

        await BotClient.send_chat_action(
            callback_query.message.chat.id, enums.ChatAction.TYPING
        )
        data = callback_query.data
        if data.startswith("folder_"):
            file_id = data.replace("folder_", "")
            file_data = load_from_temp(file_id)
            if not file_data:
                await callback_query.message.reply("Folder information not found.")
                return
            surl, folder_path = file_data["surl"], file_data["path"]
            await send_file_buttons(
                surl, callback_query.message, is_root=False, dir=folder_path
            )
            delete_temp(file_id)

        elif data.startswith("file_"):
            file_id = data.replace("file_", "")
            file_data = load_from_temp(file_id)
            if not file_data:
                await callback_query.message.reply("File information not found.")
                return

            buttons = [
                [InlineKeyboardButton("Stream", callback_data=f"stream_{file_id}")],
            ]
            if "dlink" in file_data:
                buttons.append(
                    [InlineKeyboardButton("Download", url=file_data["dlink"])]
                )

            await callback_query.message.reply_photo(
                caption="Your file is ready.",
                photo=file_data["thumb"],
                reply_markup=InlineKeyboardMarkup(buttons),
            )

        elif data.startswith("stream_"):
            file_id = data.replace("stream_", "")
            file_data = load_from_temp(file_id)
            if not file_data:
                await callback_query.message.reply("Stream information not found.")
                return

            text_data = streamData(
                uk=file_data["uk"], shareid=file_data["shareid"], fid=file_id
            )
            if not text_data:
                await callback_query.message.reply("Failed to generate stream data.")
                return
            await BotClient.send_chat_action(
                callback_query.message.chat.id, enums.ChatAction.CANCEL
            )
            await BotClient.send_chat_action(
                callback_query.message.chat.id, enums.ChatAction.UPLOAD_DOCUMENT
            )
            file_path = f"playlist_{random.randint(1, 100)}.m3u8"
            with open(file_path, "w") as f:
                f.write(text_data)

            await callback_query.message.reply_document(
                file_path,
                caption="Here is your stream file (best viewed with MX Player).",
            )
            os.remove(file_path)

        else:
            await callback_query.answer("Unknown action!")
    except Exception as e:
        print(f"Error: {e}")
        write_log(f"Error: {e}")

    finally:
        try:
            await BotClient.send_chat_action(
                callback_query.message.chat.id, enums.ChatAction.CANCEL
            )
        except:
            pass


async def send_file_buttons(surl, message: Message, is_root=True, dir=""):
    try:
        try:
            write_log(
                f"New Task from {message.chat.first_name}: {message.chat.username} - {surl}"
            )
        except:
            pass
        js_token = genKeys(surl)
        if not js_token:
            await message.reply("Failed to generate keys.")
            return

        files_list = getFilesList2(jsToken=js_token, surl=surl, isRoot=is_root, dir=dir)
        if not files_list:
            await message.reply("Invalid Link !")
            return

        buttons_list = [
            [InlineKeyboardButton("--- Files ---", callback_data="placeholder")]
        ]

        for file in files_list["list"]:
            file_id = file["fs_id"]
            if file["isdir"] == "1":
                save_to_temp(file_id, {"surl": surl, "path": file["path"]})
                buttons_list.append(
                    [
                        InlineKeyboardButton(
                            f"🗂: {file['server_filename']}",
                            callback_data=f"folder_{file_id}",
                        )
                    ]
                )
            else:
                file_data = {
                    "thumb": file["thumbs"]["url3"],
                    "shareid": files_list["share_id"],
                    "uk": files_list["uk"],
                }
                if file.get("dlink"):
                    file_data["dlink"] = file["dlink"]
                save_to_temp(file_id, file_data)
                file_size = round(int(file["size"]) / (1024 * 1024), 2)
                buttons_list.append(
                    [
                        InlineKeyboardButton(
                            f"{file['server_filename']} - {file_size} MB",
                            callback_data=f"file_{file_id}",
                        )
                    ]
                )
        if len(files_list["list"]) == 1 and files_list["list"][0]["isdir"] != "1":
            await sendFile(files_list["list"][0]["fs_id"], message)
        else:
            await message.reply(
                text=f"<b>Files for {surl}</b>",
                reply_markup=InlineKeyboardMarkup(buttons_list),
            )
    except Exception as e:
        print(f"Error: {e}")
        write_log(f"Error: {e}")

        await message.reply("An error occurred while processing the files.")


@BotClient.on_message(filters.text and filters.incoming)
async def handle_text_message(_, message: Message):
    try:
        if not getPemission(message.id):
            return

        text = message.text

        await BotClient.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        try:
            if len(message.caption) > 5:
                text = message.caption
        except:
            pass
        try:
            links = re.findall(r"https?://\S+", text)
            if len(links) > 1:
                for link in links:
                    link = parseLink(link)
                    await send_file_buttons(link, message)
                return

        except Exception as err:
            # print(f"error at mul {err}")
            pass
        surl = text.strip()
        if "/s/" in surl:
            surl = surl.split("/s/")[1]
        elif "?surl=" in surl:
            surl = surl.split("?surl=")[1]

        if surl.startswith("1"):
            surl = surl[1:]
        if not surl:
            await message.reply("Invalid link.")
            return

        print(f"Processing task: {surl}")

        await send_file_buttons(surl, message)
    except Exception as e:
        print(f"Error: {e}")
        write_log(f"Error: {e}")

        await message.reply(f"Failed to process the link: {str(e)}")
    finally:
        try:
            await BotClient.send_chat_action(message.chat.id, enums.ChatAction.CANCEL)
        except:
            pass
