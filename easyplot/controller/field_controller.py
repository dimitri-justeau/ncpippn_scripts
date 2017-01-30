# coding: utf-8


class FieldController(object):
    """
    Abstract base class for field controller.
    """

    def __init__(self, column_ref, python_type=object, allow_null=True,
                 label=None, readonly=False, device=None):
        self._column_ref = column_ref
        self._python_type = python_type
        self._value = None
        self.observers = list()
        # Not used internally, it is just an indication for the GUI
        self.allow_null = allow_null
        self.readonly = readonly
        self.device = device
        self.label = label if label is not None else column_ref
        if type(self) == FieldController:
            m = u"FieldController is abstract and should not be instantiated."
            raise NotImplementedError(m)

    def _get_column_ref(self):
        return self._column_ref

    def _set_column_ref(self, value):
        self._column_ref = value

    def _get_python_type(self):
        return self._python_type

    def _get_value(self):
        return self._value

    def _set_value(self, value):
        self.validate(value)
        self._value = value

    column_ref = property(_get_column_ref, _set_column_ref)
    python_type = property(_get_python_type)
    value = property(_get_value, _set_value)

    def update(self, sources, value):
        self.value = value
        self.notify_observers(sources)

    def notify_observers(self, exclude):
        for o in self.observers:
            if o not in exclude:
                o.notify(self.value)

    def to_str(self, value=None):
        val = value
        if val is None:
            val = self.value
        if val is None:
            return ''
        else:
            return str(val)

    @staticmethod
    def from_str(value):
        if value is None or value == 'None':
            return None
        return value

    def validate(self, value):
        # Not really used at the moment
        if value is None:
            return
        if not isinstance(value, self.python_type):
            m = u'%d type (%d) is incorrect (should be a subclass of %d).' \
                % (value, type(value), self.python_type)
            raise TypeError(m)


class IntegerField(FieldController):
    """
    Controller for integer field.
    """

    def __init__(self, column_reference, allow_null=True, label=None,
                 readonly=False, device=None):
        super(IntegerField, self).__init__(column_reference,
                                           python_type=int,
                                           allow_null=allow_null,
                                           label=label,
                                           readonly=readonly,
                                           device=device)

    @staticmethod
    def from_str(value):
        if value is None or value == 'None' or value == '':
            return None
        return int(value)


class FloatField(FieldController):
    """
    Controller for float field.
    """

    def __init__(self, column_reference, allow_null=True, label=None,
                 readonly=False, device=None):
        super(FloatField, self).__init__(column_reference,
                                         python_type=float,
                                         allow_null=allow_null,
                                         label=label,
                                         readonly=readonly,
                                         device=device)

    @staticmethod
    def from_str(value):
        if value is None or value == 'None' or value == '':
            return None
        return value

    def validate(self, value):
        # Not really used at the moment
        if value is None:
            return
        float(value)
        return


class FloatArrayField(FieldController):
    """
    Controller for float array field.
    """

    def __init__(self, column_reference, allow_null=True, label=None,
                 readonly=False, device=None):
        super(FloatArrayField, self).__init__(column_reference,
                                              python_type=unicode,
                                              allow_null=allow_null,
                                              label=label,
                                              readonly=readonly,
                                              device=device)

    @staticmethod
    def from_str(value):
        if value is None or value == 'None' or value == '':
            return None
        return value

    def validate(self, value):
        # Not really used at the moment
        if value is None:
            return
        return


class TextField(FieldController):
    """
    Controller for text field.
    """

    def __init__(self, column_reference, allow_null=True, label=None,
                 readonly=False, device=None):
        super(TextField, self).__init__(column_reference,
                                        python_type=unicode,
                                        allow_null=allow_null,
                                        label=label,
                                        readonly=readonly,
                                        device=device)


class BooleanField(FieldController):
    """
    Controller for a boolean field.
    """

    def __init__(self, column_reference, true_label='True',
                 false_label='False', allow_null=True, label=None,
                 readonly=False, device=None):
        super(BooleanField, self).__init__(column_reference,
                                           python_type=bool,
                                           allow_null=allow_null,
                                           label=label,
                                           readonly=readonly,
                                           device=device)
        self.true_label = true_label
        self.false_label = false_label

    def to_str(self, value=None):
        val = value
        if val is None:
            val = self.value
        if val:
            return self.true_label
        else:
            return self.false_label


