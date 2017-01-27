# coding: utf-8

import sqlite3


def generate_references():
    v_refs = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    h_refs = [str(i) for i in range(11)]
    refs = []
    ascending = True
    k = 0
    for vr in v_refs:
        iter_h_refs = h_refs if ascending else reversed(h_refs)
        for hr in iter_h_refs:
            ref = ''.join([vr, hr])
            refs.append(ref)
        k += 1
        if k >= 2:
            ascending = not ascending
            k = 0
    return refs


def generate_easyplot_dabatase(database_path, start_id, end_id):
    refs = ["('{}')".format(i) for i in generate_references()]
    vals = ["('{}')".format(i) for i in range(start_id, end_id + 1)]
    sql = \
        """
        DROP TABLE IF EXISTS ncpippn;
        CREATE TABLE ncpippn (
            id TEXT PRIMARY KEY,
            quadrat TEXT,
            strata INTEGER,
            circumferences REAL,
            dbh REAL,
            height REAL,
            reference TEXT,
            hdist REAL,
            azimuth REAL,
            x REAL,
            y REAL
        );
        /* First insert references */
        INSERT INTO ncpippn (id) VALUES {};
        /* Insert identifiers */
        INSERT INTO ncpippn (id) VALUES {};
        """.format(','.join(refs), ','.join(vals))
    connexion = sqlite3.connect(database_path)
    cursor = connexion.cursor()
    cursor.executescript(sql)


if __name__ == '__main__':

    import sys
    import os
    import argparse


    def query_yes_no(question, default="yes"):
        """Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is True for "yes" or False for "no".
        """
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            sys.stdout.write(question + prompt)
            choice = input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' "
                                 "(or 'y' or 'n').\n")

    description = \
        """
        Easyplot Generator generates a database and a launcher script for
        collecting field data with Easyplot.
        """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        'database_path',
        help="The output path of the database to generate."
    )
    parser.add_argument(
        'start_id',
        type=int,
        help="The starting id of the database to generate."
    )
    parser.add_argument(
        'end_id',
        type=int,
        help="The ending id of the database to generate."
    )

    args = parser.parse_args()
    database_path = args.database_path
    start_id = args.start_id
    end_id = args.end_id

    if os.path.exists(database_path):
        b = query_yes_no("{} already exist, do you want to overwrite it?"
                         .format(database_path))
        if not b:
            print("Aborting...")
            sys.exit()

    generate_easyplot_dabatase(database_path, start_id, end_id)
