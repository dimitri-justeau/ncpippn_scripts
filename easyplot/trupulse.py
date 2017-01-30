# coding: utf-8

"""
Module providing a wrapper around a RS232 connection with a TruPulse Laser.
"""

import threading
import time
import traceback

import ppygui
from ppygui.w32api import *
import ceserial


MESSAGE_TYPE_IDX = 1
HV_MESSAGE = 'HV'
HT_MESSAGE = 'HT'

# Horizontal vector indexes
HD_VALUE = (2, 3)
AZ_VALUE = (4, 5)
INC_VALUE = (6, 7)
SD_VALUE = (8, 9)

# Height indexes
HT_VALUE = (2, 3)


class TruPulseValueReader(object):

    def __init__(self, timeout=None, freq=.5):
        super(TruPulseValueReader, self).__init__()
        self._timeout = timeout
        self.freq = freq
        self.received = ''
        self._serial = None
        self._hv_observers = list()
        self._ht_observers = list()
        self._hv_values = {'hd': (None, None),
                           'az': (None, None),
                           'inc': (None, None),
                           'sd': (None, None), }
        self._ht_values = {'ht': (None, None), }
        self._listening = False

    def get_hv_observers(self):
        return self._hv_observers

    def get_ht_observers(self):
        return self._ht_observers

    def _get_hv_values(self):
        return self._hv_values

    def _get_ht_values(self):
        return self._ht_values

    hv_observers = property(get_hv_observers)
    ht_observers = property(get_ht_observers)
    hv_values = property(_get_hv_values)
    ht_values = property(_get_ht_values)

    def notify_hv_observers(self):
        for o in self.hv_observers:
            o.notify()

    def notify_ht_observers(self):
        for o in self.ht_observers:
            o.notify()

    def connect(self, com_port):
        if self._serial is not None:
            self._serial.close()
        if com_port is not None:
            try:
                self._serial = ceserial.Serial(port=com_port,
                                               baudrate=4800,
                                               timeout=self._timeout)
                self._serial.open()
                print("Connection ready - %s" % (self._serial.port, ))
            except:
                self._serial = None
                raise
        else:
            self._serial = None

    def is_connected(self):
        return self._serial is not None

    def current_port(self):
        if self.is_connected():
            return self._serial.port
        else:
            return None

    def is_listening(self):
        return self._listening

    def start_listening(self):
        if self._serial is not None:
            self._listening = True
            listening_thread = threading.Thread(target=self._listen)
            listening_thread.start()

    def stop_listening(self):
        self._listening = False

    def _listen(self):
        self.received = ''
        # Wait until data start being received
        err_count = 0
        while self._listening:
            if err_count > 10:
                self.stop_listening()
                err_popup = TrupulseConnectErroDial()
                err_popup.popup()
            try:
                time.sleep(self.freq)
                self.received = self._serial.readline().decode("utf-8").rstrip()
                if len(self.received) <= 0:
                    continue
                values = self.received.split(',')
                if values[MESSAGE_TYPE_IDX] == HV_MESSAGE:
                    self.update_hv(values)
                    windll.coredll.MessageBeep(MB_OK)
                    err_count = 0
                elif values[MESSAGE_TYPE_IDX] == HT_MESSAGE:
                    self.update_ht(values)
                    windll.coredll.MessageBeep(MB_OK)
                    err_count = 0
                else:
                    print('-' * 60)
                    print(u'Unknown message type - %s' % (values, ))
                    print('-' * 60)
                    windll.coredll.MessageBeep(MB_ICONEXCLAMATION)
            except:
                print('-' * 60)
                traceback.print_exc()
                print(u'Error reading the message - %s' % (values, ))
                print('-' * 60)
                windll.coredll.MessageBeep(MB_ICONEXCLAMATION)
                err_count += 1


    def update_hv(self, vals):
        try:
            self.hv_values['hd'] = (vals[HD_VALUE[0]], vals[HD_VALUE[1]])
            self.hv_values['az'] = (vals[AZ_VALUE[0]], vals[AZ_VALUE[1]])
            self.hv_values['inc'] = (vals[INC_VALUE[0]], vals[INC_VALUE[1]])
            self.hv_values['sd'] = (vals[SD_VALUE[0]], vals[SD_VALUE[1]])
            self.notify_hv_observers()
        except:
            print('-' * 60)
            traceback.print_exc()
            print(u'Error reading the message %s' % (vals, ))
            print('-' * 60)

    def update_ht(self, vals):
        try:
            self.ht_values['ht'] = (vals[HT_VALUE[0]], vals[HT_VALUE[1]])
            self.notify_ht_observers()
        except:
            print('-' * 60)
            traceback.print_exc()
            print(u'Error reading the message %s' % (vals, ))
            print('-' * 60)


class TrupulseConnectErroDial(ppygui.Dialog):

    def __init__(self):
        super(TrupulseConnectErroDial, self).__init__("Erreur de connection au laser")
        label = ppygui.Label(self, u'La connection avec le Trupulse a été perdue.')
        box = ppygui.VBox()
        box.add(label)
        self.sizer = box
