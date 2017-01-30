# coding: utf-8

import ppygui

from gui.widgets import EasyEdit, EasyCombo, MemoizeCombo, EasyCheckbox, \
    FloatEdit, FloatArrayEdit
import controller.field_controller as f_c


BORDER_LEFT = 4
BORDER_TOP = 4
BORDER_RIGHT = 4
BORDER_BOTTOM = 4
BORDER = (BORDER_LEFT, BORDER_TOP, BORDER_RIGHT, BORDER_BOTTOM)
SPACING = 2

BUTTON_FONT = ppygui.Font()
LABEL_FONT = ppygui.Font(bold=True)
TINY_LABEL_FONT = ppygui.Font(bold=True, size=8)
EDIT_FONT = ppygui.Font(size=8)
COMBO_FONT = ppygui.Font(size=9)
VALUE_FONT = ppygui.Font(italic=True)


def move_edit_cursor_to_end(edit):
    n = len(edit.text)
    edit.selection = n, n


def fill_combo(int_enum_field, combo):
    for i in int_enum_field.enum_values:
        combo.append(i)


WIDGETS = {
    f_c.TextField: (EasyEdit,
                    {},
                    None),
    f_c.IntegerField: (EasyEdit,
                       {'style': 'number', 'font': EDIT_FONT},
                       None),
    f_c.FloatField: (FloatEdit,
                     {'font': EDIT_FONT},
                     None),
    f_c.FloatArrayField: (FloatArrayEdit,
                          {'font': EDIT_FONT},
                          None),
    f_c.BooleanField: (EasyCheckbox,
                       {'font': EDIT_FONT},
                       None),
    f_c.EnumField: (MemoizeCombo,
                    {'style': 'list', 'font': COMBO_FONT},
                    fill_combo),
    f_c.IntegerEnumField: (EasyCombo,
                           {'style': 'list', 'font': COMBO_FONT},
                           fill_combo),
    f_c.TrupulseHDistField: (EasyEdit,
                             {'font': EDIT_FONT, 'readonly': True, },
                             None),
    f_c.TrupulseAzimuthField: (EasyEdit,
                               {'font': EDIT_FONT, 'readonly': True, },
                               None),
    f_c.TrupulseInclinationField: (EasyEdit,
                                   {'font': EDIT_FONT, 'readonly': True, },
                                   None),
    f_c.TrupulseHeightField: (EasyEdit,
                              {'font': EDIT_FONT, 'readonly': True, },
                              None),
}


class RowEditForm(ppygui.Frame):
    """
    Base class for row edit forms.
    """

    def __init__(self, parent, field_controllers=(), manual_save=False):
        # Set bordered
        self._w32_window_style |= ppygui.w32api.WS_BORDER
        super(RowEditForm, self).__init__(parent)
        self.field_controllers = field_controllers
        self.manual_save = manual_save
        # Main box
        main_box = ppygui.HBox(border=BORDER, spacing=6)
        # Create and place controls
        self.fields_widgets = dict()
        for fc in self.field_controllers:
            fld_label = fc.label
            fld_ref = fc.column_ref
            fld_cls, fld_kwargs, fld_callback = WIDGETS[type(fc)]
            # Create field and field label
            field_label = ppygui.Label(self, fld_label, font=TINY_LABEL_FONT,
                                       align='center')
            field_widget = fld_cls(self, fc, **fld_kwargs)
            if fld_callback is not None:
                fld_callback(fc, field_widget)
            if fc.readonly:
                field_widget.set(readonly=True)
            # Keep reference
            self.fields_widgets[fld_ref] = field_widget
            # Add to main box
            box = ppygui.VBox(border=(0, 0, 0, 4), spacing=SPACING)
            box.add(field_label)
            box.add(field_widget)
            main_box.add(box)
            signal = field_widget.UPDATE_SIGNAL
            if not self.manual_save:
                callback = self._make_auto_callback(field_widget)
            else:
                callback = self._make_manual_callback(field_widget)
            field_widget.bind(**{signal: callback})
        #  Save button if manual save
        if self.manual_save:
            self.save_button = ppygui.Button(self, u'Save', font=BUTTON_FONT)
            self.save_button.bind(clicked=self.save_row)
            main_box.add(self.save_button)
        self.sizer = main_box

    def _make_auto_callback(self, field_widget):
        def callback(event):
            field_widget.on_change(event)
            if not self.parent.updating_row_edit_form:
                self.save_row(event)
            self.focus_to_first_editable()
        return callback

    def _make_manual_callback(self, field_widget):
        def callback(event):
            field_widget.on_change(event)
            self.update_save_button()
        return callback

    def save_row(self, event):
        self.parent.save_row()

    def set_values(self, values):
        for i, val in enumerate(values):
            fc = self.field_controllers[i]
            widget = self.fields_widgets[fc.column_ref]
            widget.notify(val)
            # Fix for Combo not sending signal when index is -1
            if isinstance(widget, ppygui.Combo):
                widget.on_change(None)

    def update_save_button(self):
        b = True
        for fc in self.field_controllers:
            if not fc.allow_null and (fc.value is None or fc.value == ''):
                b = False
                break
        self.save_button.enable(b)

    def focus_to_first_editable(self):
        """
        Look for the first editable field and set focus to it.
        """
        for i, fc in enumerate(self.field_controllers):
            if not fc.readonly:
                self.focus()
                widget = self.fields_widgets[fc.column_ref]
                widget.focus()
                if isinstance(widget, ppygui.Edit):
                    move_edit_cursor_to_end(widget)
                break
