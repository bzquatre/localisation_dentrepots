from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QFileDialog, QListWidget,
    QPushButton, QHBoxLayout, QVBoxLayout
)
from PyQt5.QtGui import QIcon
import sys, os
from pulp import *
import pandas as pd
import numpy as np

def resource_path(relative_path):
    """ Get the absolute path to a resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
class Windo(QWidget):
    def __init__(self):
        super().__init__()

        # ------------------------------
        # Window Settings
        # ------------------------------
        self.setWindowIcon(QIcon(resource_path('Icon.ico')))
        self.setWindowTitle("Localisation Dentrepots")
        self.setGeometry(200, 100, 1024, 600)

        # ------------------------------
        # UI Components
        # ------------------------------

        # Button to select Excel file
        self.file = QPushButton(self, text="Select")
        self.file.clicked.connect(self.getfile)

        # Status label (LP status: Optimal, Infeasible...)
        self.status = QLabel(self, text="Status:")

        # Label showing the objective function result
        self.objectivefunction = QLabel(self, text="Objective function:")

        # List to show non-zero decision variables (x and y)
        self.liste = QListWidget(self)

        # Extra buttons (unused here but available in GUI)
        self.btnghraph1 = QPushButton(text="Ghraphe Biparti")
        self.btntranv = QPushButton(text="Transvarsal Minimum")
        self.btnghraph2 = QPushButton(text="Ghraphe de Transvarsal Minimum")
        self.btnghraph2.setStyleSheet('padding: 15px 25px;')

        # Set layout
        self.setLayout(self.layout())
        self.show()


    # -----------------------------------------------------
    # Function to solve the optimization problem using PuLP
    # -----------------------------------------------------
    def solve(self, filename):
        # Load Excel file
        file = pd.ExcelFile(filename)

        # Read sheets into numpy arrays
        livraisons = np.array(pd.read_excel(file, index_col=0, sheet_name=0))
        entrepots   = np.array(pd.read_excel(file, index_col=0, sheet_name=1))
        centrales   = np.array(pd.read_excel(file, index_col=0, sheet_name=2))

        # -------------------------------------
        # Create index sets for variables
        # -------------------------------------
        var_y_keys = [i for i in range(1, 13)]                    # y[1..12]
        var_x_keys = [(i, j) for i in range(1, 13)                # x[i,j]
                                for j in range(1, 13)]

        # -------------------------------------
        # Decision Variables
        # -------------------------------------
        y = LpVariable.dicts('y', var_y_keys, cat='Binary')       # Warehouse open/close
        x = LpVariable.dicts('x', var_x_keys, lowBound=0,
                             cat='Integer')                       # Quantities transported

        # -------------------------------------
        # Define the LP problem (Minimization)
        # -------------------------------------
        prob = LpProblem("Localisation_dentrepots", LpMinimize)

        # -------------------------------------
        # Objective Function
        # cost = opening_costs(y) + transport_costs(x)
        # -------------------------------------

        # Extract coefficients for y and x from Excel
        coeff_y = [entrepots[0][i] for i in range(12)]
        coeff_x = [livraisons[i][j] for i in range(12) for j in range(12)]

        coeff_x_dict = dict(zip(var_x_keys, coeff_x))
        coeff_y_dict = dict(zip(var_y_keys, coeff_y))

        prob += (
            lpSum(coeff_y_dict[i] * y[i] for i in var_y_keys)
            + lpSum(coeff_x_dict[i] * x[i] for i in var_x_keys)
        )

        # -------------------------------------
        # Constraints
        # -------------------------------------

        # 1) Demand constraints: sum of x over warehouses = central demand
        for j in range(1, 13):
            prob += lpSum(x[i, j] for i in range(1, 13)) == centrales[0][j-1]

        # 2) Capacity constraints: sum of outgoing flows ≤ capacity * y
        for i in range(1, 13):
            prob += lpSum(x[i, j] for j in range(1, 13)) <= y[i] * entrepots[1][i-1]

        # -------------------------------------
        # Solve the problem
        # -------------------------------------
        prob.solve()

        # Update GUI with results
        self.status.setText('Status  :  ' + str(LpStatus[prob.status]))
        self.objectivefunction.setText('Objective function  :  ' + str(value(prob.objective)))

        # Show only the non-zero variables
        self.liste.clear()
        for s in prob.variables():
            if s.varValue != 0:
                self.liste.addItem(f"{s.name} = {s.varValue}")


    # -----------------------------------------------------
    # Open file dialog and call solve()
    # -----------------------------------------------------
    def getfile(self):
        home_directory = os.getenv('HOME')

        # Choose Excel file
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', home_directory)

        if fname != '':
            self.solve(fname)

    # -----------------------------------------------------
    # Build layout
    # -----------------------------------------------------
    def layout(self):
        v = QVBoxLayout()
        h = QHBoxLayout()

        h.addWidget(QLabel('Enter file:'))
        h.addWidget(self.file)

        v.addLayout(h)
        v.addWidget(self.status)
        v.addWidget(self.objectivefunction)
        v.addWidget(self.liste)

        return v


# -----------------------------------------------------
# Main Application Entry
# -----------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load CSS style file
    app.setStyleSheet(open(resource_path("style.qss"), "r").read())

    windo = Windo()
    windo.show()

    sys.exit(app.exec_())
