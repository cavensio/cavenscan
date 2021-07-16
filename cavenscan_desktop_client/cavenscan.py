import sys
from time import sleep

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import *

from cavenscan_mcu import CavenscanMcuEmulator
from cavenscan_model import CavenscanModel


class ScanThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, model: CavenscanModel) -> None:
        super().__init__()
        self._model = model

    def run(self):
        while not self.isInterruptionRequested():
            self._model.scan()
            for i in range(self._model.from_channel, self._model.to_channel + 1):
                if not self.isInterruptionRequested():
                    sleep(0.05)
                self.progress.emit(i)


class Cavenscan(QMainWindow):

    def __init__(self):
        super().__init__()
        mcu = CavenscanMcuEmulator()
        self._model = CavenscanModel(mcu)
        self.setWindowTitle('Cavenscan')
        self.setMinimumSize(1200, 400)

        self.setStatusBar(QStatusBar())
        vbox = QVBoxLayout()
        vbox.addLayout(self._create_controls_panel())
        vbox.addWidget(QLabel('Recent stats:'))
        vbox.addLayout(self._create_stats_panel())
        vbox.addWidget(QLabel('Total stats:'))
        vbox.addLayout(self._create_total_stats_panel())
        vbox.setStretch(2, 1)
        vbox.setStretch(4, 2)

        center = QWidget()
        center.setLayout(vbox)
        self.setCentralWidget(center)
        self._init_thread()

    def _create_stats_panel(self) -> QLayout:
        layout = QGridLayout()
        layout.setSpacing(2)

        rows = []
        for row in range(0, self._model.lines_count):
            items = list()
            for col in range(0, self._model.channels_count):
                item = QLabel()
                item.setProperty('block', 0)
                item.setMinimumSize(5, 10)
                item.setStatusTip(f'Channel: {self._model.from_channel + col}')
                layout.addWidget(item, row, col)
                items.append(item)
            rows.append(items)
        self._stat_elements = rows
        return layout

    def _create_total_stats_panel(self) -> QLayout:
        layout = QGridLayout()
        layout.setSpacing(2)

        items = []
        for col in range(0, self._model.channels_count):
            item = QLabel()
            item.setProperty('block', 0)
            item.setMinimumSize(5, 30)
            item.setStatusTip(f'Channel: {self._model.from_channel + col}')
            layout.addWidget(item, 5, col)
            items.append(item)
        self._total_stat_elements = items
        return layout

    def _create_controls_panel(self) -> QLayout:
        from_input = QSpinBox()
        from_input.setRange(self._model.from_channel, self._model.to_channel)
        from_input.setValue(self._model.from_channel)
        from_input.setMinimumWidth(75)

        to_input = QSpinBox()
        to_input.setRange(self._model.from_channel, self._model.to_channel)
        to_input.setValue(self._model.to_channel)
        to_input.setMinimumWidth(75)

        scan_button = QPushButton('Scan')
        scan_button.setCheckable(True)

        save_button = QPushButton('Save')
        save_button.setEnabled(False)
        save_button.pressed.connect(self._show_save_dialog)

        clear_button = QPushButton('Clear')
        clear_button.pressed.connect(self._show_clear_dialog)
        clear_button.setEnabled(False)

        port_select = QComboBox()
        port_select.addItems(self._model.get_ports())

        def resize_matrix():
            for i in range(0, self._model.lines_count):
                for j in range(0, self._model.channels_count):
                    if from_input.value() <= j + 1 <= to_input.value():
                        self._stat_elements[i][j].show()
                    else:
                        self._stat_elements[i][j].hide()
            for j in range(0, self._model.channels_count):
                if from_input.value() <= j + 1 <= to_input.value():
                    self._total_stat_elements[j].show()
                else:
                    self._total_stat_elements[j].hide()

        def from_to_fix():
            if from_input.value() > to_input.value():
                to_input.setValue(from_input.value())
            resize_matrix()

        def to_from_fix():
            if to_input.value() < from_input.value():
                from_input.setValue(to_input.value())
            resize_matrix()

        def scan():
            if scan_button.isChecked():
                from_input.setEnabled(True)
                to_input.setEnabled(True)
                port_select.setEnabled(True)
                self._stop_scan()
            else:
                from_input.setEnabled(False)
                to_input.setEnabled(False)
                port_select.setEnabled(False)
                self._start_scan()

        from_input.valueChanged.connect(from_to_fix)
        to_input.valueChanged.connect(to_from_fix)
        scan_button.pressed.connect(scan)

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Channels range:'))

        hbox.addWidget(from_input)
        hbox.addWidget(QLabel('to:'))
        hbox.addWidget(to_input)
        hbox.addWidget(scan_button)
        hbox.addStretch()
        hbox.addWidget(save_button)
        hbox.addStretch()
        hbox.addWidget(clear_button)
        hbox.addStretch()
        hbox.addWidget(QLabel('Port:'))
        hbox.addWidget(port_select)
        return hbox

    def _clear_stats(self):
        self._model.clear_stats()

        for i in range(0, self._model.lines_count):
            for j in range(0, self._model.channels_count):
                self._update_style(self._stat_elements[i][j], block=0)
        for j in range(0, self._model.channels_count):
            self._update_style(self._total_stat_elements[j], block=0)

        self.statusBar().showMessage('Cleared stats', 5000)

    def _save_to_file(self, filename):
        self._model.save_stats(filename)
        self.statusBar().showMessage(f'Saved stats {filename}', 5000)

    def _show_clear_dialog(self):
        dlg = QMessageBox()
        dlg.setWindowTitle('Clear stats')
        dlg.setText('This will clear all collected stats')
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Warning)
        button = dlg.exec()

        if button == QMessageBox.Yes:
            self._clear_stats()

    def _show_save_dialog(self):
        filename, _ = QFileDialog.getSaveFileName(caption='Save stats', filter='CSV file (*.csv)')
        if filename:
            self._save_to_file(filename)

    @staticmethod
    def _update_style(elem: QWidget, **kwargs):
        for k, v in kwargs.items():
            elem.setProperty(k, v)
        elem.setStyle(elem.style())

    def _init_thread(self):
        self.thread = ScanThread(self._model)
        self.thread.progress.connect(self.report_progress)

    def _start_scan(self):
        self.thread.start()

    def _stop_scan(self):
        self.thread.requestInterruption()

    @staticmethod
    def _color(number: int, count: int):
        val = (number * 100 / count)
        if val == 0:
            return 0
        elif val < 5:
            return 1
        elif val < 10:
            return 2
        elif val < 25:
            return 3
        elif val < 50:
            return 4
        elif val < 75:
            return 5
        else:
            return 6

    def report_progress(self, channel):
        line = self._model.curr_line
        stat = self._model.get_stats(line).stats[channel]
        count = self._model.get_stats(line).scans_count
        val = Cavenscan._color(stat, count)
        elem: QLabel = self._stat_elements[line][channel - self._model.from_channel]
        elem.setStatusTip(f'Channel: {channel}, carrier: {stat}, scans: {count}')
        elem.setProperty('block', val)
        elem.setStyle(elem.style())

        if channel == self._model.to_channel:
            line = self._model.next_line
            channel = self._model.from_channel
            for i in range(0, self._model.channels_count):
                stat = self._model.get_total_stats().stats[i]
                count = self._model.get_total_stats().scans_count
                val = Cavenscan._color(stat, count)
                elem = self._total_stat_elements[i]
                elem.setStatusTip(f'Channel: {i}, total carrier: {stat}, scans: {count}')
                elem.setProperty('block', val)
                elem.setStyle(elem.style())
        else:
            channel += 1

        elem = self._stat_elements[line][channel - self._model.from_channel]
        elem.setProperty('block', 'active')
        elem.setStyle(elem.style())


if __name__ == '__main__':
    old_excepthook = sys.excepthook


    def exception_hook(exctype, value, traceback):
        old_excepthook(exctype, value, traceback)
        sys.exit(1)


    sys.excepthook = exception_hook

    app = QApplication(sys.argv)
    with open('cavenscan.qss') as f:
        app.setStyleSheet(f.read())
    window = Cavenscan()
    window.show()
    app.exec_()
