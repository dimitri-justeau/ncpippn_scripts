# coding: utf-8

import ppygui

from gui.row_edit_form import RowEditForm


BORDER_LEFT = 4
BORDER_TOP = 4
BORDER_RIGHT = 4
BORDER_BOTTOM = 4
BORDER = (BORDER_LEFT, BORDER_TOP, BORDER_RIGHT, BORDER_BOTTOM)
SPACING = 2


class DataCollectionFrame(ppygui.Frame):
    """
    Base class for data collection frames.
    """

    def __init__(self, parent, table_controller, manual_save=False):
        super(DataCollectionFrame, self).__init__(parent)
        self.updating_row_edit_form = False
        self._updating_row = False
        self._selection = list()
        self.table_controller = table_controller
        self.table_controller.observers.append(self)
        field_controllers = self.table_controller.field_controllers
        self.columns = [fc.label for fc in field_controllers]
        # Create controls
        self.data_table = ppygui.Table(self, columns=self.columns)
        self.row_edit_form = RowEditForm(self, field_controllers, manual_save)
        # Place controls
        main_box = ppygui.VBox(spacing=SPACING, border=BORDER)
        table_box = ppygui.HBox()
        table_box.add(ppygui.Spacer(x=0))
        table_box.add(self.data_table)
        main_box.add(table_box)
        main_box.add(self.row_edit_form)
        self.sizer = main_box
        self.adjust_columns_to_headers()
        for row in self.table_controller.get_rows():
            self.data_table.rows.append([field_controllers[i].to_str(value=v)
                                         if v is not None else ''
                                         for i, v in enumerate(row)])
        self.row_edit_form.enable(False)
        self.data_table.bind(selchanged=self.selection_changed)
        self.data_table.bind(focus=self.focus_to_edit)

    def selection_changed(self, event):
        if self._updating_row:
            return
        selection = self.data_table.rows.selection
        if selection != self._selection:
            self._selection = selection
            self.focus()
        if self.data_table.rows.selected_count > 0:
            self.updating_row_edit_form = True
            self.row_edit_form.enable(True)
            row_idx = selection[0]
            self.row_edit_form.set_values(self.data_table.rows[row_idx])
            self.updating_row_edit_form = False
        else:
            self.row_edit_form.enable(False)

    def save_row(self):
        self.table_controller.update_row()

    def update_row(self, row):
        self._updating_row = True
        row_idx = self.data_table.rows.selection[0]
        self.data_table.rows[row_idx] = [str(i) if i is not None else ''
                                         for i in row]
        self._updating_row = False
        self.selection_changed(None)

    def focus_to_edit(self, event):
        self.row_edit_form.focus_to_first_editable()

    def adjust_columns_to_headers(self):
        """
        Adjust columns width to fit headers.
        """
        self.data_table.rows.append([c + 6 * ' ' for c in self.columns])
        self.data_table.adjust_all()
        del self.data_table.rows[0]
