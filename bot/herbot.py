import discord
import os
import datetime

class Herbot(discord.Client):
    
    def __init__(self, db):
        super().__init__()
        self.__dbcursor = db.cursor()
        self.__setup_db()

    def __setup_db(self):
        self.__dbcursor.execute("CREATE DATABASE IF NOT EXISTS herbot")
        self.__dbcursor.execute("USE herbot")
        self.__dbcursor.execute("CREATE TABLE IF NOT EXISTS commands (id INT AUTO_INCREMENT PRIMARY KEY, command VARCHAR(32), text VARCHAR(1024))")
        self.__dbcursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, display_name VARCHAR(64), schwanz TINYINT(3) UNSIGNED, yarak TINYINT(3) UNSIGNED, subschwanz TINYINT(3) UNSIGNED, highscore SMALLINT(3) UNSIGNED)")
        self.__dbcursor.execute("CREATE TABLE IF NOT EXISTS settings (last_date DATE)")