import discord
from discord.ext import tasks
import os
from random import randint
import shlex
from .sql import SQL
import math

class Herbot(discord.Client):
    
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.__sql = SQL(os.getenv("MYSQL_HOST"), os.getenv("MYSQL_USER"), os.getenv("MYSQL_PASSWORD"), os.getenv("MYSQL_DATABASE"))
        self.enabled_members = [(408639338910449664, 505060092811411493)]
        self.ignored_voice_channels = [408730091682791425]
        
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
        command = msg[0].lower()
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
                embed = self.__get_stats_embed(message.author, color)
                await message.channel.send(embed=embed)
            elif len(args) == 1:
                if self.__sql.user_exists(args[0]):
                    for user in message.channel.members:
                        if user.display_name.lower() == args[0].lower():
                            embed = self.__get_stats_embed(user, color)
                            await message.channel.send(embed=embed)
                else:
                    await message.channel.send(f"Es gibt den User \"{args[0]}\" nicht.")
        elif command == "!187":
            count = self.__sql.get_value_where("187_count", "users", ("display_name", display_name))
            await message.channel.send(f"{display_name} hat {count} mal 187 gehabt. :one: :eight: :seven:")
        elif command == "!69":
            count = self.__sql.get_value_where("69_count", "users", ("display_name", display_name))
            await message.channel.send(f"{display_name} hat {count} mal 69 gehabt. nice. :joy:")
        elif command == "!88":
            count = self.__sql.get_value_where("88_count", "users", ("display_name", display_name))
            await message.channel.send(f"{display_name} hat {count} mal 88 gehabt. :sunglasses:")
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

                if not bl: await message.channel.send("Es gibt noch keine Einträge.")
                embed = discord.Embed(title=f"Bestenliste (Top 10)", color=color)
                embed.add_field(name="Rank", value=ranks)
                embed.add_field(name="User", value=users)
                embed.add_field(name="Länge", value=laengen)
                await message.channel.send(embed=embed)
            if len(args) == 1:
                if args[0].lower() == "kleinster":
                    ranks = ""
                    users = ""
                    laengen = ""
                    bl = self.__sql.get_ordered_kleinster()[:10]
                    for i in range(len(bl)):
                        ranks += f"#{i+1}\n"
                        users += f"{bl[i][0]}\n"
                        laengen += f"{bl[i][1]}cm\n"

                    if not bl:
                        await message.channel.send("Es gibt noch keine Einträge.")
                        return
                    embed = discord.Embed(title=f"Kleinster (Top 10)", color=color)
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
        elif command == "!help":
            if len(args) == 0:
                embed = self.__get_command_list_embed(color, 1)
                await message.channel.send(embed=embed)
            if len(args) == 1:
                if args[0].isnumeric():
                    embed = self.__get_command_list_embed(color, int(args[0]))
                    await message.channel.send(embed=embed)

    def __get_command_list_embed(self, color, page):
        commands = self.__sql.query("SELECT * FROM commands", ())
        num_pages = math.ceil(len(commands) / 10)
        if (page > num_pages):
            return self.__get_command_list_embed(color, num_pages)
        embed = discord.Embed(title=f"Liste mit allen Text Commands (Seite {page}/{num_pages})", color=color)
        all_commands_string = ""
        all_texts_string = ""
        start = 10 * (page - 1)
        end = 10 * page
        if len(commands) < end:
            end = len(commands)
        for i in range(start, end):
            command = commands[i]
            all_commands_string += command[0] + "\n"
            if len(command[1]) > 55:
                all_texts_string += command[1][:55] + "...\n"
            else:
                all_texts_string += command[1] + "\n"
        all_commands_string = all_commands_string[:-1]
        all_texts_string = all_texts_string[:-1]
        embed.add_field(name="Command", value=all_commands_string)
        embed.add_field(name="Text", value=all_texts_string)
        
        return embed
                
    def __get_stats_embed(self, user, color):
        display_name = user.display_name
        embed = discord.Embed(title=f"{display_name} Stats", color=color)
        embed.set_thumbnail(url=user.avatar_url_as(size=128))
        embed.add_field(name="Typ", value="Schwanz\nYarak\nSubschwanz\nInsgesamt", inline=True)
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
        rank = None
        for i in range(len(bl)):
            if bl[i][0] == display_name:
                rank = i+1
                
        highscore = self.__sql.get_value_where("highscore", "users", ("display_name", display_name))

        bl_kleinster = self.__sql.get_ordered_kleinster()
        rank_kleinster = None
        for i in range(len(bl_kleinster)):
            if bl_kleinster[i][0] == display_name:
                rank_kleinster = i+1
                
        kleinster_schwanz = self.__sql.get_value_where("kleinster_schwanz", "users", ("display_name", display_name))
        if highscore is None: highscore = "- "
        if rank is None: rank = "-"
        if rank_kleinster is None: rank_kleinster = "-"
        if kleinster_schwanz is None: kleinster_schwanz = "- "
        
        embed.add_field(name="Länge", value=f"{schwaenze[0]}cm\n{schwaenze[1]}cm\n{schwaenze[2]}cm\n{insgesamt}cm".replace("None", "- "), inline=True)
        embed.add_field(name="\u200B", value="\u200B", inline=True)
        embed.add_field(name="Highscore", value=f"{highscore}cm (#{rank})", inline=True)
        embed.add_field(name="Kleinster", value=f"{kleinster_schwanz}cm (#{rank_kleinster})")
        embed.add_field(name="\u200B", value="\u200B", inline=True)
        online_time_minutes = self.__sql.get_online_time(display_name)
        online_time = "{:.2f}".format(online_time_minutes / 60)
        embed.add_field(name="Online Zeit (Voice)", value=f"{online_time} Stunden", inline=False)

        streaming_time_minutes = self.__sql.get_streaming_time(display_name)
        streaming_time = "{:.2f}".format(streaming_time_minutes / 60)
        embed.add_field(name="Gestreamte Zeit", value=f"{streaming_time} Stunden")
        return embed

    @tasks.loop(seconds=60)
    async def count_time(self):
        for i in range(len(self.enabled_members)):
            for member in self.get_guild(self.enabled_members[i][0]).get_channel(self.enabled_members[i][1]).members:
                if member.voice:
                    if member.voice.channel.id in self.ignored_voice_channels: continue
                    if not self.__sql.is_connected(): self.__sql.reconnect()
                    self.__sql.add_online_time(member.display_name, 1)
                    if member.voice.self_stream:
                        self.__sql.add_streaming_time(member.display_name, 1)
        
