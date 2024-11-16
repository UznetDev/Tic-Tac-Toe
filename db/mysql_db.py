# database.py
import mysql.connector
import pandas as pd

class Database:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            game_id INT,
            move_number INT,
            player INT,
            position VARCHAR(5),
            result VARCHAR(10)
        )
        """)
        self.conn.commit()

    def insert_move(self, game_id, move_number, player, position, result):
        sql = "INSERT INTO game_data (game_id, move_number, player, position, result) VALUES (%s, %s, %s, %s, %s)"
        val = (game_id, move_number, player, str(position), result)
        self.cursor.execute(sql, val)
        self.conn.commit()

    def close(self):
        self.conn.close()
