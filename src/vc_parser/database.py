import sqlite3 as sq

con = sq.connect('data.db')
cur = con.cursor()


def create_table(source):
    cur.execute(f"""CREATE TABLE IF NOT EXISTS {source} (
                   platform_id INT,
                   generated_url VARCHAR(255),
                   url VARCHAR(255),
                   date DATE,
                   time DATE,
                   title VARCHAR(127),
                   author VARCHAR(127),
                   profile_link VARCHAR(63),
                   subsite VARCHAR(31),
                   subsite_link VARCHAR(63),
                   company VARCHAR(63),
                   company_link VARCHAR(63),
                   text TEXT,
                   hyperlinks TEXT,
                   attachments TEXT,
                   comments_count SMALLINT,
                   rating SMALLINT,
                   favorites SMALLINT,
                   is_subsite BOOLEAN,
                   is_author BOOLEAN,
                   status_code SMALLINT,
                   rescan BOOLEAN
                   )""")


def insert_data(data, source):
    with con:
        values = tuple(data.values())
        cur.execute(f"""INSERT INTO {source} (
                        platform_id,
                        generated_url,
                        url,
                        date,
                        time,
                        title,
                        author,
                        profile_link,
                        subsite,
                        subsite_link,
                        company,
                        company_link,
                        text,
                        hyperlinks,
                        attachments,
                        comments_count,
                        rating,
                        favorites,
                        is_subsite,
                        is_author,
                        status_code
                        )
                    VALUES (
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?
                        )""", values)


def get_parsed_ids(source):
    with con:
        cur.row_factory = lambda cursor, row: row[0]
        cur.execute(f"""SELECT platform_id FROM {source}""")
        ids = cur.fetchall()
    return ids
