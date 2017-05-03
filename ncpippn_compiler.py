#!/usr/bin/python
# coding: utf-8

import math
import csv
import sqlite3

import matplotlib.pyplot as plt


# IDX
ID_IDX = 0
CIRCS_IDX = 3
DBH_IDX = 4
HEIGHT_IDX = 5
REF_IDX = 6
HDIST_IDX = 7
AZIMUTH_IDX = 8
X_IDX = 9
Y_IDX = 10


def easyplot_db_to_data_array(database_path):
    c = sqlite3.connect(database_path)
    cur = c.cursor()
    cur.execute("SELECT * FROM ncpippn;")
    data = cur.fetchall()
    c.close()
    return data


def get_row_from_easyplot_db(database_path, row_id):
    c = sqlite3.connect(database_path)
    cur = c.cursor()
    cur.execute("SELECT * FROM ncpippn WHERE ncpippn.id = '{}';"
                .format(row_id))
    data = cur.fetchone()
    c.close()
    return data


def stem_circ_to_dbh(*stems):
    """
    Given a list of stem circumferences values, compute and return
    an equivalent dbh value.
    """
    total_area = 0
    for stem in stems:
        r = stem / (2 * math.pi)
        a = math.pi * r**2
        total_area += a
    return 2 * math.sqrt(total_area / math.pi)


def azimuth_to_trigo(azimuth, plot_azimuth):
    """
    Convert an azimuth in degrees to a radian trigonometric angle.
    """
    h = 450 - azimuth + plot_azimuth
    return math.radians(h) if h < 180 else math.radians(h - 360)


def resolve_ref(ref, refs, input_database, plot_azimuth, north_oriented):
    if ref in refs:
        return refs[ref]
    try:
        row = get_row_from_easyplot_db(input_database, ref)
    except:
        raise ValueError(
            "The reference '{}' does not exist in database.".format(ref)
        )
    ref_ref = row[REF_IDX]
    if ref_ref is None:
        raise ValueError(
            "The reference '{}' had not been positioned.".format(ref)
        )
    ref_hdist = row[HDIST_IDX]
    ref_dbh = row[DBH_IDX]
    if ref_dbh is None:
        ref_dbh = 0
    ref_azimuth = row[AZIMUTH_IDX]
    return get_xy(ref_ref, ref_dbh, ref_hdist, ref_azimuth, refs,
                  plot_azimuth, north_oriented, input_database)


def get_xy(ref, dbh, hdist, azimuth, refs, plot_azimuth, north_oriented,
           input_database):
    """
    Compute and return the carthesian coordinates of a tree given
    a reference point, the horizontal distance between the reference
    and the tree, the azimuth of the direction from the reference
    to the tree, and the dbh of the tree.
    """
    ref_x, ref_y = resolve_ref(ref, refs, input_database, plot_azimuth,
                               north_oriented)
    # Rectified hdist with half the dbh of the tree.
    hdist_rect = hdist + 0.5 * dbh
    az = plot_azimuth if not north_oriented else 0
    phi = azimuth_to_trigo(azimuth, az)
    dx = math.cos(phi) * hdist_rect
    dy = math.sin(phi) * hdist_rect
    return ref_x + dx, ref_y + dy


