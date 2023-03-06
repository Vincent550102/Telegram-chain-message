import sqlite3
import json


class Database():
    def __init__(self):
        self.con = sqlite3.connect(
            'database/sqlite.db', check_same_thread=False)
        self.cur = self.con.cursor()
        sql_init = open('database/init.sql', 'r').read()
        self.con.executescript(sql_init)
        self.con.commit()

    def __del__(self):
        self.con.close()

    def select_all_chain_by_id(self, group_id):
        self.cur.execute(
            "SELECT chain_group FROM chains WHERE group_id = ?", (group_id,))
        result = self.cur.fetchone()
        return json.loads(result[0]) if result != None else []

    def update_chain_by_id(self, group_id, chain_group):
        self.cur.execute(
            "SELECT chain_group FROM chains WHERE group_id = ?", (group_id,))
        result = self.cur.fetchone()
        print(result)
        if result is None:
            self.cur.execute(
                "INSERT INTO chains (group_id, chain_group) VALUES (?, ?)",
                (group_id, json.dumps([chain_group])))
        else:
            chain_group_new = json.loads(result[0])
            if chain_group not in chain_group_new:
                chain_group_new.append(chain_group)
                print(chain_group_new)
                self.cur.execute(
                    "UPDATE chains SET chain_group = ? WHERE group_id = ?",
                    (json.dumps(chain_group_new),
                     group_id))
                self.con.commit()

    def delete_chain_by_id(self, group_id, chain_group):
        self.cur.execute(
            "SELECT chain_group FROM chains WHERE group_id = ?", (group_id,))
        result = self.cur.fetchone()
        if result is not None:
            chain_group_delete = json.loads(result[0])
            if chain_group in chain_group_delete:
                chain_group_delete.remove(chain_group)
                self.cur.execute(
                    "UPDATE chains SET chain_group = ? WHERE group_id = ?",
                    (json.dumps(chain_group_delete),
                     group_id))
                self.con.commit()
                return True
        return False
