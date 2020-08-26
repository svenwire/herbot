import discord
import os
import datetime
import mysql.connector
from datetime import datetime
from random import randint

class Herbot(discord.Client):
    
    def __init__(self):
        super().__init__()
        self.__db = self.__setup_db()
        self.__cursor = self.__db.cursor(buffered=True)
        

    async def on_ready(self):
        print("[HERBOT] started.")

    async def on_message(self, message):
        if message.author == self.user:
            return

        # create user if not exist
        if not self.__user_exists(message.author.display_name):
            self.__cursor.execute(f"INSERT INTO users (display_name) VALUES ('{message.author.display_name}')")
            self.__db.commit()
        
        args = message.content.split(" ", 2)
        command = args[0].lower()

        # check for text command and get it's message if exists
        self.__cursor.execute(f"SELECT * FROM commands WHERE command ='{command}'")
        result = self.__cursor.fetchall()
        if result and result[0][1] == command:
            await message.channel.send(result[0][2])

        # check for other commands
        if len(args) == 1:
            self.__check_next_date()

            if command == "!schwanz":
                if not self.__already_typed_schwanz(message.author.display_name, "schwanz"):
                    laenge = randint(0, 100)
                    await message.channel.send(f"{message.author.display_name} hat einen {laenge}cm Schwanz.")
                    self.__cursor.execute(f"UPDATE users SET schwanz = {laenge} WHERE display_name = '{message.author.display_name}'")
                    self.__db.commit()
                    self.__process_highscore(message.author.display_name)
                else:
                    laenge = self.__get_user_value(message.author.display_name, "schwanz")
                    await message.channel.send(f"{message.author.display_name} hatte heute einen {laenge}cm Schwanz.")
            elif command == "!yarak":
                if not self.__already_typed_schwanz(message.author.display_name, "yarak"):
                    laenge = randint(0, 100)
                    await message.channel.send(f"{message.author.display_name} hat einen {laenge}cm Yarak.")
                    self.__cursor.execute(f"UPDATE users SET yarak = {laenge} WHERE display_name = '{message.author.display_name}'")
                    self.__db.commit()
                    self.__process_highscore(message.author.display_name)
                else:
                    laenge = self.__get_user_value(message.author.display_name, "yarak")
                    await message.channel.send(f"{message.author.display_name} hatte heute einen {laenge}cm Yarak.")
            elif command == "!subschwanz":
                if not self.__already_typed_schwanz(message.author.display_name, "subschwanz"):
                    laenge = randint(0, 200)
                    await message.channel.send(f"{message.author.display_name} hat einen {laenge}cm Subschwanz.")
                    self.__cursor.execute(f"UPDATE users SET subschwanz = {laenge} WHERE display_name = '{message.author.display_name}'")
                    self.__db.commit()
                    self.__process_highscore(message.author.display_name)
                else:
                    laenge = self.__get_user_value(message.author.display_name, "subschwanz")
                    await message.channel.send(f"{message.author.display_name} hatte heute einen {laenge}cm Subschwanz.")
            elif command == "!schwanzinfo":
                embed = discord.Embed(title=f"{message.author.display_name} Schwanzinfo")
                embed.add_field(name="Typ", value="Schwanz\nYarak\nSubschwanz\nInsgesamt")
                schwaenze = [self.__get_user_value(message.author.display_name, "schwanz"), self.__get_user_value(message.author.display_name, "yarak"), self.__get_user_value(message.author.display_name, "subschwanz")]
                insgesamt = 0
                for i in range(len(schwaenze)):
                    if schwaenze[i] == None:
                        schwaenze[i] == "- "
                    else:
                        insgesamt += schwaenze[i]
                highscore = self.__get_user_value(message.author.display_name, "highscore")
                if highscore == None: highscore = "- "
                
                embed.add_field(name="Länge", value=f"{schwaenze[0]}cm\n{schwaenze[1]}cm\n{schwaenze[2]}cm\n{insgesamt}cm")
                embed.add_field(name="Highscore", value=f"{highscore}cm", inline=False)
                await message.channel.send(embed=embed)
            elif command == "!bestenliste":
                ranks = ""
                users = ""
                laengen = ""
                bl = self.__get_bestenliste()
                for i in range(len(bl)):
                    ranks += f"#{i+1}\n"
                    users += f"{bl[i][0]}\n"
                    laengen += f"{bl[i][4]}cm\n"
                
                embed = discord.Embed(title=f"Bestenliste (Top 10)")
                embed.add_field(name="Rank", value=ranks)
                embed.add_field(name="User", value=users)
                embed.add_field(name="Länge", value=laengen)
                await message.channel.send(embed=embed)
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
        if result and result[0][0] == command: return True
        else: return False

    def __check_next_date(self):
        self.__cursor.execute(f"SELECT * FROM settings WHERE name = 'next_date'")
        result = self.__cursor.fetchall()
        if result:
            next_date = datetime.strptime(result[0][1], '%Y-%m-%d').date()
            if datetime.today().date() > next_date:
                self.__cursor.execute("UPDATE users SET schwanz = NULL, yarak = NULL, subschwanz = NULL")
                self.__db.commit()
        else:
            next_date = str(datetime.today().date().replace(day=datetime.today().day+1))
            self.__cursor.execute("INSERT INTO settings (name, val) VALUES (%s, %s)", ("next_date", next_date))
            self.__db.commit()

    def __already_typed_schwanz(self, display_name, schwanz_type):
        self.__cursor.execute(f"SELECT {schwanz_type} FROM users WHERE display_name = '{display_name}'")
        result = self.__cursor.fetchone()
        if result[0] != None:
            return True
        else:
            return False

    def __get_bestenliste(self):
        self.__cursor.execute("SELECT * FROM users ORDER BY highscore DESC")
        result = self.__cursor.fetchall()
        for x in result:
            if x[4] == None:
                result.remove(x)
        return result[:10]

    def __get_user_value(self, display_name, column):
        self.__cursor.execute(f"SELECT {column} FROM users WHERE display_name = '{display_name}'")
        result = self.__cursor.fetchone()
        return result[0]

    def __user_exists(self, display_name):
        self.__cursor.execute(f"SELECT * FROM users WHERE display_name = '{display_name}'")
        result = self.__cursor.fetchone()
        if result: return True
        else: return False

    def __process_highscore(self, display_name):
        self.__cursor.execute(f"SELECT * FROM users WHERE display_name = '{display_name}'")
        result = self.__cursor.fetchone()
        if result[1] != None and result[2] != None and result[3] != None:
            sum = result[1] + result[2] + result[3]
            if result[4] != None:
                if result[4] < sum:
                    self.__cursor.execute(f"UPDATE users SET highscore = {sum} WHERE display_name = '{display_name}'")
                    self.__db.commit()
            else:
                self.__cursor.execute(f"UPDATE users SET highscore = {sum} WHERE display_name = '{display_name}'")
                self.__db.commit()

    def __setup_db(self):
        db = mysql.connector.connect(host=os.getenv('MYSQL_HOST'), user=os.getenv('MYSQL_USER'), password=os.getenv('MYSQL_PASSWORD'))
        db.cursor().execute("CREATE DATABASE IF NOT EXISTS herbot")
        db.cursor().execute("USE herbot")
        db.cursor().execute("CREATE TABLE IF NOT EXISTS commands (command VARCHAR(32) PRIMARY KEY, text VARCHAR(1024))")
        db.cursor().execute("CREATE TABLE IF NOT EXISTS users (display_name VARCHAR(64) PRIMARY KEY, schwanz TINYINT(3) UNSIGNED DEFAULT NULL, yarak TINYINT(3) UNSIGNED DEFAULT NULL, subschwanz TINYINT(3) UNSIGNED DEFAULT NULL, highscore SMALLINT(3) UNSIGNED DEFAULT NULL)")
        db.cursor().execute("CREATE TABLE IF NOT EXISTS settings (name VARCHAR(32) PRIMARY KEY, val VARCHAR(512))")
        return db