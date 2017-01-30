# -*- coding: utf8 -*-

"""
Module defining the database schema (SQLite3 is used) and providing methods
related to database access.
"""

from contextlib import contextmanager
import os
import csv
import sqlite3


NC_PIPPN_COLUMNS = {
    'id': 1,
    'specie': 19,
    'strata': 5,
    'circumference': 6,
    'wood_density': 7,
    'height': 13,
}

STRATAS = {
    'indetermineae': 0,
    'sous-bois': 1,
    'sous-canopee': 2,
    'canopee': 3,
    'emergent': 4
}

BASE = os.path.dirname(__file__)


@contextmanager
def get_cursor(file_path):
    connection = None
    try:
        connection = sqlite3.connect(file_path)
        yield connection.cursor()
        connection.commit()
    except:
        if connection is not None:
            connection.rollback()
        raise
    finally:
        if connection is not None:
            connection.close()


def load_nc_pippn(nc_pippn_csv):
    with open(nc_pippn_csv, 'r') as csvfile:
        ncpippn = csv.reader(csvfile, delimiter=';')
        cols = ('id', 'specie', 'strata', 'circumference',
                'wood_density', 'height')
        idx = [NC_PIPPN_COLUMNS[k] for k in cols]
        data = list()
        for j, row in enumerate(ncpippn):
            if j == 0:
                continue
            values = list()
            for i, col in enumerate(cols):
                v = row[idx[i]]
                if col == 'strata':
                    values.append(str(STRATAS[v]))
                else:
                    values.append(v.replace(',', '.'))
            data.append(values)
        return data


def make_ncpippn_db(nc_pippn_csv, db_path):
    data = load_nc_pippn(nc_pippn_csv)
    with get_cursor(db_path) as cursor:
        cursor.execute(
            """
            CREATE TABLE ncpippn (
                id INTEGER PRIMARY KEY,
                specie TEXT,
                strata INTEGER,
                circumference REAL,
                wood_density REAL,
                height REAL,
                reference TEXT,
                hdist REAL,
                azimuth REAL
            );
            """)
        for row in data:
            cursor.execute(
                """
                INSERT INTO ncpippn (id, specie, strata, circumference,
                                     wood_density, height, reference, hdist,
                                     azimuth)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, row + ['', '', ''])


make_ncpippn_db('csv_templates/amoss.csv', 'databases/amoss.db')

#
# letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
# for i, l in enumerate(letters):
#     for j in range(11):
#         cur.execute("""
#                     INSERT INTO reference (reference, x, y)
#                     VALUES (?, ?, ?);""",
#                     ("%s%s" % (l, j), i * 10, j * 10))
# for i in range(1, 100):
#     cur.execute("""
#                 INSERT INTO parcel (dbh, strata,
#                                     bark_thickness, wood_density)
#                 VALUES (?, ?, ?, ?);""",
#                 (None, None, None, None))
#     cur.execute("""
#                 INSERT INTO reference (id)
#                 VALUES (?);""",
#                 (i, ))
#     cur.execute("""
#                 INSERT INTO position (id)
#                 VALUES (?);""",
#                 (i, ))
# connection.commit()
