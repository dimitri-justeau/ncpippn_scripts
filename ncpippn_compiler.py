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


def get_xy(ref, dbh, hdist, azimuth, refs, plot_azimuth, north_oriented):
    """
    Compute and return the carthesian coordinates of a tree given
    a reference point, the horizontal distance between the reference
    and the tree, the azimuth of the direction from the reference
    to the tree, and the dbh of the tree.
    """
    ref_x, ref_y = refs[ref]
    # Rectified hdist with half the dbh of the tree.
    hdist_rect = hdist + 0.5 * dbh
    az = plot_azimuth if not north_oriented else 0
    phi = azimuth_to_trigo(azimuth, az)
    dx = math.cos(phi) * hdist_rect
    dy = math.sin(phi) * hdist_rect
    return ref_x + dx, ref_y + dy


def compile_data(input_database, output_csv_file, csv_delimiter, plot_azimuth, output_plot_jpg, north_oriented, relative):

    # Generate references
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

    with open(output_csv_file, 'w', newline='') as dest:
        dest_writer = csv.writer(dest, delimiter=csv_delimiter)
        for i, row in enumerate(easyplot_db_to_data_array(input_database)):
            if i == 0 or (row[0] in refs.keys() and not relative):
                continue
            d_row = [val for val in row]
            dbh = 15
            if len(row[CIRCS_IDX]) > 0:
                circs = [float(c) for c in row[CIRCS_IDX].split(';')]
                dbh = round(stem_circ_to_dbh(*circs), 1)
                d_row[DBH_IDX] = dbh
            if len(row[REF_IDX]) > 0:
                ref = d_row[REF_IDX]
                hdist = float(d_row[HDIST_IDX])
                azimuth = float(d_row[AZIMUTH_IDX])
                if relative:
                    x, y = get_xy(ref, dbh * 0.01, hdist, azimuth, rel_refs, plot_azimuth, north_oriented)
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
                    x, y = get_xy(ref, dbh * 0.01, hdist, azimuth, refs, plot_azimuth, north_oriented)
                    ldbh.append(dbh)
                    lx.append(x)
                    ly.append(y)
                    d_row[X_IDX] = x
                    d_row[Y_IDX] = y
            dest_writer.writerow(d_row)

    if output_plot_jpg:
        # Plot the results
        fig, ax = plt.subplots(figsize=(16, 16))

        ax.scatter(lx, ly, ldbh, alpha=0.4)
        if relative:
            ax.scatter(lxref_rel, lyref_rel, 50, color='y')
        ax.scatter(lxref, lyref, color='r')

        dtext = [1.5, -4]
        for i, hr in enumerate(h_refs):
            for j, vr in enumerate([str(v_refs[0]), str(v_refs[len(v_refs) - 1])]):
                r = ''.join([vr, hr])
                ax.text(refs[r][0] + dtext[j], refs[r][1] + dtext[j], r,
                        fontsize=12, color='g')

        plt.savefig(output_plot_jpg)


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
        NCPIPPN Compiler is a utility program for compiling field data from
        a NCPIPPN plot. Copyright 'Les blaireaux'.
        """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        'input_database',
        help="The input easyplot database"
    )
    parser.add_argument(
        'output_csv_file',
        help="The output file"
    )
    parser.add_argument(
        '--csv_separator',
        default=',',
        help="The separator character to use for reading and writing csv."
    )
    parser.add_argument(
        '--plot_azimuth',
        type=float,
        help="The plot azimuth"
    )
    parser.add_argument(
        '--output_plot_jpg',
        default=None,
        help="""
            If specified, NCPIPPN Compiler will generate a jpg representation
            of the plot, with the positions of the trees.
            """
    )
    parser.add_argument(
        '--north_oriented',
        type=bool,
        default=False,
        help="""
            compute the x, y coordinates in the north oriented
            coordinate system.
            """
    )
    parser.add_argument(
        '--relative',
        type=bool,
        default=False,
        help="""
            compute the x, y coordinates in the north oriented using the
            relative positioning of the references.
            """
    )

    args = parser.parse_args()

    input_database = args.input_database
    output_file = args.output_csv_file
    csv_separator = args.csv_separator
    plot_azimuth = args.plot_azimuth
    output_plot_jpg = args.output_plot_jpg
    north_oriented = args.north_oriented
    relative = args.relative

    if os.path.exists(output_file):
        b = query_yes_no("{} already exist, do you want to overwrite it?"
                         .format(output_file))
        if not b:
            print("Aborting...")
            sys.exit()

    if output_plot_jpg is not None and os.path.exists(output_plot_jpg):
        b = query_yes_no("{} already exist, do you want to overwrite it?"
                         .format(output_plot_jpg))
        if not b:
            print("Aborting...")
            sys.exit()

    compile_data(input_database, output_file, csv_separator, plot_azimuth, output_plot_jpg, north_oriented, relative)
