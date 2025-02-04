from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
import numpy as np
import tools.gui_utility as gui_utility
import tools.gui_globals as gui_globals


class buses_ui(QtWidgets.QVBoxLayout):

    def setup(self, window):
        """Setup for buses tab"""
        self.main_window = window

        hbox = QtWidgets.QHBoxLayout()
        hbox.setAlignment(Qt.AlignLeft)

        headings = ['Bus ID', 'Type', 'Load P', 'Load Q', 'Shunt G', 'Shunt B', 'Area', 'Vm', 'Vang', 'Base kV', 'Zone',
                    'Vmax', 'Vmin']
        self.tableWidget = Buses_EditTable(window, headings=headings, alternatingRowColors=True)

        self.addLayout(hbox)
        self.addWidget(self.tableWidget)

        self.tableWidget.itemChanged.connect(self.update_data_matrix)

        self.refresh_data()
        # self.tableWidget.sortItems(0)

    def update_data_matrix(self, tableWidgetItem):
        """ Update matrix whenever table data is changed """
        lower_bound = 0.0
        upper_bound = float("inf")
        value = 0.0
        if tableWidgetItem.column() == 0:
            element = "Bus ID"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive=False,
                                         u_inclusive=False, convert_to_integer=True)
        elif tableWidgetItem.column() == 1:
            # Bus type (changes handled by combobox event)
            value = tableWidgetItem.text()
        elif tableWidgetItem.column() == 2:
            element = "Load P (MW)"
            lower_bound = -1.0 * float("inf")
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive=False,
                                         u_inclusive=False)
        elif tableWidgetItem.column() == 3:
            element = "Load Q (Mvar)"
            lower_bound = -1.0 * float("inf")
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive=False,
                                         u_inclusive=False)
        elif tableWidgetItem.column() == 4:
            lower_bound = -1.0 * float("inf")
            element = "Shunt G (pu)"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive=False,
                                         u_inclusive=False)
        elif tableWidgetItem.column() == 5:
            lower_bound = -1.0 * float("inf")
            element = "Shunt B (pu)"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive=False,
                                         u_inclusive=False)
        elif tableWidgetItem.column() == 6:
            element = "Area"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive=False,
                                         u_inclusive=False, convert_to_integer=True)
        elif tableWidgetItem.column() == 7:
            element = "Vm (pu)"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive=False,
                                         u_inclusive=False)
        elif tableWidgetItem.column() == 8:
            element = "Vang (deg)"
            upper_bound = 360.0
            lower_bound = -360.0
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive=True,
                                         u_inclusive=True)
        elif tableWidgetItem.column() == 9:
            element = "Base kV"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive=True,
                                         u_inclusive=False)
        elif tableWidgetItem.column() == 10:
            element = "Zone"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive=False,
                                         u_inclusive=False, convert_to_integer=True)
        elif tableWidgetItem.column() == 11:
            element = "Vmax (pu)"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive=False,
                                         u_inclusive=False)
        elif tableWidgetItem.column() == 12:
            element = "Vmin (pu)"
            value = gui_utility.validate(tableWidgetItem.text(), lower_bound, upper_bound, l_inclusive=False,
                                         u_inclusive=False)
        if value is not False:
            gui_globals.ppc["bus"][tableWidgetItem.row(), tableWidgetItem.column()] = value
        else:
            self.main_window.show_status_message("Bus row " + str(
                tableWidgetItem.row() + 1) + " - " + element + ": Input value '" + tableWidgetItem.text() + "' out of bounds. (" + str(
                lower_bound) + " to " + str(upper_bound) + "). Value not set.", error=True, beep=True)
            self.tableWidget.itemChanged.disconnect()
            self.refresh_data()
            self.tableWidget.itemChanged.connect(self.update_data_matrix)

    def refresh_data(self):
        """Update text fields to match global variables."""
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.fill_table(gui_globals.ppc["bus"])
        self.tableWidget.setSortingEnabled(True)


