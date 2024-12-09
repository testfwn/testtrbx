from pyrogram import Client
import variables as var

# Initialize logger

BotClient = Client(
    name=var.package + str(var.version),
    api_id=var.API_ID,
    api_hash=var.API_HASH,
    bot_token=var.BOT_TOKEN,
    plugins={"root": "tgServices/plugins"},
)
