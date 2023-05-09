import sqlite3


class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        result = self.cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
        return bool(len(result.fetchall()))

    def wallet_exists(self, wallet):
        result = self.cursor.execute("SELECT id FROM users WHERE wallet = ?", (wallet,))
        return bool(len(result.fetchall()))

    def add_wallet(self, wallet, user_id):
        self.cursor.execute("UPDATE users SET wallet = ? WHERE user_id = ?", (wallet, user_id,))
        return self.conn.commit()

    def check_wallet(self, wallet):
        result = self.cursor.execute("SELECT id FROM users WHERE wallet = ?", (wallet,))
        return bool(len(result.fetchall()))

    def get_wallet(self, user_id):
        result = self.cursor.execute("SELECT wallet FROM users WHERE user_id = ?", (user_id,))
        return ''.join(map(str, result.fetchall()[0]))

    def get_chat(self, wallet):
        result = self.cursor.execute("SELECT user_id FROM users WHERE wallet = ?", (wallet,))
        return ''.join(map(str, result.fetchall()[0]))

    def get_user_id(self, user_id):
        result = self.cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
        return result.fetchall()[0]

    def add_user(self, user_id):
        self.cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        return self.conn.commit()

    def add_moss(self, user_id):
        self.cursor.execute("UPDATE users SET moss = moss+1 WHERE user_id = ?", (user_id,))
        return self.conn.commit()

    def trans_moss(self, wallet, countmoss, chatid):
        self.cursor.execute("UPDATE users SET moss = moss+? WHERE wallet = ?",
                            (countmoss, wallet,))
        self.cursor.execute("UPDATE users SET moss = moss-? WHERE user_id = ?",
                            (countmoss, chatid,))
        return self.conn.commit()

    def moss_from_userid(self, user_id):
        result = self.cursor.execute("SELECT moss FROM users WHERE user_id = ?", (user_id,))
        return ''.join(map(str, result.fetchall()[0]))

    def moss_from_wallet(self, wallet):
        result = self.cursor.execute("SELECT moss FROM users WHERE wallet = ?", (wallet,))
        return ''.join(map(str, result.fetchall()[0]))

    def moss_cum(self):
        result = self.cursor.execute("SELECT sum(moss) FROM users")
        return ''.join(map(str, result.fetchall()[0]))

    def max_id(self):
        result = self.cursor.execute("SELECT max(id) FROM users")
        return ''.join(map(str, result.fetchall()[0]))

    def userid_from_id(self, id_):
        result = self.cursor.execute("SELECT user_id FROM users WHERE id = ?", (id_,))
        return ''.join(map(str, result.fetchall()[0]))

    def close(self):
        self.conn.close()
