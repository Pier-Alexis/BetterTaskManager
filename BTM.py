import sys
import psutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton
)
from PyQt5.QtGui import QFont

class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestionnaire de Tâches Avancé")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        # Widget principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # Bouton de rafraîchissement
        self.refresh_button = QPushButton("Rafraîchir")
        self.refresh_button.setFont(QFont("Arial", 12))
        self.refresh_button.clicked.connect(self.update_processes)
        layout.addWidget(self.refresh_button)

        # Tableau des processus
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(5)
        self.process_table.setHorizontalHeaderLabels(["PID", "Nom", "CPU %", "Mémoire %", "Statut"])
        self.process_table.setFont(QFont("Arial", 10))
        layout.addWidget(self.process_table)

        # Charger les processus
        self.update_processes()

    def update_processes(self):
        self.process_table.setRowCount(0)
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            row_position = self.process_table.rowCount()
            self.process_table.insertRow(row_position)
            self.process_table.setItem(row_position, 0, QTableWidgetItem(str(proc.info['pid'])))
            self.process_table.setItem(row_position, 1, QTableWidgetItem(proc.info['name'] or "N/A"))
            self.process_table.setItem(row_position, 2, QTableWidgetItem(f"{proc.info['cpu_percent']:.2f}"))
            self.process_table.setItem(row_position, 3, QTableWidgetItem(f"{proc.info['memory_percent']:.2f}"))
            self.process_table.setItem(row_position, 4, QTableWidgetItem(proc.info['status']))

# Lancer l'application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec_())
