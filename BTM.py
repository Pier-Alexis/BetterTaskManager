import sys
import psutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget, QPushButton, QHBoxLayout, QLabel, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import pyqtgraph as pg


class AdvancedTaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestionnaire de Tâches Avancé")
        self.setGeometry(100, 100, 1200, 700)
        self.initUI()

    def initUI(self):
        # Widget principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)

        # Barre latérale
        sidebar = QVBoxLayout()
        sidebar.setSpacing(20)
        self.add_sidebar_button("Vue d'ensemble", sidebar)
        self.add_sidebar_button("Processus", sidebar)
        self.add_sidebar_button("Performances", sidebar)
        self.add_sidebar_button("Applications", sidebar)
        self.add_sidebar_button("Paramètres", sidebar)

        # Ajouter la barre latérale au layout principal
        sidebar_frame = QFrame()
        sidebar_frame.setLayout(sidebar)
        sidebar_frame.setStyleSheet("background-color: #2e2e2e; color: white;")
        sidebar_frame.setFixedWidth(200)
        main_layout.addWidget(sidebar_frame)

        # Section principale
        self.main_content = QVBoxLayout()
        main_layout.addLayout(self.main_content)

        # Graphique de performances
        self.init_overview()

    def add_sidebar_button(self, name, layout):
        button = QPushButton(name)
        button.setFont(QFont("Arial", 12))
        button.setFixedHeight(40)
        button.setStyleSheet(
            "background-color: #444; color: white; border-radius: 5px;"
        )
        layout.addWidget(button)

    def init_overview(self):
        self.main_content.setSpacing(20)

        # Titre
        title = QLabel("Vue d'ensemble des ressources")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        self.main_content.addWidget(title)

        # Graphiques CPU et RAM
        self.cpu_graph = self.create_graph("CPU Usage (%)")
        self.ram_graph = self.create_graph("RAM Usage (%)")

        graph_layout = QHBoxLayout()
        graph_layout.addWidget(self.cpu_graph)
        graph_layout.addWidget(self.ram_graph)
        self.main_content.addLayout(graph_layout)

        # Mettre à jour les graphiques toutes les secondes
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graphs)
        self.timer.start(1000)

    def create_graph(self, title):
        graph_widget = pg.PlotWidget(title=title)
        graph_widget.setBackground("w")
        graph_widget.showGrid(x=True, y=True)
        graph_widget.setYRange(0, 100, padding=0)
        return graph_widget

    def update_graphs(self):
        # Ajouter des données de CPU et RAM
        cpu_percent = psutil.cpu_percent(interval=0.1)
        ram_percent = psutil.virtual_memory().percent

        self.update_graph(self.cpu_graph, cpu_percent)
        self.update_graph(self.ram_graph, ram_percent)

    def update_graph(self, graph, value):
        # Mise à jour simplifiée pour l'exemple
        graph.clear()
        graph.plot([0, value], pen=pg.mkPen(color="b", width=2))


# Lancer l'application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdvancedTaskManager()
    window.show()
    sys.exit(app.exec_())
