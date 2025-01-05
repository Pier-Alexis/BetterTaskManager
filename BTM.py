import sys
import psutil
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget, QPushButton, QHBoxLayout, QLabel, QFrame, QStackedLayout
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
        self.buttons = {}
        self.pages = QStackedLayout()

        self.add_sidebar_button("Vue d'ensemble", sidebar, self.init_overview)
        self.add_sidebar_button("Processus", sidebar, self.init_processes)
        self.add_sidebar_button("Performances", sidebar, self.init_performance)
        self.add_sidebar_button("Applications", sidebar, self.init_applications)
        self.add_sidebar_button("Paramètres", sidebar, self.init_settings)

        # Ajouter la barre latérale au layout principal
        sidebar_frame = QFrame()
        sidebar_frame.setLayout(sidebar)
        sidebar_frame.setStyleSheet("background-color: #2e2e2e; color: white;")
        sidebar_frame.setFixedWidth(200)
        main_layout.addWidget(sidebar_frame)

        # Section principale (pages dynamiques)
        main_layout.addLayout(self.pages)

        # Charger la vue d'ensemble par défaut
        self.init_overview()

    def add_sidebar_button(self, name, layout, function):
        button = QPushButton(name)
        button.setFont(QFont("Arial", 12))
        button.setFixedHeight(40)
        button.setStyleSheet(
            "background-color: #444; color: white; border-radius: 5px;"
        )
        button.clicked.connect(function)
        layout.addWidget(button)
        self.buttons[name] = button

    def switch_page(self, widget):
        self.pages.setCurrentWidget(widget)

    def init_overview(self):
        overview_page = QWidget()
        layout = QVBoxLayout(overview_page)

        # Titre
        title = QLabel("Vue d'ensemble des ressources")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Graphiques CPU et RAM
        self.cpu_graph = self.create_graph("CPU Usage (%)")
        self.ram_graph = self.create_graph("RAM Usage (%)")

        graph_layout = QHBoxLayout()
        graph_layout.addWidget(self.cpu_graph)
        graph_layout.addWidget(self.ram_graph)
        layout.addLayout(graph_layout)

        # Ajouter à la pile de pages
        self.pages.addWidget(overview_page)
        self.switch_page(overview_page)

        # Mettre à jour les graphiques toutes les secondes
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graphs)
        self.timer.start(1000)

    def init_processes(self):
        process_page = QWidget()
        layout = QVBoxLayout(process_page)

        # Titre
        title = QLabel("Processus")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Tableau des processus
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(5)
        self.process_table.setHorizontalHeaderLabels(
            ["PID", "Nom", "CPU %", "Mémoire %", "Statut"]
        )
        layout.addWidget(self.process_table)

        # Bouton de rafraîchissement
        refresh_button = QPushButton("Rafraîchir")
        refresh_button.clicked.connect(self.update_process_table)
        layout.addWidget(refresh_button)

        # Ajouter à la pile de pages
        self.pages.addWidget(process_page)
        self.switch_page(process_page)
        self.update_process_table()

    def init_performance(self):
        performance_page = QWidget()
        layout = QVBoxLayout(performance_page)

        # Titre
        title = QLabel("Performances")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Graphiques interactifs
        self.disk_graph = self.create_graph("Disk Usage (%)")
        self.network_graph = self.create_graph("Network Usage (%)")

        graph_layout = QHBoxLayout()
        graph_layout.addWidget(self.disk_graph)
        graph_layout.addWidget(self.network_graph)
        layout.addLayout(graph_layout)

        # Ajouter à la pile de pages
        self.pages.addWidget(performance_page)
        self.switch_page(performance_page)

    def init_applications(self):
        app_page = QWidget()
        layout = QVBoxLayout(app_page)

        # Titre
        title = QLabel("Applications installées")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Tableau des applications (nom et taille)
        self.app_table = QTableWidget()
        self.app_table.setColumnCount(2)
        self.app_table.setHorizontalHeaderLabels(["Nom", "Taille"])
        layout.addWidget(self.app_table)

        # Bouton de désinstallation
        uninstall_button = QPushButton("Désinstaller sélectionnée")
        uninstall_button.clicked.connect(self.uninstall_application)
        layout.addWidget(uninstall_button)

        # Ajouter à la pile de pages
        self.pages.addWidget(app_page)
        self.switch_page(app_page)
        self.update_applications_table()

    def init_settings(self):
        settings_page = QWidget()
        layout = QVBoxLayout(settings_page)

        # Titre
        title = QLabel("Paramètres")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Ajouter à la pile de pages
        self.pages.addWidget(settings_page)
        self.switch_page(settings_page)

    def create_graph(self, title):
        graph_widget = pg.PlotWidget(title=title)
        graph_widget.setBackground("w")
        graph_widget.showGrid(x=True, y=True)
        graph_widget.setYRange(0, 100, padding=0)
        return graph_widget

    def update_graphs(self):
        cpu_percent = psutil.cpu_percent(interval=0.1)
        ram_percent = psutil.virtual_memory().percent

        self.update_graph(self.cpu_graph, cpu_percent)
        self.update_graph(self.ram_graph, ram_percent)

    def update_graph(self, graph, value):
        graph.clear()
        graph.plot([0, value], pen=pg.mkPen(color="b", width=2))

    def update_process_table(self):
        self.process_table.setRowCount(0)
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            row = self.process_table.rowCount()
            self.process_table.insertRow(row)
            self.process_table.setItem(row, 0, QTableWidgetItem(str(proc.info['pid'])))
            self.process_table.setItem(row, 1, QTableWidgetItem(proc.info['name'] or "N/A"))
            self.process_table.setItem(row, 2, QTableWidgetItem(f"{proc.info['cpu_percent']:.2f}"))
            self.process_table.setItem(row, 3, QTableWidgetItem(f"{proc.info['memory_percent']:.2f}"))
            self.process_table.setItem(row, 4, QTableWidgetItem(proc.info['status']))

    def update_applications_table(self):
        self.app_table.setRowCount(0)
        for app in psutil.disk_partitions():
            row = self.app_table.rowCount()
            self.app_table.insertRow(row)
            self.app_table.setItem(row, 0, QTableWidgetItem(app.device))
            self.app_table.setItem(row, 1, QTableWidgetItem("N/A"))

    def uninstall_application(self):
        selected_row = self.app_table.currentRow()
        if selected_row != -1:
            app_name = self.app_table.item(selected_row, 0).text()
            os.system(f"msiexec /x {app_name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdvancedTaskManager()
    window.show()
    sys.exit(app.exec_())
