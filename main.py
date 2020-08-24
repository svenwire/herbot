import os
from dotenv import load_dotenv
from bot.herbot import Herbot
import mysql.connector

def main():
    load_dotenv()
    db = mysql.connector.connect(host=os.getenv('MYSQL_HOST'), user=os.getenv('MYSQL_USER'), password=os.getenv('MYSQL_PASSWORD'))
    client = Herbot(db)
    client.run(os.getenv('BOT_TOKEN'))

if __name__ == "__main__":
    main()