class EnumField(FieldController):
    """
    Controller for values belonging to an enum.
    """

    def __init__(self, column_reference, enum_values=(), allow_null=True,
                 python_type=object, label=None, readonly=False, device=None):
        super(EnumField, self).__init__(column_reference,
                                        python_type=python_type,
                                        allow_null=allow_null,
                                        label=label,
                                        readonly=readonly,
                                        device=device)
        if not isinstance(enum_values, (tuple, list)):
            m = u"Enum values must be a tuple or a list."
            raise TypeError(m)
        self.enum_values = enum_values

    def _get_enum_values(self):
        return self._enum_values

    def _set_enum_values(self, values):
        for val in values:
            if not isinstance(val, self.python_type):
                m = u"Enum values must be of type %s." % self.python_type
                raise TypeError(m)
        self._enum_values = values

    enum_values = property(_get_enum_values, _set_enum_values)

    def validate(self, value):
        super(EnumField, self).validate(value)
        if value is None:
            return
        if value not in self.enum_values:
            m = u"%s not in %s." % (value, self.enum_values)
            raise ValueError(m)

    def current_index(self):
        return self.enum_values.index(self.value)


class IntegerEnumField(EnumField):
    """
    Controller for value belonging to an integer enum.
    """

    def __init__(self, column_reference, enum_values=(), allow_null=True,
                 label=None, readonly=False, device=None):
        super(IntegerEnumField, self).__init__(column_reference,
                                               enum_values=enum_values,
                                               allow_null=allow_null,
                                               python_type=int,
                                               label=label,
                                               readonly=readonly,
                                               device=device)

    @staticmethod
    def from_str(value):
        return IntegerField.from_str(value)


class TrupulseField(FieldController):
    """
    Abstract base class for field controller linked to a trupulse laser.
    A TrupulseField is an observer of a TrupulseValueReader.
    """

    OBSERVER_TYPE = None

    def __init__(self, column_reference, trupulse_reader=None,
                 python_type=object, allow_null=True,
                 label=None, readonly=False):
        if type(self) == TrupulseField:
            m = u"TrupulseEdit is abstract and should not be instantiated."
            raise NotImplementedError(m)
        super(TrupulseField, self).__init__(column_reference,
                                            python_type=python_type,
                                            allow_null=allow_null,
                                            readonly=readonly,
                                            label=label,
                                            device='trupulse')
        self._trupulse_reader = trupulse_reader
        self.register_to_trupulse()

    def _get_trupulse_reader(self):
        return self._trupulse_reader

    def _set_trupulse_reader(self, value):
        self._trupulse_reader = value
        self.register_to_trupulse()

    def register_to_trupulse(self):
        if self._trupulse_reader is not None:
            if self.OBSERVER_TYPE == 'HV':
                self._trupulse_reader.hv_observers.append(self)
            elif self.OBSERVER_TYPE == 'HT':
                self._trupulse_reader.ht_observers.append(self)

    trupulse_reader = property(_get_trupulse_reader, _set_trupulse_reader)

    def notify(self):
        raise NotImplementedError()


class TrupulseHDistField(TrupulseField):

    OBSERVER_TYPE = 'HV'

    def notify(self):
        self.update((self.trupulse_reader, ),
                    self.trupulse_reader.hv_values['hd'][0])


class TrupulseAzimuthField(TrupulseField):

    OBSERVER_TYPE = 'HV'

    def notify(self):
        self.update((self.trupulse_reader, ),
                    self.trupulse_reader.hv_values['az'][0])


class TrupulseInclinationField(TrupulseField):

    OBSERVER_TYPE = 'HV'

    def notify(self):
        self.update((self.trupulse_reader, ),
                    self.trupulse_reader.hv_values['inc'][0])


class TrupulseHeightField(TrupulseField):

    OBSERVER_TYPE = 'HT'

    def notify(self):
        self.update((self.trupulse_reader, ),
                    self.trupulse_reader.ht_values['ht'][0])
