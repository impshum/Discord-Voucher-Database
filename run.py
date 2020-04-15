import discord
import asyncio
import sqlite3
from sqlite3 import Error
import datetime
import configparser

config = configparser.ConfigParser()
config.read('conf.ini')
discord_token = config['DISCORD']['token']
types = ['ticket', 'popcorn', 'drink']


def db_connect():
    try:
        conn = sqlite3.connect('data.db')
        create_table = """CREATE TABLE IF NOT EXISTS vouchers (
                                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                        type TEXT NOT NULL,
                                        code TEXT NOT NULL,
                                        date TEXT NULL
                                        );"""
        conn.execute(create_table)
        return conn
    except Error as e:
        print(e)
    return None


conn = db_connect()


def insert_row(conn, type, code):
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM vouchers WHERE type='{}' AND code='{}'".format(type, code))
    if not len(cur.fetchall()):
        conn.execute(
            "INSERT INTO vouchers (type, code) VALUES (?, ?)", (type, code))
        conn.commit()
        print(f'Adding new {type} to db')
    cur.close()


def search_db(conn, type, amount):
    print('searching db')
    results = []
    cur = conn.cursor()
    if type == 'bundle':
        if type == 'bundle':
            for i in range(amount):
                for type in types:
                    cur.execute(
                        "SELECT * FROM vouchers WHERE type='{}' AND date IS NULL LIMIT 1".format(type))
                    row = cur.fetchone()
                    if row:
                        results.append({row[1]: row[2]})
                        now = datetime.datetime.now().strftime('%c')
                        cur.execute("UPDATE vouchers SET date='{}' WHERE ID={}".format(now, row[0]))
                        conn.commit()
    else:
        cur.execute(
            "SELECT * FROM vouchers WHERE type='{}' AND date IS NULL LIMIT {}".format(type, amount))
        rows = cur.fetchall()
        for row in rows:
            results.append({row[1]: row[2]})
            now = datetime.datetime.now().strftime('%c')
            cur.execute("UPDATE vouchers SET date='{}' WHERE ID={}".format(now, row[0]))
            conn.commit()
    cur.close()
    return results


def read_db(conn, mode, limit=False):
    cur = conn.cursor()
    if mode == 'stats':
        used = ''
        unused = ''
        bundles = 0
        things = {'ticket': 0, 'popcorn': 0, 'drink': 0}

        for type in types:
            cur.execute(
                "SELECT COUNT(*) FROM vouchers WHERE type='{}' AND date IS NOT NULL".format(type))
            rows = cur.fetchall()
            for row in rows:
                count = row[0]
                used += f'Used {type}: {count}\n'

        for type in types:
            cur.execute(
                "SELECT COUNT(*) FROM vouchers WHERE type='{}' AND date IS NULL".format(type))
            rows = cur.fetchall()
            for row in rows:
                count = row[0]
                unused += f'Unused {type}: {count}\n'
                things[type] = count

        value = 2
        while value > 1:
            bundles += 1
            for thing, value in things.items():
                things[thing] -= 1

        result = f'{used.strip()}\n\n{unused.strip()}\n\nUnused bundles: {bundles}'
    else:
        cur.execute(
            "SELECT * FROM vouchers ORDER BY ID DESC LIMIT {}".format(limit))
        rows = cur.fetchall()
        result = ''
        for row in rows:
            result += f'{row[1]} - {row[2]} - {row[3]}\n'
    return result


def populate_db(conn):
    print('populating db')
    for type in types:
        with open(f'data/{type}.txt') as f:
            for code in f.read().splitlines():
                insert_row(conn, type, code)


class DiscordClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user.name}')
        #print(self.user.id)
        print('------')

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        user_input = message.content

        if user_input.startswith('/v'):
            populate_db(conn)
            order = {}

            codes = user_input.replace('/v', '').strip().split(' ')
            print(' '.join(codes))
            for code in codes:
                if code.endswith('b'):
                    amount = code.replace('b', '')
                    order['bundle'] = amount
                elif code.endswith('t'):
                    amount = code.replace('t', '')
                    order['ticket'] = amount
                elif code.endswith('p'):
                    amount = code.replace('p', '')
                    order['popcorn'] = amount
                elif code.endswith('d'):
                    amount = code.replace('d', '')
                    order['drink'] = amount

            reply = ''
            for item, amount in order.items():
                results = search_db(conn, item, int(amount))
                for result in results:
                    for k, v in result.items():
                        reply += f'{k} - {v}\n'

            if not len(reply):
                reply = 'No vouchers left!'
            return await message.channel.send(reply)

        elif user_input == '/help':
            print('help')
            reply = '/help - Show help\n\n/stats - Show used/unused count\n/readall - Read all in database add a number to limit results\n\nStart the process with /v\n\n1b = 1 x bundle\n1t = 1 x ticket\n1p = 1 x popcorn\n1d = 1 x drink\n\nExamples\n/v 2t 1p 2d\n/readall3'
            return await message.channel.send(reply)

        elif user_input == '/stats':
            reply = read_db(conn, 'stats')
            return await message.channel.send(reply)

        elif user_input.startswith('/readall'):
            print('readall')
            amount = user_input.replace('/readall', '')
            limit = 50
            if amount:
                limit = int(amount)
            reply = read_db(conn, 'all', limit)
            return await message.channel.send(reply)


def main():
    populate_db(conn)
    client = DiscordClient()
    client.run(discord_token)


if __name__ == '__main__':
    main()
