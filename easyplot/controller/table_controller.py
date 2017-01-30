# coding: utf-8


class TableController(object):
    """
    Table controller.
    """

    def __init__(self, db_controller, table_ref, field_controllers,
                 label=None, devices=list()):
        self.db_controller = db_controller
        self._table_ref = table_ref
        self._field_controllers = field_controllers
        self.observers = list()
        self.label = label if label is not None else self.table_ref
        self.devices = devices

    def _get_table_ref(self):
        return self._table_ref

    def _set_table_ref(self, value):
        self._table_ref = value

    def _get_field_controllers(self):
        return self._field_controllers

    def _set_field_controllers(self, value):
        self._field_controllers = value

    table_ref = property(_get_table_ref, _set_table_ref)
    field_controllers = property(_get_field_controllers,
                                 _set_field_controllers)

    def get_rows(self):
        return self.db_controller.get_table_rows(self)

    def update_row(self):
        """
        WARNING: Assume that the first element of row correspond to PK.
        """
        column_refs = list()
        row = list()
        str_row = list()
        for fc in self.field_controllers:
            column_refs.append(fc.column_ref)
            row.append(fc.value)
            str_row.append(fc.to_str())
        self.db_controller.update_table_row(self, row, column_refs)
        for o in self.observers:
            o.update_row(str_row)
