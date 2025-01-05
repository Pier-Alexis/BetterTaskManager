import sys
import psutil
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QComboBox, QHBoxLayout, QTextEdit
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import pyqtgraph as pg

class TerminalWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: black; color: white;")
        self.setFont(QFont("Courier New", 10))
        self.setReadOnly(False)

    def execute_command(self, command):
        result = os.popen(command).read()
        self.append(result)

class AdvancedTaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestionnaire de Tâches Avancé")
        self.setGeometry(100, 100, 1200, 700)
        self.is_dark_mode = False
        self.cpu_threshold = 80  # Seuil de l'alerte CPU
        self.ram_threshold = 80  # Seuil de l'alerte RAM
        self.initUI()
        self.init_timer()

    def initUI(self):
        # Layout principal
        layout = QVBoxLayout()

        # Tableau des processus
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(5)
        self.process_table.setHorizontalHeaderLabels(["PID", "Nom", "CPU %", "Mémoire %", "Actions"])
        self.process_table.setColumnWidth(1, 250)
        self.process_table.setColumnWidth(4, 150)

        layout.addWidget(self.process_table)

        # Boutons pour tuer des processus
        kill_button = QPushButton("Tuer le processus sélectionné")
        kill_button.clicked.connect(self.kill_process)
        layout.addWidget(kill_button)

        # Terminal intégré
        self.terminal = TerminalWidget()
        layout.addWidget(self.terminal)

        # Choix de thème
        theme_combo = QComboBox()
        theme_combo.addItem("Mode Clair")
        theme_combo.addItem("Mode Sombre")
        theme_combo.currentIndexChanged.connect(self.toggle_theme)
        layout.addWidget(theme_combo)

        # Bouton de nettoyage des fichiers temporaires
        clean_button = QPushButton("Nettoyer les fichiers temporaires")
        clean_button.clicked.connect(self.clean_temp_files)
        layout.addWidget(clean_button)

        # Graphiques CPU et RAM
        self.cpu_graph = pg.PlotWidget(title="Utilisation CPU")
        self.ram_graph = pg.PlotWidget(title="Utilisation RAM")
        layout.addWidget(self.cpu_graph)
        layout.addWidget(self.ram_graph)

        # Layout et widget principal
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def init_timer(self):
        # Met à jour les informations des processus toutes les secondes
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_processes)
        self.timer.start(1000)

        # Met à jour les graphiques toutes les 2 secondes
        self.graph_timer = QTimer(self)
        self.graph_timer.timeout.connect(self.update_graphs)
        self.graph_timer.start(2000)

    def update_processes(self):
        # Récupère les processus actifs
        processes = [(p.pid, p.name(), psutil.cpu_percent(interval=0.1), psutil.virtual_memory().percent) for p in psutil.process_iter(['pid', 'name'])]

        # Met à jour le tableau des processus
        self.process_table.setRowCount(len(processes))
        for row, (pid, name, cpu, memory) in enumerate(processes):
            self.process_table.setItem(row, 0, QTableWidgetItem(str(pid)))
            self.process_table.setItem(row, 1, QTableWidgetItem(name))
            self.process_table.setItem(row, 2, QTableWidgetItem(f"{cpu}%"))
            self.process_table.setItem(row, 3, QTableWidgetItem(f"{memory}%"))
            kill_button = QPushButton("Tuer")
            kill_button.clicked.connect(lambda _, pid=pid: self.kill_process(pid))
            self.process_table.setCellWidget(row, 4, kill_button)

    def update_graphs(self):
        # Récupère les statistiques du CPU et de la RAM
        cpu_percent = psutil.cpu_percent(interval=0.1)
        ram_percent = psutil.virtual_memory().percent

        # Affiche les graphiques
        self.update_graph(self.cpu_graph, cpu_percent)
        self.update_graph(self.ram_graph, ram_percent)

        # Vérifie si les seuils sont dépassés pour afficher une alerte
        if cpu_percent > self.cpu_threshold:
            self.cpu_graph.setBackground('red')
        else:
            self.cpu_graph.setBackground('white')

        if ram_percent > self.ram_threshold:
            self.ram_graph.setBackground('red')
        else:
            self.ram_graph.setBackground('white')

    def update_graph(self, graph, value):
        # Affiche les valeurs sur le graphique
        graph.clear()
        graph.plot([0, value], pen=pg.mkPen(color="b", width=2), symbol='o', symbolBrush='r', symbolSize=10)

    def kill_process(self, pid=None):
        # Tuer le processus sélectionné
        if pid is None:
            pid = self.process_table.item(self.process_table.currentRow(), 0).text()
        try:
            process = psutil.Process(int(pid))
            process.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    def toggle_theme(self):
        # Bascule entre le mode clair et sombre
        if self.is_dark_mode:
            self.set_light_mode()
        else:
            self.set_dark_mode()
        self.is_dark_mode = not self.is_dark_mode

    def set_dark_mode(self):
        self.setStyleSheet("background-color: #2e2e2e; color: white;")

    def set_light_mode(self):
        self.setStyleSheet("background-color: white; color: black;")

    def clean_temp_files(self):
        # Nettoie les fichiers temporaires
        temp_dirs = ["/tmp", "/var/tmp"]
        for temp_dir in temp_dirs:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    try:
                        os.remove(os.path.join(root, file))
                    except Exception as e:
                        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdvancedTaskManager()
    window.show()
    sys.exit(app.exec_())