def compile_data(input_database, output_csv_file, csv_delimiter, plot_azimuth,
                 output_plot_png, north_oriented, relative,
                 letters_abscissa=False):

    # Generate references
    if letters_abscissa:
        h_refs = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
        v_refs = [str(i) for i in range(11)]
    else:
        v_refs = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
        h_refs = [str(i) for i in range(11)]
    refs = {}
    rel_refs = {'A0': (0, 0)}
    lxref = []
    lyref = []
    lxref_rel = []
    lyref_rel = []
    ldbh = []
    lx = []
    ly = []

    theta = math.radians(360 - plot_azimuth)

    for i, hr in enumerate(h_refs):
        for j, vr in enumerate(v_refs):
            if letters_abscissa:
                r = ''.join([hr, vr])
            else:
                r = ''.join([vr, hr])
            # Coordinates of the reference in the plot referential
            x1 = i * 10
            y1 = j * 10
            # Coordinates of the reference in the north oriented referential,
            # with the same origin as the plot referential.
            x2 = x1 * math.cos(theta) - y1 * math.sin(theta)
            y2 = x1 * math.sin(theta) + y1 * math.cos(theta)
            if north_oriented:
                refs[r] = (x2, y2)
                lxref.append(x2)
                lyref.append(y2)
            else:
                refs[r] = (x1, y1)
                lxref.append(x1)
                lyref.append(y1)

    data = easyplot_db_to_data_array(input_database)

    with open(output_csv_file, 'w') as dest:
        dest_writer = csv.writer(dest, delimiter=csv_delimiter)
        for i, row in enumerate(data):
            if i == 0 or (row[0] in refs.keys() and not relative):
                continue
            d_row = [val for val in row]
            dbh = 15
            if row[CIRCS_IDX]:
                circs = [float(c) for c in row[CIRCS_IDX].split(';')]
                dbh = round(stem_circ_to_dbh(*circs), 1)
                d_row[DBH_IDX] = dbh
            if row[REF_IDX]:
                ref = d_row[REF_IDX]
                hdist = float(d_row[HDIST_IDX])
                azimuth = float(d_row[AZIMUTH_IDX])
                if relative:
                    x, y = get_xy(ref, dbh * 0.01, hdist, azimuth, rel_refs,
                                  plot_azimuth, north_oriented, input_database)
                    rel_refs[row[ID_IDX]] = (x, y)
                    ldbh.append(dbh)
                    lx.append(x)
                    ly.append(y)
                    d_row[X_IDX] = x
                    d_row[Y_IDX] = y
                    if row[ID_IDX] in refs:
                        lxref_rel.append(x)
                        lyref_rel.append(y)
                else:
                    x, y = get_xy(ref, dbh * 0.01, hdist, azimuth, refs,
                                  plot_azimuth, north_oriented, input_database)
                    ldbh.append(dbh)
                    lx.append(x)
                    ly.append(y)
                    d_row[X_IDX] = x
                    d_row[Y_IDX] = y
            dest_writer.writerow(d_row)

    if output_plot_png:
        # Plot the results
        fig, ax = plt.subplots(figsize=(16, 16))

        ax.scatter(lx, ly, ldbh, alpha=0.4)
        if relative:
            ax.scatter(lxref_rel, lyref_rel, 50, color='y')
        ax.scatter(lxref, lyref, color='r')

        dtext = [1.5, -4]
        for i, hr in enumerate(h_refs):
            for j, vr in enumerate([str(v_refs[0]), str(v_refs[len(v_refs) - 1])]):
                if letters_abscissa:
                    r = ''.join([hr, vr])
                else:
                    r = ''.join([vr, hr])
                ax.text(refs[r][0] + dtext[j], refs[r][1] + dtext[j], r,
                        fontsize=12, color='g')

        plt.savefig(output_plot_png, format='png')


if __name__ == '__main__':

    import sys
    import os
    import argparse


    def str2bool(v):
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        if v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')


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
            # For python2/3 compatibility
            input = __builtins__.input
            if hasattr(__builtins__, 'raw_input'):
                input = raw_input
            choice = input(question + prompt).lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' "
                                 "(or 'y' or 'n').\n")

    description = \
        """
        NCPIPPN Compiler is a utility program for compiling field data from
        a NCPIPPN plot. By default, compute the positions in the plot oriented
        coordinate system. it computes Copyright 'Les blaireaux'.
        """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        'plot_azimuth',
        type=float,
        help="The plot azimuth (float)"
    )
    parser.add_argument(
        'input_database',
        help="The input easyplot database (.epdb)"
    )
    parser.add_argument(
        'output_csv_file',
        help="The output file"
    )
    parser.add_argument(
        '--csv_separator',
        default=',',
        help="The separator character to use for writing the output csv file"
    )
    parser.add_argument(
        '--output_plot_png',
        default=None,
        help="""
            If specified, NCPIPPN Compiler will generate a png representation
            of the plot, with the positions of the trees.
            """
    )
    parser.add_argument(
        '--north_oriented',
        type=str2bool,
        default=False,
        help="""
            Compute the x, y coordinates in the north oriented
            coordinate system (boolean: True/False).
            """
    )
    parser.add_argument(
        '--relative',
        type=str2bool,
        default=False,
        help="""
            Compute the x, y coordinates in the north oriented using the
            relative positioning of the references (boolean: True/False).
            """
    )
    parser.add_argument(
        '--letters_abscissa',
        type=str2bool,
        default=False,
        help="""
            If True, A0 -> K0 is considered as the abscissa. Else, A0 -> A10
            is considered as the abscissa. (boolean: True/False).
            """
    )

    args = parser.parse_args()

    input_database = args.input_database
    output_file = args.output_csv_file
    csv_separator = args.csv_separator
    plot_azimuth = args.plot_azimuth
    output_plot_png = args.output_plot_png
    north_oriented = args.north_oriented
    relative = args.relative
    letters_abscissa = bool(args.letters_abscissa)

    if os.path.exists(output_file):
        b = query_yes_no("{} already exist, do you want to overwrite it?".format(output_file))
        if not b:
            print("Aborting...")
            sys.exit()

    if output_plot_png is not None and os.path.exists(output_plot_png):
        b = query_yes_no("{} already exist, do you want to overwrite it?"\
                         .format(output_plot_png))
        if not b:
            print("Aborting...")
            sys.exit()

    compile_data(input_database, output_file, csv_separator, plot_azimuth,
                 output_plot_png, north_oriented, relative,
                 letters_abscissa=letters_abscissa)
