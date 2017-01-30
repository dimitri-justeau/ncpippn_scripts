# coding: utf-8

import sqlite3


class DatabaseController(object):
    """
    Database controller.
    """

    def __init__(self, db_path, table_controllers=()):
        self.db_path = db_path
        self.table_controllers = table_controllers
        # Connect to database
        self.connection = sqlite3.connect(self.db_path)

    def get_table_rows(self, tb_ctrl):
        c = self.connection.cursor()
        columns = [fld.column_ref for fld in tb_ctrl.field_controllers]
        try:
            c.execute("SELECT %s FROM %s;"
                      % (','.join(columns), tb_ctrl.table_ref))
            return c.fetchall()
        except:
            c.close()
            self.connection.rollback()
            raise

    def update_table_row(self, tb_ctrl, row, column_refs):
        """
        WARNING: Assume that the first element of row correspond to PK.
        """
        c = self.connection.cursor()
        try:
            rvals = [r if r is not None else '' for r in row]
            updates = list()
            for i in range(1, len(row)):
                updates.append("%s = '%s'" % (column_refs[i], rvals[i]))
            query = "UPDATE %s SET %s WHERE %s = '%s';" \
                    % (tb_ctrl.table_ref, ','.join(updates),
                       column_refs[0], row[0])
            c.execute(query)
            self.connection.commit()
        except:
            c.close()
            self.connection.rollback()
            raise