class Buses_EditTable(gui_utility.EditTable):
    """Modified version of Edit Table specifically for the Buses tab."""

    def setup(self, main_window, allowCopy=True, allowPaste=True, allowShortcut=True):
        """Set up table."""
        self.main_window = main_window

        # Add row
        addRow = QtGui.QAction('&Add Row', self)
        addRow.setStatusTip('Add Row')
        if allowShortcut:
            addRow.setShortcut('Ctrl+R')
        addRow.triggered.connect(self.addrow_fn)
        self.addAction(addRow)

        # Delete row
        delRow = QtGui.QAction('&Delete Row', self)
        delRow.setStatusTip('Delete Row')
        # if allowShortcut:
        #    delRow.setShortcut('Delete')
        delRow.triggered.connect(self.delrow_fn)
        self.addAction(delRow)

        if allowCopy:
            copyAction = QtGui.QAction('&Copy', self)
            if allowShortcut:
                copyAction.setShortcut('Ctrl+C')
            copyAction.setStatusTip('Copy')
            copyAction.triggered.connect(self.copy_fn)
            self.addAction(copyAction)

        if allowPaste:
            pasteAction = QtGui.QAction('&Paste', self)
            if allowShortcut:
                pasteAction.setShortcut('Ctrl+V')
            pasteAction.setStatusTip('Paste')
            pasteAction.triggered.connect(self.paste_fn)
            self.addAction(pasteAction)

        if allowCopy or allowPaste:
            self.setContextMenuPolicy(Qt.ActionsContextMenu)
            self.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)

    def addrow_fn(self):
        """Function for the Add Row action."""
        self.setSortingEnabled(False)
        vbus_no = np.array(gui_globals.ppc["bus"][:, 0], dtype=int)

        bus_no = max(vbus_no) + 1
        self.main_window.show_status_message("Adding row: " + str(bus_no))

        new_row = np.array([bus_no, 1, 0.0, 0.0, 0.0, 0.0, 1, 1.0, 0.0, 132.0, 1, 1.1, 0.9])
        gui_globals.ppc["bus"] = np.vstack([gui_globals.ppc["bus"], new_row])
        self.fill_table(gui_globals.ppc["bus"])
        self.setSortingEnabled(True)

    def delrow_fn(self):
        """Function for the Delete Row action."""
        gui_globals.ppc["bus"] = np.delete(gui_globals.ppc["bus"], self.currentRow(), 0)
        self.fill_table(gui_globals.ppc["bus"])

    def fill_table(self, data, readOnly=False):
        """Fill table from 2D list or numpy array."""
        if len(data) > 0:
            if isinstance(data, np.ndarray):
                data = data.tolist()
            data_rows = len(data)
            data_columns = len(data[0])
            if data_columns > 0:
                self.setRowCount(data_rows)
                self.setColumnCount(data_columns)
                for r in range(0, data_rows):
                    for c in range(0, data_columns):
                        item = QtWidgets.QTableWidgetItem()
                        item.setTextAlignment(Qt.AlignHCenter)
                        if c == 0:
                            item.setText(str(int(data[r][c])))
                        else:
                            item.setText(str(data[r][c]))

                        if readOnly:
                            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

                        self.setItem(r, c, item)

                        # Column 2 is a QComboBox to select bus type
                        bus_type = QtWidgets.QComboBox()
                        bus_type.addItems(["SW", "PQ", "PV"])

                        if data[r][1] == 3:
                            combo_index = 0
                        elif data[r][1] == 1:
                            combo_index = 1
                        else:
                            combo_index = 2
                        bus_type.setCurrentIndex(combo_index)
                        bus_type.currentIndexChanged.connect(self.bustype_signal(bus_type, r, 1))
                        self.setCellWidget(r, 1, bus_type)

    def bustype_signal(self, bus_type, r, c):
        """Function will update bus type in gui_globals.  Connect to combobox index changed event."""

        def signal():
            value = bus_type.currentIndex()
            if value == 0:
                gui_globals.ppc["bus"][r, c] = 3
            elif value == 1:
                gui_globals.ppc["bus"][r, c] = 1
            else:
                gui_globals.ppc["bus"][r, c] = 2

        return signal
