from mysql import connector
from datetime import datetime

class SQL():
    def __init__(self, host, user, password, database):
        self.__db = connector.connect(host=host, user=user, passwd=password, database=database)
        self.__cursor = self.__db.cursor(buffered=True)
        self.__create_tables()
        

    def __create_tables(self):
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS commands (command VARCHAR(32) PRIMARY KEY, text VARCHAR(1024))")
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS users (display_name VARCHAR(64) PRIMARY KEY, schwanz TINYINT(3) UNSIGNED DEFAULT NULL, yarak TINYINT(3) UNSIGNED DEFAULT NULL, subschwanz TINYINT(3) UNSIGNED DEFAULT NULL, highscore SMALLINT(3) UNSIGNED DEFAULT NULL, online_time INT DEFAULT 0)")
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
        else:
            self.execute("INSERT INTO settings (name, val) VALUES (%s, %s)", ('next_date', datetime.today().date()))
 
    def schwanz_on_cooldown(self, display_name, schwanz_type):
        result = self.query("SELECT {} from users WHERE display_name = %s".format(schwanz_type), (display_name,))
        if result == None: return False
        else: return True

    def get_ordered_highscores(self):
        return self.query("SELECT display_name, highscore from users WHERE highscore IS NOT NULL ORDER BY highscore DESC", ())

    def get_value_where(self, column, table, where):
        return self.query("SELECT {} FROM {} WHERE {} = %s".format(column, table, where[0]), (where[1],))[0][0]

    def update_value_where(self, table, column, value, where):
        self.execute("UPDATE {} SET {} = %s WHERE {} = %s".format(table, column, where[0]), (value, where[1]))

    def user_exists(self, display_name):
        result = self.query("SELECT display_name FROM users WHERE display_name = %s", (display_name,))
        if result: return True
        else: return False

    def process_highscore(self, display_name):
        result = self.query("SELECT schwanz, yarak, subschwanz, highscore FROM users WHERE display_name = %s", (display_name,))
        highscore = result[0][3]
        if None not in result[0][0:3]:
            schwanz_summe = sum(result[0][0:3])
            if highscore is None or highscore < schwanz_summe:
                self.execute("UPDATE users SET highscore = %s WHERE display_name = %s", (schwanz_summe, display_name))

    def add_user(self, display_name):
        self.execute("INSERT INTO users (display_name) VALUES (%s)", (display_name,))

    def update_schwanz_laenge(self, display_name, schwanz_type, laenge):
        self.update_value_where("users", schwanz_type, laenge, ("display_name", display_name))

    def get_schwanz_laenge(self, display_name, schwanz_type):
        return self.get_value_where(schwanz_type, "users", ("display_name", display_name))

    def add_text_command(self, command, text):
        self.execute("INSERT INTO commands (command, text) VALUES (%s, %s)", (command, text))

    def delete_text_command(self, command):
        self.execute("DELETE FROM commands WHERE command = %s", (command,))

    def edit_text_command(self, command, text):
        self.update_value_where("commands", "text", text, ("command", command))

    def get_online_time(self, display_name):
        return self.get_value_where("online_time", "users", ("display_name", display_name))

    def add_online_time(self, display_name, minutes):
        self.execute("UPDATE users SET online_time = online_time + %s WHERE display_name = %s", (minutes, display_name))
