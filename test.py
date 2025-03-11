import os
from dotenv import load_dotenv
from ConnectingToAirtable import connecting


load_dotenv()
connecting(os.getenv("AIRTABLE_TOKEN"), os.getenv("APP_AIRTABLE_TOKEN"))