from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import json
from datetime import datetime
import pytz

# from variables import MONGO_DB_URL, DATABASE_NAME, MESSAGE_QUEUE
MONGO_DB_URL = "mongodb+srv://civewe7923:Test12345@cluster0.xj3wy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "teraboxdwnfree_bot"
MESSAGE_QUEUE = "message_queue"
USERS = "users"

LOG_FILE = "log.txt"


def write_log(message):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        write_log(f"Logging failed: {e}")


class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        self.client = MongoClient(MONGO_DB_URL)
        self.db = self.client[DATABASE_NAME]
        self.messageQueue = self.db[MESSAGE_QUEUE]
        self.users = self.db[USERS]

        self.ping()

    def ping(self):
        self.client.admin.command("ping")
        write_log("Connected to Atlas instance!")

    def store_user(self, userId):

        try:
            if self.users.find_one({"_id": userId}):
                return True

            ist = pytz.timezone("Asia/Kolkata")
            current_time = datetime.now(ist)

            self.users.insert_one({"_id": userId, "added_at": current_time})
            return False
        except Exception as e:
            write_log(f"Error storing user: {e}")
            return True

    def store_message(self, messageId, messageData):
        """
        Store a message in the queue.
        :param messageId: Unique identifier of the message
        :param messageData: Content of the message
        :return: Boolean indicating success or failure
        """
        try:
            serialized_data = json.loads(messageData)

            self.messageQueue.insert_one(
                {"_id": messageId, "messageData": serialized_data}
            )
            return True
        except DuplicateKeyError:
            return True
        except Exception as e:
            write_log(f"Error storing message: {e}")
            return False

    def store_messagev2(self, messageId, randomNum):
        try:

            self.messageQueue.insert_one({"_id": messageId, "random": randomNum})
            return True
        except DuplicateKeyError:
            return True
        except Exception as e:
            write_log(f"Error storing messagev2: {e}")
            return False

    def get_message(self):
        """
        Retrieve and remove the oldest message from the queue.
        :return: The message document or None if the queue is empty
        """
        try:
            message = self.messageQueue.find_one_and_delete({})
            return message
        except Exception as e:
            write_log(f"Error retrieving message: {e}")
            return None

    def delete_all_messages(self):
        try:
            last_10_docs = self.messageQueue.find().sort("_id", -1).limit(10)

            last_10_ids = [doc["_id"] for doc in last_10_docs]

            if last_10_ids:
                self.messageQueue.delete_many({"_id": {"$nin": last_10_ids}})
                write_log(
                    f"Deleted all documents except the last 10 with IDs: {last_10_ids}"
                )
            else:
                write_log("No documents found to delete.")

        except Exception as e:
            write_log(f"Error during deletion: {e}")

    def delete_message(self, messageId):
        try:
            message = self.messageQueue.find_one_and_delete({"_id": messageId})

            if message:
                return message
            else:
                return False
        except Exception as e:
            write_log(f"Error retrieving and deleting message: {e}")
            return False

    def get_messagev2(self, messageId):
        try:
            message = self.messageQueue.find_one({"_id": messageId})

            if message:
                return message["random"]
            else:
                return False
        except Exception as e:
            write_log(f"Error retrieving and deleting message: {e}")
            return False

    def updateConfig(self, data):
        try:
            self.config_collection.update_one(
                {"_id": self.config_docid}, {"$set": data}
            )
            return True
        except Exception as e:
            write_log(f"Error updating config: {e}")
            return False


# db = Database()

# # Store a message
# message_stored = db.store_message("msg_001", "user_123", {"text": "Hello, world!"})
# write_log("Message stored:", message_stored)

# Get a message
# message = db.get_message()
# if message:
#     write_log("Retrieved message:", message)
# else:
#     write_log("No messages in the queue.")
