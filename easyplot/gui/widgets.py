# coding: utf-8

"""
Widgets extending PyPocketGUI to enable connection with field controllers.
"""

import ppygui


class EasyWidget(object):
    """
    Abstract base class for widgets. The only requirement is
    """

    UPDATE_SIGNAL = None

    def __init__(self, field_controller):
        self.field_controller = field_controller
        self.field_controller.observers.append(self)
        if type(self) == EasyWidget:
            raise NotImplementedError()
        self.bind(**{self.UPDATE_SIGNAL: self.on_change})

    def notify(self, value):
        raise NotImplementedError()

    def on_change(self, event):
        # TODO convert from str inside the field controller
        value = self.field_controller.from_str(self.text)
        if value == '':
            value = None
        self.field_controller.update((self, ), value)


class EasyEdit(EasyWidget, ppygui.Edit):

    UPDATE_SIGNAL = 'update'

    def __init__(self, parent, field_controller, **kwargs):
        ppygui.Edit.__init__(self, parent, **kwargs)
        EasyWidget.__init__(self, field_controller)

    def notify(self, value):
        txt = ''
        if value is not None:
            txt = str(value)
        self.set_text(txt)


class FloatEdit(EasyEdit):

    def __init__(self, parent, field_controller, **kwargs):
        kwargs['style'] = 'normal'
        super(FloatEdit, self).__init__(parent, field_controller, **kwargs)
        self.last_text = self.text
        self.float_value = None
        self._restoring = False
        try:
            self.float_value = float(self.text)
        except:
            self.float_value = None

    def on_change(self, event):
        if len(self.text) > 0:
            try:
                n_float_value = float(self.text)
                self.float_value = n_float_value
                self.last_text = self.text
                super(FloatEdit, self).on_change(event)
            except:
                self.set_text(self.last_text)
        else:
            self.last_text = self.text
            super(FloatEdit, self).on_change(event)


class FloatArrayEdit(EasyEdit):

    def __init__(self, parent, field_controller, **kwargs):
        kwargs['style'] = 'normal'
        super(FloatArrayEdit, self).__init__(parent, field_controller, **kwargs)
        self.last_text = self.text
        self.array_values = None
        self._restoring = False
        try:
            self.array_values = self.text.split(";")
            for i, v in enumerate(self.array_values):
                if i == len(self.array_values) - 1 and v == '':
                    continue
                float(v)
        except:
            self.array_values = None

    def on_change(self, event):
        if len(self.text) > 0:
            try:
                n_array_values = self.text.split(";")
                for i, v in enumerate(n_array_values):
                    if i == len(n_array_values) - 1 and v == '':
                        continue
                    float(v)
                self.array_values = n_array_values
                self.last_text = self.text
                super(FloatArrayEdit, self).on_change(event)
            except:
                self.set_text(self.last_text)
        else:
            self.last_text = self.text
            super(FloatArrayEdit, self).on_change(event)


class EasyCombo(EasyWidget, ppygui.Combo):

    UPDATE_SIGNAL = 'selchanged'

    def __init__(self, parent, field_controller, **kwargs):
        ppygui.Combo.__init__(self, parent, **kwargs)
        EasyWidget.__init__(self, field_controller)

    def notify(self, value):
        if value is None or value == '':
            self.set_selection(None)
        else:
            self.set_selection(self.choices.index(value))


class MemoizeCombo(EasyCombo):

    def __init__(self, parent, field_controller, **kwargs):
        super(MemoizeCombo, self).__init__(parent, field_controller, **kwargs)
        self.last_idx = None

    def on_change(self, event):
        if self.selection >= 0:
            self.last_idx = self.selection
        elif self.last_idx is not None:
            self.set_selection(self.last_idx)
        super(MemoizeCombo, self).on_change(event)


class EasyCheckbox(EasyWidget, ppygui.Button):

    UPDATE_SIGNAL = 'clicked'

    def __init__(self, parent, field_controller, **kwargs):
        ppygui.Button.__init__(self, parent, style='check', **kwargs)
        EasyWidget.__init__(self, field_controller)

    def on_change(self, event):
        value = self.checked
        self.field_controller.update((self, ), value)

    def notify(self, value):
        self.set_checked(value)
