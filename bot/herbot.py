import discord
from discord.ext import tasks
import os
import datetime
from datetime import datetime
from datetime import timedelta
from random import randint
import shlex
from .sql import SQL

class Herbot(discord.Client):
    
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.__sql = SQL(os.getenv("MYSQL_HOST"), os.getenv("MYSQL_USER"), os.getenv("MYSQL_PASSWORD"), os.getenv("MYSQL_DATABASE"))
        
    async def on_ready(self):
        self.count_time.start()
        print("[HERBOT] ist am start yo.")

    async def on_message(self, message):
        if not self.__sql.is_connected():
            self.__sql.reconnect()

        if message.author == self.user:
            return

        role_minimum = 6
        highest_role = 0
        for role in message.author.roles:
            if highest_role < role.position:
                highest_role = role.position
        
        if highest_role < role_minimum: return

        display_name = message.author.display_name
        color = discord.Color.gold()

        # create user if not exist
        if not self.__sql.user_exists(display_name):
            self.__sql.add_user(display_name)
        
        msg = shlex.split(message.content)
        command = msg[0]
        args = msg[1:]

        # check for text command and get it's message if exists
        if self.__sql.text_command_exists(command):
            text = self.__sql.get_value_where("text", "commands", ("command", command))
            await message.channel.send(text)

        # check for other commands
        self.__sql.check_next_date()

        if command == "!schwanz":
            if len(args) == 0:
                if not self.__sql.schwanz_on_cooldown(display_name, "schwanz"):
                    laenge = randint(0, 100)
                    await message.channel.send(f"{display_name} hat einen {laenge}cm Schwanz.")
                    self.__sql.update_schwanz_laenge(display_name, "schwanz", laenge)
                    self.__sql.process_highscore(display_name)
                else:
                    laenge = self.__sql.get_schwanz_laenge(display_name, "schwanz")
                    await message.channel.send(f"{display_name} hatte heute einen {laenge}cm Schwanz.")
        elif command == "!yarak":
            if len(args) == 0:
                if not self.__sql.schwanz_on_cooldown(display_name, "yarak"):
                    laenge = randint(0, 100)
                    await message.channel.send(f"{display_name} hat einen {laenge}cm Yarak.")
                    self.__sql.update_schwanz_laenge(display_name, "yarak", laenge)
                    self.__sql.process_highscore(display_name)
                else:
                    laenge = self.__sql.get_schwanz_laenge(display_name, "yarak")
                    await message.channel.send(f"{display_name} hatte heute einen {laenge}cm Yarak.")
        elif command == "!subschwanz":
            if len(args) == 0:
                if not self.__sql.schwanz_on_cooldown(display_name, "subschwanz"):
                    laenge = randint(0, 200)
                    await message.channel.send(f"{display_name} hat einen {laenge}cm Subschwanz.")
                    self.__sql.update_schwanz_laenge(display_name, "subschwanz", laenge)
                    self.__sql.process_highscore(display_name)
                else:
                    laenge = self.__sql.get_schwanz_laenge(display_name, "subschwanz")
                    await message.channel.send(f"{display_name} hatte heute einen {laenge}cm Subschwanz.")
        elif command == "!stats":
            if len(args) == 0:
                embed = self.__get_stats_embed(display_name, color)
                await message.channel.send(embed=embed)
            elif len(args) == 1:
                if self.__sql.user_exists(args[0]):
                    embed = self.__get_stats_embed(args[0], color)
                    await message.channel.send(embed=embed)
                else:
                    await message.channel.send(f"Es gibt den User \"{args[0]}\" nicht.")
        elif command == "!bestenliste":
            if len(args) == 0:
                ranks = ""
                users = ""
                laengen = ""
                bl = self.__sql.get_ordered_highscores()[:10]
                for i in range(len(bl)):
                    ranks += f"#{i+1}\n"
                    users += f"{bl[i][0]}\n"
                    laengen += f"{bl[i][1]}cm\n"
                
                embed = discord.Embed(title=f"Bestenliste (Top 10)", color=color)
                embed.add_field(name="Rank", value=ranks)
                embed.add_field(name="User", value=users)
                embed.add_field(name="Länge", value=laengen)
                await message.channel.send(embed=embed)
        elif command == "!addcom":
            if len(args) == 2:
                if not self.__sql.text_command_exists(args[0]):
                    self.__sql.add_text_command(args[0], args[1])
                    await message.channel.send(f"Der Command \"{args[0]}\" wurde hinzugefügt.")
                else:
                    await message.channel.send(f"Den Command \"{args[0]}\" gibt es schon.")
        elif command == "!delcom":
            if len(args) == 1:
                if self.__sql.text_command_exists(args[0]):
                    self.__sql.delete_text_command(args[0])
                    await message.channel.send(f"Der Command \"{args[0]}\" wurde gelöscht.")
                else:
                    await message.channel.send(f"Den Command \"{args[0]}\" gibt es nicht.")
        elif command == "!editcom":
            if len(args) == 2:
                if self.__sql.text_command_exists(args[0]):
                    self.__sql.edit_text_command(args[0], args[1])
                    await message.channel.send(f"Der Command \"{args[0]}\" wurde bearbeitet.")
                else:
                    await message.channel.send(f"Den Command \"{args[0]}\" gibt es nicht.")

    def __get_stats_embed(self, display_name, color):
        embed = discord.Embed(title=f"{display_name} Stats", color=color)
        embed.add_field(name="Typ", value="Schwanz\nYarak\nSubschwanz\nInsgesamt")
        schwaenze = [
            self.__sql.get_schwanz_laenge(display_name, "schwanz"),
            self.__sql.get_schwanz_laenge(display_name, "yarak"),
            self.__sql.get_schwanz_laenge(display_name, "subschwanz")
        ]
        insgesamt = 0
        for n, i in enumerate(schwaenze):
            if i != None:
                insgesamt += schwaenze[n]

        bl = self.__sql.get_ordered_highscores()
        highscore = None
        rank = None
        for i in range(len(bl)):
            if bl[i][0] == display_name:
                highscore = bl[i][1]
                rank = i+1
        highscore = self.__sql.get_value_where("highscore", "users", ("display_name", display_name))
        if highscore == None: highscore = "- "
        if rank == None: rank = "-"
        
        embed.add_field(name="Länge", value=f"{schwaenze[0]}cm\n{schwaenze[1]}cm\n{schwaenze[2]}cm\n{insgesamt}cm".replace("None", "- "))
        embed.add_field(name="Highscore", value=f"{highscore}cm (#{rank})", inline=False)
        
        online_time_minutes = self.__sql.get_online_time(display_name)
        online_time = "{:.2f}".format(online_time_minutes / 60)
        embed.add_field(name="Online Zeit", value=f"{online_time} Stunden", inline=False)
        return embed

    @tasks.loop(seconds=60)
    async def count_time(self):
        for member in self.get_guild(408639338910449664).get_channel(505060092811411493).members:
            if member.voice:
                self.__sql.add_online_time(member.display_name, 1)
        