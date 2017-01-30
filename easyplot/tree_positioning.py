# coding: utf-8

if __name__ == '__main__':

    import sqlite3

    import ppygui

    import gui.main_frame
    import controller.database_controller as db_ctrl
    import controller.table_controller as tb_ctrl
    import controller.field_controller as fld_ctrl
    import trupulse

    DB_PATH = ppygui.FileDialog.open(
        wildcards={"EasyPlot Database (*.epdb)": "*.epdb"}
    )

    print("Opening '%s'..." % DB_PATH)

    # Get references for positioning
    refs = list()
    quadrats = list()
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    for i, l in enumerate(letters):
        for j in range(11):
            refs.append(u"%s%s" % (l, j))
            if i < 10 and j > 0:
                quadrats.append(u"%s%s" % (l, j))
    connection = sqlite3.connect(DB_PATH)
    cur = connection.cursor()
    cur.execute("SELECT id FROM ncpippn;")
    refs += [str(r[0]) for r in cur.fetchall()]
    connection.close()

    # Instantiate Trupulse
    trupulse = trupulse.TruPulseValueReader()

    APP = [
        (u'ncpippn',
         [
             fld_ctrl.IntegerField(u'id',
                                   label=u'id',
                                   readonly=True),
             fld_ctrl.TextField(u'quadrat',
                                label=u'quadrat',
                                readonly=True),
             fld_ctrl.EnumField(u'reference',
                                label=u'ref.',
                                enum_values=refs,
                                allow_null=False),
             fld_ctrl.TrupulseHDistField(u'hdist',
                                         label=u'hdist',
                                         trupulse_reader=trupulse,
                                         allow_null=False,
                                         readonly=True),
             fld_ctrl.TrupulseAzimuthField(u'azimuth',
                                           label=u'azimuth',
                                           trupulse_reader=trupulse,
                                           allow_null=False,
                                           readonly=True),
         ],
         {'label': u"Tree positioning",
          'devices': (trupulse, ), }),
    ]

    db_controller = db_ctrl.DatabaseController(DB_PATH)

    t_controllers = [tb_ctrl.TableController(db_controller, tb[0], tb[1],
                                             **tb[2])
                     for tb in APP]

    db_controller.table_controllers = t_controllers

    print(u'Loading data...')
    app = gui.main_frame.EasyPlotApplication(db_controller, trupulse)
    print(u'Ok!')
    app.run()
