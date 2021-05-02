import discord
from discord.ext import tasks
import os
from random import randint
import shlex
from .sql import SQL
import math
from datetime import datetime

class Herbot(discord.Client):
    
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.sql = SQL(os.getenv("MYSQL_HOST"), os.getenv("MYSQL_USER"), os.getenv("MYSQL_PASSWORD"), os.getenv("MYSQL_DATABASE"))
        self.enabled_members = [(408639338910449664, 505060092811411493)]
        self.ignored_voice_channels = [408730091682791425]
        self.embed_color = discord.Color.gold()
        
    async def on_ready(self):
        self.count_time.start()
        print("[HERBOT] ist am start yo.")

    async def on_message(self, message):
        if not self.sql.is_connected():
            self.sql.reconnect()

        user = message.author

        if user == self.user:
            return

        role_minimum = 6
        highest_role = 0
        for role in user.roles:
            if highest_role < role.position:
                highest_role = role.position
        
        if highest_role < role_minimum: return

        # create user if it does not exist or update display_name if changed
        self.sql.check_user(user)
        
        msg = shlex.split(message.content)
        command = msg[0].lower()
        args = msg[1:]

        # check for text command and get it's message if exists
        if self.sql.text_command_exists(command):
            text = self.sql.get_value_where("text", "commands", ("command", command))
            await message.channel.send(text)

        # check for other commands
        self.sql.check_next_date()

        if command == "!schwanz":
            if len(args) == 0:
                if not self.sql.schwanz_on_cooldown(user, "schwanz"):
                    laenge = randint(0, 100)
                    await message.channel.send(f"{user.display_name} hat einen {laenge}cm Schwanz.")
                    self.sql.update_schwanz_laenge(user, "schwanz", laenge)
                    self.sql.process_highscore(user)
                else:
                    laenge = self.sql.get_schwanz_laenge(user, "schwanz")
                    await message.channel.send(f"{user.display_name} hatte heute einen {laenge}cm Schwanz.")
        elif command == "!yarak":
            if len(args) == 0:
                if not self.sql.schwanz_on_cooldown(user, "yarak"):
                    laenge = randint(0, 100)
                    await message.channel.send(f"{user.display_name} hat einen {laenge}cm Yarak.")
                    self.sql.update_schwanz_laenge(user, "yarak", laenge)
                    self.sql.process_highscore(user)
                else:
                    laenge = self.sql.get_schwanz_laenge(user, "yarak")
                    await message.channel.send(f"{user.display_name} hatte heute einen {laenge}cm Yarak.")
        elif command == "!subschwanz":
            if len(args) == 0:
                if not self.sql.schwanz_on_cooldown(user, "subschwanz"):
                    laenge = randint(0, 200)
                    await message.channel.send(f"{user.display_name} hat einen {laenge}cm Subschwanz.")
                    self.sql.update_schwanz_laenge(user, "subschwanz", laenge)
                    self.sql.process_highscore(user)
                else:
                    laenge = self.sql.get_schwanz_laenge(user, "subschwanz")
                    await message.channel.send(f"{user.display_name} hatte heute einen {laenge}cm Subschwanz.")
        elif command == "!stats":
            if len(args) == 0:
                embed = self.get_stats_embed(user, self.embed_color)
                await message.channel.send(embed=embed)
            elif len(args) == 1:
                if self.sql.user_exists(args[0]):
                    for member in message.channel.members:
                        if member.display_name.lower() == args[0].lower():
                            embed = self.get_stats_embed(member, self.embed_color)
                            await message.channel.send(embed=embed)
                else:
                    await message.channel.send(f"Es gibt den User \"{args[0]}\" nicht.")
        elif command == "!187":
            count = self.sql.get_value_where("187_count", "users", ("id", user.id))
            await message.channel.send(f"{user.display_name} hat {count} mal 187 gehabt. :one: :eight: :seven:")
        elif command == "!69":
            count = self.sql.get_value_where("69_count", "users", ("id", user.id))
            await message.channel.send(f"{user.display_name} hat {count} mal 69 gehabt. nice. :joy:")
        elif command == "!88":
            count = self.sql.get_value_where("88_count", "users", ("id", user.id))
            await message.channel.send(f"{user.display_name} hat {count} mal 88 gehabt. :sunglasses:")
        elif command == "!1337":
            count = self.sql.get_value_where("1337_count", "users", ("id", user.id))
            time = datetime.now().time()
            if time.hour == 13 and time.minute == 37:
                already_did_today = self.sql.get_value_where("1337_today", "users", ("id", user.id))
                if not already_did_today:
                    await message.channel.send(f"Juhu, es ist 13:37 Uhr! {user.display_name} war jetzt {count + 1} mal um 13:37 Uhr da.")
                    self.sql.add_1337_count(user, 1)
                    return
            await message.channel.send(f"{user.display_name} war {count} mal um 13:37 Uhr da.")
            
                
        elif command == "!bestenliste":
            if len(args) == 0:
                ranks = ""
                users = ""
                laengen = ""
                bl = self.sql.get_ordered_highscores()[:10]
                for i in range(len(bl)):
                    ranks += f"#{i+1}\n"
                    users += f"{bl[i][1]}\n"
                    laengen += f"{bl[i][2]}cm\n"

                if not bl: await message.channel.send("Es gibt noch keine Einträge.")
                embed = discord.Embed(title=f"Bestenliste (Top 10)", color=self.embed_color)
                embed.add_field(name="Rank", value=ranks)
                embed.add_field(name="User", value=users)
                embed.add_field(name="Länge", value=laengen)
                await message.channel.send(embed=embed)
            if len(args) == 1:
                if args[0].lower() == "kleinster":
                    ranks = ""
                    users = ""
                    laengen = ""
                    bl = self.sql.get_ordered_kleinster()[:10]
                    for i in range(len(bl)):
                        ranks += f"#{i+1}\n"
                        users += f"{bl[i][1]}\n"
                        laengen += f"{bl[i][2]}cm\n"

                    if not bl:
                        await message.channel.send("Es gibt noch keine Einträge.")
                        return
                    embed = discord.Embed(title=f"Kleinster (Top 10)", color=self.embed_color)
                    embed.add_field(name="Rank", value=ranks)
                    embed.add_field(name="User", value=users)
                    embed.add_field(name="Länge", value=laengen)
                    await message.channel.send(embed=embed)
        elif command == "!addcom":
            if len(args) == 2:
                if not self.sql.text_command_exists(args[0]):
                    self.sql.add_text_command(args[0], args[1])
                    await message.channel.send(f"Der Command \"{args[0]}\" wurde hinzugefügt.")
                else:
                    await message.channel.send(f"Den Command \"{args[0]}\" gibt es schon.")
        elif command == "!delcom":
            if len(args) == 1:
                if self.sql.text_command_exists(args[0]):
                    self.sql.delete_text_command(args[0])
                    await message.channel.send(f"Der Command \"{args[0]}\" wurde gelöscht.")
                else:
                    await message.channel.send(f"Den Command \"{args[0]}\" gibt es nicht.")
        elif command == "!editcom":
            if len(args) == 2:
                if self.sql.text_command_exists(args[0]):
                    self.sql.edit_text_command(args[0], args[1])
                    await message.channel.send(f"Der Command \"{args[0]}\" wurde bearbeitet.")
                else:
                    await message.channel.send(f"Den Command \"{args[0]}\" gibt es nicht.")
        elif command == "!help":
            if len(args) == 0:
                embed = self.get_command_list_embed(self.embed_color, 1)
                await message.channel.send(embed=embed)
            if len(args) == 1:
                if args[0].isnumeric():
                    embed = self.get_command_list_embed(self.embed_color, int(args[0]))
                    await message.channel.send(embed=embed)

    def get_command_list_embed(self, color, page):
        commands = self.sql.query("SELECT * FROM commands", ())
        num_pages = math.ceil(len(commands) / 10)
        if (page > num_pages):
            return self.get_command_list_embed(color, num_pages)
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
                
    def get_stats_embed(self, user, color):
        embed = discord.Embed(title=f"{user.display_name} Stats", color=color)
        embed.set_thumbnail(url=user.avatar_url_as(size=128))
        embed.add_field(name="Typ", value="Schwanz\nYarak\nSubschwanz\nInsgesamt", inline=True)
        schwaenze = [
            self.sql.get_schwanz_laenge(user, "schwanz"),
            self.sql.get_schwanz_laenge(user, "yarak"),
            self.sql.get_schwanz_laenge(user, "subschwanz")
        ]
        insgesamt = 0
        for n, i in enumerate(schwaenze):
            if i != None:
                insgesamt += schwaenze[n]

        bl = self.sql.get_ordered_highscores()
        rank = None
        for i in range(len(bl)):
            if bl[i][0] == user.id:
                rank = i+1
                
        highscore = self.sql.get_value_where("highscore", "users", ("id", user.id))

        bl_kleinster = self.sql.get_ordered_kleinster()
        rank_kleinster = None
        for i in range(len(bl_kleinster)):
            if bl_kleinster[i][0] == user.id:
                rank_kleinster = i+1
                
        kleinster_schwanz = self.sql.get_value_where("kleinster_schwanz", "users", ("id", user.id))
        if highscore is None: highscore = "- "
        if rank is None: rank = "-"
        if rank_kleinster is None: rank_kleinster = "-"
        if kleinster_schwanz is None: kleinster_schwanz = "- "
        
        embed.add_field(name="Länge", value=f"{schwaenze[0]}cm\n{schwaenze[1]}cm\n{schwaenze[2]}cm\n{insgesamt}cm".replace("None", "- "), inline=True)
        embed.add_field(name="\u200B", value="\u200B", inline=True)
        embed.add_field(name="Highscore", value=f"{highscore}cm (#{rank})", inline=True)
        embed.add_field(name="Kleinster", value=f"{kleinster_schwanz}cm (#{rank_kleinster})")
        embed.add_field(name="\u200B", value="\u200B", inline=True)
        online_time_minutes = self.sql.get_value_where("online_time", "users", ("id", user.id))
        online_time = "{:.2f}".format(online_time_minutes / 60)
        embed.add_field(name="Online Zeit (Voice)", value=f"{online_time} Stunden", inline=False)

        streaming_time_minutes = self.sql.get_value_where("streaming_time", "users", ("id", user.id))
        streaming_time = "{:.2f}".format(streaming_time_minutes / 60)
        embed.add_field(name="Gestreamte Zeit", value=f"{streaming_time} Stunden")
        return embed

    @tasks.loop(seconds=60)
    async def count_time(self):
        for i in range(len(self.enabled_members)):
            for member in self.get_guild(self.enabled_members[i][0]).get_channel(self.enabled_members[i][1]).members:
                self.sql.check_user(member)
                if member.voice:
                    if member.voice.channel.id in self.ignored_voice_channels: continue
                    if not self.sql.is_connected(): self.__sql.reconnect()
                    self.sql.add_online_time(member, 1)
                    if member.voice.self_stream:
                        self.sql.add_streaming_time(member, 1)
        
