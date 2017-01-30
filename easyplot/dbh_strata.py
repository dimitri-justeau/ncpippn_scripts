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
             fld_ctrl.IntegerField(u'id', label=u'id', readonly=True),
             fld_ctrl.FloatArrayField(u'circumferences', label=u'circ.'),
             fld_ctrl.IntegerEnumField(u'strata', label=u'strata',
                                       enum_values=range(5)),
             fld_ctrl.EnumField(u'quadrat', label=u'quadrat',
                                enum_values=quadrats)
         ],
         {'label': u"DBH/Strata/Quadrat", }
         ),
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
