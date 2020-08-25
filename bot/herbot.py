import discord
import os
import datetime
import mysql.connector

class Herbot(discord.Client):
    
    def __init__(self):
        super().__init__()
        self.__db = self.__setup_db()
        self.__cursor = self.__db.cursor(buffered=True)
        

    async def on_ready(self):
        print("Moin Leute, Trymacs hier!")

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        args = message.content.split(" ", 2)
        command = args[0].lower()

        # check for text command and get it's message if exists
        self.__cursor.execute(f"SELECT * FROM commands WHERE command ='{command}'")
        result = self.__cursor.fetchall()
        if result and result[0][1] == command:
            await message.channel.send(result[0][2])

        # check for other commands
        if len(args) == 1:
            pass
        elif len(args) == 2:
            if command == "!delcom":
                if self.__is_text_command(args[1]):
                    self.__cursor.execute(f"DELETE FROM commands WHERE command = '{args[1]}'")
                    self.__db.commit()
                    await message.channel.send(f"Der Command \"{args[1]}\" wurde gelöscht.")
                else:
                    await message.channel.send(f"Den Command \"{args[1]}\" gibt es nicht.")
        elif len(args) == 3:
            if command == "!addcom":
                if not self.__is_text_command(args[1]):
                    self.__cursor.execute("INSERT INTO commands (command, text) VALUES (%s, %s)", (args[1], args[2]))
                    self.__db.commit()
                    await message.channel.send(f"Der Command \"{args[1]}\" wurde hinzugefügt.")
                else:
                    await message.channel.send(f"Den Command \"{args[1]}\" gibt es schon.")
            elif command == "!editcom":
                if self.__is_text_command(args[1]):
                    self.__cursor.execute(f"UPDATE commands SET text = '{args[2]}' WHERE command = '{args[1]}'")
                    self.__db.commit()
                    await message.channel.send(f"Der Command \"{args[1]}\" wurde bearbeitet.")
                else:
                    await message.channel.send(f"Den Command \"{args[1]}\" gibt es nicht.")

    def __is_text_command(self, command):
        self.__cursor.execute(f"SELECT * FROM commands WHERE command ='{command}'")
        result = self.__cursor.fetchall()
        if result and result[0][1] == command: return True
        else: return False

    def __setup_db(self):
        db = mysql.connector.connect(host=os.getenv('MYSQL_HOST'), user=os.getenv('MYSQL_USER'), password=os.getenv('MYSQL_PASSWORD'))
        db.cursor().execute("CREATE DATABASE IF NOT EXISTS herbot")
        db.cursor().execute("USE herbot")
        db.cursor().execute("CREATE TABLE IF NOT EXISTS commands (id INT AUTO_INCREMENT PRIMARY KEY, command VARCHAR(32), text VARCHAR(1024))")
        db.cursor().execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, display_name VARCHAR(64), schwanz TINYINT(3) UNSIGNED, yarak TINYINT(3) UNSIGNED, subschwanz TINYINT(3) UNSIGNED, highscore SMALLINT(3) UNSIGNED)")
        db.cursor().execute("CREATE TABLE IF NOT EXISTS settings (last_date DATE)")
        return db