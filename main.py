import os
from dotenv import load_dotenv
from bot.herbot import Herbot

def main():
    load_dotenv()
    client = Herbot()
    client.run(os.getenv('BOT_TOKEN'))

if __name__ == "__main__":
    main()

