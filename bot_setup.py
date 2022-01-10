import sqlite3

"""Sets up database and adds items to it"""


def add_store_from_list(
    item_name, item_desc, item_price, in_buhinet, usable, item_function
):
    con = sqlite3.connect("economy.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM store_data WHERE item_name=?", (item_name,))
    item = cur.fetchall()
    if item == []:
        cur.execute(
            "INSERT INTO store_data VALUES (?, ?, ?, ?, ?, ?)",
            (item_name, item_desc, item_price, in_buhinet, usable, item_function),
        )
    else:
        cur.execute(
            """ UPDATE store_data
                        SET item_name=?, item_desc=?, item_price=?, in_buhinet=?, usable=?, item_function=?
                        WHERE item_name=?""",
            (
                item_name,
                item_desc,
                item_price,
                in_buhinet,
                usable,
                item_function,
                item_name,
            ),
        )

    con.commit()
    con.close()


def add_items(item_list):
    for item in item_list:
        item_name, item_desc, item_price, in_buhinet, usable, item_function = item
        add_store_from_list(
            item_name, item_desc, item_price, in_buhinet, usable, item_function
        )


def create_tables():
    con = sqlite3.connect("economy.db")
    cur = con.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS inventory_data(
                user_id integer,
                item_name str references store_data,
                amount integer)"""
    )
    cur.execute(
        """ CREATE TABLE IF NOT EXISTS user_data(
                    user_id integer,
                    balance integer)"""
    )
    cur.execute(
        """ CREATE TABLE IF NOT EXISTS store_data(
                    item_name text,
                    item_desc text,
                    item_price integer,
                    in_buhinet bit,
                    usable bit,
                    item_function text
                    )"""
    )
    con.commit()
    con.close()
