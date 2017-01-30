# coding: utf-8

import traceback

import ppygui
import sys

from gui.activities_book import ActivitiesBook


class TrupulseConfig(ppygui.Dialog):
    """
    Dialog for trupulse configuration.
    """

    TITLE = u"Connect a Trupulse laser"
    NOT_CONNECTED = u'No trupulse connected'
    CONNECTED = u'Connected on %s'
    ERROR = u'Unable to connect to %s'
    SUCCESS = u'Successfully connected to %s'
    ERROR_FONT = ppygui.Font(italic=True, color=(153, 0, 0))
    SUCCESS_FONT = ppygui.Font(italic=True, color=(0, 153, 0))

    def __init__(self, trupulse_reader=None):
        super(TrupulseConfig, self).__init__(self.TITLE)
        self.trupulse_reader = trupulse_reader
        # Create controls
        status_label = ppygui.Label(self, u'Status:')
        self.status_value = ppygui.Label(self, font=ppygui.Font(italic=True))
        status_box = ppygui.HBox()
        status_box.add(status_label)
        status_box.add(self.status_value)
        port_label = ppygui.Label(self, u'COM Port:')
        self.port_edit = ppygui.Edit(self)
        port_box = ppygui.HBox()
        port_box.add(port_label)
        port_box.add(self.port_edit)
        self.connect_button = ppygui.Button(self, u'Connect device',
                                            action=self.connect)
        self.connect_result_label = ppygui.Label(self)
        box = ppygui.VBox(border=(4, 4, 4, 4), spacing=2)
        box.add(status_box)
        box.add(port_box)
        box.add(self.connect_button)
        box.add(self.connect_result_label)
        self.sizer = box
        self.update_status()

    def connect(self, event):
        com = self.port_edit.text
        try:
            self.trupulse_reader.connect(com)
            self.connect_result_label.font = self.SUCCESS_FONT
            self.connect_result_label.text = self.SUCCESS % (com, )
        except:
            self.connect_result_label.font = self.ERROR_FONT
            self.connect_result_label.text = self.ERROR % (com, )
            print('-' * 60)
            traceback.print_exc(file=sys.stdout)
            print('-' * 60)
        self.update_status()

    def update_status(self):
        if self.trupulse_reader.is_connected():
            port = self.trupulse_reader.current_port()
            t = self.CONNECTED % (port, )
            self.status_value.text = t
        else:
            self.status_value.text = self.NOT_CONNECTED


class MainFrame(ppygui.CeFrame):
    """
    Main frame of the GUI.
    """

    ABOUT_TITLE = u'About Easy-Plot'
    ABOUT_TEXT = u'Easy-Plot makes data collection easier when settling ' \
                 + u'forest parcels. Developed by the CIA (New-Caledonian ' \
                 + u'Institute of Agronomy). Love the forest.'

    def __init__(self, database_controller, trupulse_reader=None):
        super(MainFrame, self).__init__(title=u'Easy-Plot',
                                        action=(u'About', self.on_about),
                                        menu=u'Activities')
        self.trupulse_reader = trupulse_reader
        # Create controls
        self.parcel_book = ActivitiesBook(self, database_controller)
        # Fill activities menu
        self.cb_menu.append(u'Trupulse config', callback=self.trupulse_config)
        for i, tab_name in enumerate(self.parcel_book.tabs):
            self.cb_menu.append(tab_name, callback=self._menu_callback(i))
        # Place the controls
        sizer = ppygui.VBox()
        sizer.add(self.parcel_book)
        self.sizer = sizer

    def on_about(self, event):
        ppygui.Message.ok(self.ABOUT_TITLE, self.ABOUT_TEXT, 'info', self)

    def trupulse_config(self, event):
        tp_config = TrupulseConfig(self.trupulse_reader)
        tp_config.popup(self)
        self.parcel_book._onchange(None)

    def _menu_callback(self, tab_idx):
        def menu_callback(event):
            self.parcel_book.selection = tab_idx
        return menu_callback


class EasyPlotApplication(ppygui.Application):
    """
    Main application.
    """

    def __init__(self, database_controller, trupulse_reader):
        main_frame = MainFrame(database_controller, trupulse_reader)
        super(EasyPlotApplication, self).__init__(main_frame)
        main_frame.bringtofront()
