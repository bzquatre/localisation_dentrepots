from PyQt5.QtWidgets import QApplication,QWidget,QLabel,QFileDialog,QListWidget,QPushButton,QTableWidget,QHBoxLayout,QVBoxLayout,QMessageBox
from PyQt5.QtGui import QIntValidator
import sys
from pulp import *
import pandas as pd
import numpy as np

# dataset

class Windo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("USTHB >> youcef >>Localisation_dentrepots ")
        self.setGeometry(200,100,1024,600)
        self.file=QPushButton(self,text="select file")
        self.file.clicked.connect(self.getfile)
        self.status=QLabel(self,text="Status:")
        self.objectivefunction=QLabel(self,text="Objective function:")
        self.liste=QListWidget(self)
        self.btnghraph1=QPushButton(text="Ghraphe Biparti")
        self.btntranv=QPushButton(text= "Transvarsal Minimum")
        self.btnghraph2=QPushButton(text="Ghraphe de Transvarsal Minimum")
        self.btnghraph2.setStyleSheet('padding: 15px 25px;')
        self.setLayout(self.layout())
        self.show()
    def solve(self,filename):
        file = pd.ExcelFile(filename)

        livraisons = np.array(pd.read_excel(file, index_col=0, sheet_name=0))
        entrepots = np.array(pd.read_excel(file, index_col=0, sheet_name=1))
        centrales = np.array(pd.read_excel(file, index_col=0, sheet_name=2))

        # Dicts for indices
        var_y_keys = [i for i in range(1, 13)]
        var_x_keys = [(i, j) for i in range(1, 13) for j in range(1, 13)]

        # Decision Variables
        y = LpVariable.dicts('y', var_y_keys, cat='Binary')
        x = LpVariable.dicts('x', var_x_keys, lowBound=0, cat='Integer')

        # Problem
        prob = LpProblem("Localisation_dentrepots", LpMinimize)

        # Objective Function
        coeff_y = [entrepots[0][i] for i in range(12)]
        coeff_x = [livraisons[i][j] for i in range(12) for j in range(12)]
        coeff_x_dict = dict(zip(var_x_keys, coeff_x))
        coeff_y_dict = dict(zip(var_y_keys, coeff_y))

        prob += (lpSum(coeff_y_dict[i]*y[i] for i in var_y_keys)
                +lpSum(coeff_x_dict[i]*x[i] for i in var_x_keys))


        # Constraints
        # 1st constraint
        prob += lpSum(x[i,1] for i in range(1,13)) == centrales[0][0]
        prob += lpSum(x[i,2] for i in range(1,13)) == centrales[0][1]
        prob += lpSum(x[i,3] for i in range(1,13)) == centrales[0][2]
        prob += lpSum(x[i,4] for i in range(1,13)) == centrales[0][3]
        prob += lpSum(x[i,5] for i in range(1,13)) == centrales[0][4]
        prob += lpSum(x[i,6] for i in range(1,13)) == centrales[0][5]
        prob += lpSum(x[i,7] for i in range(1,13)) == centrales[0][6]
        prob += lpSum(x[i,8] for i in range(1,13)) == centrales[0][7]
        prob += lpSum(x[i,9] for i in range(1,13)) == centrales[0][8]
        prob += lpSum(x[i,10] for i in range(1,13))== centrales[0][9]
        prob += lpSum(x[i,11] for i in range(1,13))== centrales[0][10]
        prob += lpSum(x[i,12] for i in range(1,13))== centrales[0][11]

        # 2nd constraint
        prob += lpSum(x[1,i] for i in range(1,13)) <= y[1]*entrepots[1][0]
        prob += lpSum(x[2,i] for i in range(1,13)) <= y[2]*entrepots[1][1]
        prob += lpSum(x[3,i] for i in range(1,13)) <= y[3]*entrepots[1][2]
        prob += lpSum(x[4,i] for i in range(1,13)) <= y[4]*entrepots[1][3]
        prob += lpSum(x[5,i] for i in range(1,13)) <= y[5]*entrepots[1][4]
        prob += lpSum(x[6,i] for i in range(1,13)) <= y[6]*entrepots[1][5]
        prob += lpSum(x[7,i] for i in range(1,13)) <= y[7]*entrepots[1][6]
        prob += lpSum(x[8,i] for i in range(1,13)) <= y[8]*entrepots[1][7]
        prob += lpSum(x[9,i] for i in range(1,13)) <= y[9]*entrepots[1][8]
        prob += lpSum(x[10,i] for i in range(1,13))<= y[10]*entrepots[1][9]
        prob += lpSum(x[11,i] for i in range(1,13))<= y[11]*entrepots[1][10]
        prob += lpSum(x[12,i] for i in range(1,13))<= y[12]*entrepots[1][11]

        # solve
        prob.solve()
        # Status of the solution
        self.status.setText('Status  :  '+str(LpStatus[prob.status]))
        # Objective function value
        self.objectivefunction.setText('Objective function  :  '+str(value(prob.objective)))
        # Decision variables values
        self.liste.clear()
        for s in prob.variables():
            if s.varValue != 0:
                self.liste.addItem(s.name+'='+str(s.varValue))
    def getfile(self):
      fname = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\')
      self.solve(fname[0])
    def layout(self):
        v=QVBoxLayout()
        h=QHBoxLayout()
        h.addWidget(QLabel('entre file :'))
        h.addWidget(self.file)
        v.addLayout(h)
        v.addWidget(self.status)
        v.addWidget(self.objectivefunction)
        v.addWidget(self.liste)
     
        return v
if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setStyleSheet(open("style.qss","r").read())
    windo=Windo()
    windo.show()
    sys.exit(app.exec_())













