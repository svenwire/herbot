from mysql import connector
from datetime import datetime

class SQL():
    def __init__(self, host, user, password, database):
        self.__db = connector.connect(host=host, user=user, passwd=password, database=database)
        self.__cursor = self.__db.cursor(buffered=True)
        self.__create_tables()
        

    def __create_tables(self):
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS commands (command VARCHAR(32) PRIMARY KEY, text VARCHAR(1024))")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS users (id BIGINT(18) PRIMARY KEY, display_name VARCHAR(64), schwanz TINYINT(3) UNSIGNED DEFAULT NULL, yarak TINYINT(3) UNSIGNED DEFAULT NULL, subschwanz TINYINT(3) UNSIGNED DEFAULT NULL, highscore SMALLINT(3) UNSIGNED DEFAULT NULL, online_time INT DEFAULT 0, 187_count INT DEFAULT 0 NOT NULL, streaming_time INT DEFAULT 0, 88_count INT DEFAULT 0, 69_count INT DEFAULT 0, kleinster_schwanz INT DEFAULT NULL, 1337_count int DEFAULT 0, 1337_today BIT(1) DEFAULT 0)")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS settings (name VARCHAR(32) PRIMARY KEY, val VARCHAR(512))")

    def reconnect(self):
        self.__db.reconnect()
        self.__cursor.execute("USE herbot")

    def is_connected(self):
        return self.__db.is_connected()

    def execute(self, statement, data):
        self.__cursor.execute(statement, data)
        self.__db.commit()

    def query(self, statement, data):
        self.__cursor.execute(statement, data)
        return self.__cursor.fetchall()

    def text_command_exists(self, command):
        result = self.query("SELECT command FROM commands WHERE command = %s", (command,))
        if result: return True
        else: return False

    def check_next_date(self):
        result = self.query("SELECT val FROM settings WHERE name = %s", ('next_date',))
        if result:
            next_date = datetime.strptime(result[0][0], '%Y-%m-%d').date()
            if datetime.today().date() > next_date:
                self.execute("UPDATE users SET schwanz = %s, yarak = %s, subschwanz = %s", (None, None, None))
                self.execute("UPDATE settings SET val = %s WHERE name = %s", (datetime.today().date(), 'next_date'))
                self.execute("UPDATE users SET 1337_today = %s", (0,))
        else:
            self.execute("INSERT INTO settings (name, val) VALUES (%s, %s)", ('next_date', datetime.today().date()))
 
    def schwanz_on_cooldown(self, user, schwanz_type):
        laenge = self.get_value_where(schwanz_type, "users", ("id", user.id))
        if laenge is None: return False
        else: return True
        
        """
        result = self.query("SELECT {} from users WHERE display_name = %s".format(schwanz_type), (display_name,))
        if result[0][0] == None: return False
        else: return True
        """
    def get_ordered_highscores(self):
        return self.query("SELECT id, display_name, highscore from users WHERE highscore IS NOT NULL ORDER BY highscore DESC", ())

    def get_ordered_kleinster(self):
        return self.query("SELECT id, display_name, kleinster_schwanz from users WHERE kleinster_schwanz IS NOT NULL ORDER BY kleinster_schwanz ASC", ())

    def get_value_where(self, column, table, where):
        val = self.query("SELECT {} FROM {} WHERE {} = %s".format(column, table, where[0]), (where[1],))
        if val: return val[0][0]
        else: return None

    def update_value_where(self, table, column, value, where):
        self.execute("UPDATE {} SET {} = %s WHERE {} = %s".format(table, column, where[0]), (value, where[1]))

    def check_user(self, user):
        display_name = self.get_value_where("display_name", "users", ("id", user.id))
        if display_name:
            if display_name != user.display_name:
                self.update_value_where("users", "display_name", user.display_name, ("id", user.id))
        else:
            self.add_user(user)

    def user_exists(self, display_name):
        result = self.query("SELECT display_name FROM users WHERE display_name = %s", (display_name,))
        if result: return True
        else: return False

    def process_highscore(self, user):
        result = self.query("SELECT schwanz, yarak, subschwanz, highscore, kleinster_schwanz FROM users WHERE id = %s", (user.id,))
        highscore = result[0][3]
        kleinster_schwanz = result[0][4]
        if None not in result[0][0:3]:
            schwanz_summe = sum(result[0][0:3])
            if highscore is None or highscore < schwanz_summe:
                self.execute("UPDATE users SET highscore = %s WHERE id = %s", (schwanz_summe, user.id))
            if schwanz_summe == 187:
                self.execute("UPDATE users SET 187_count = 187_count + %s WHERE id = %s", (1, user.id))
            if schwanz_summe == 69:
                self.execute("UPDATE users SET 69_count = 69_count + %s WHERE id = %s", (1, user.id))
            if schwanz_summe == 88:
                self.execute("UPDATE users SET 88_count = 88_count + %s WHERE id = %s", (1, user.id))
            if kleinster_schwanz is None or schwanz_summe < kleinster_schwanz:
                self.execute("UPDATE users SET kleinster_schwanz = %s WHERE id = %s", (schwanz_summe, user.id))

    def add_user(self, user):
        self.execute("INSERT INTO users (id, display_name) VALUES (%s, %s)", (user.id, user.display_name))

    def update_schwanz_laenge(self, user, schwanz_type, laenge):
        self.update_value_where("users", schwanz_type, laenge, ("id", user.id))

    def get_schwanz_laenge(self, user, schwanz_type):
        return self.get_value_where(schwanz_type, "users", ("id", user.id))

    def add_text_command(self, command, text):
        self.execute("INSERT INTO commands (command, text) VALUES (%s, %s)", (command, text))

    def delete_text_command(self, command):
        self.execute("DELETE FROM commands WHERE command = %s", (command,))

    def edit_text_command(self, command, text):
        self.update_value_where("commands", "text", text, ("command", command))

    def add_online_time(self, user, minutes):
        self.execute("UPDATE users SET online_time = online_time + %s WHERE id = %s", (minutes, user.id))

    def add_streaming_time(self, user, minutes):
        self.execute("UPDATE users SET streaming_time = streaming_time + %s WHERE id = %s", (minutes, user.id))

    def add_1337_count(self, user, count):
        self.execute("UPDATE users SET 1337_count = 1337_count + %s WHERE id = %s", (count, user.id))
        self.update_value_where("users", "1337_today", 1, ("id", user.id))
