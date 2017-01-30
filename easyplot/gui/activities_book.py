# coding: utf-8

import ppygui

from gui.data_collection_frame import DataCollectionFrame


class ActivitiesBook(ppygui.NoteBook):
    """
    Notebook with tabs. To each tab correspond a step in the forest parcel
    settling and data collection.
    """

    def __init__(self, parent, database_controller):
        super(ActivitiesBook, self).__init__(parent)
        self._initializing = True
        self.database_controller = database_controller
        self.tabs = list()
        self._running_devices = list()
        # append tabs
        for tc in self.database_controller.table_controllers:
            manual_save = False
            if len(tc.devices) > 0:
                manual_save = True
            tab = DataCollectionFrame(self, tc, manual_save=manual_save)
            self.tabs.append(tc.label)
            self.append(tc.label, tab)
        # Set current tab selection to 0
        self._initializing = False
        self.selection = 0

    def _onchange(self, event):
        super(ActivitiesBook, self)._onchange(event)
        if not self._initializing:
            tab = self[self.selection]
            tb_ctrl = tab.table_controller
            for device in self._running_devices:
                device.stop_listening()
            self._running_devices = list()
            for device in tb_ctrl.devices:
                self._running_devices.append(device)
                device.start_listening()
