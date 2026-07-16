"""Application main entry point.

Initializes the window structure, sets target dimensions based on display ratios,
and activates runtime layouts.
"""

import os
import sys
import urllib.request

# Pre-emptively enforce PySide6 bindings inside qtpy
os.environ["QT_API"] = "pyside6"

from qtpy import QtWidgets, QtGui
from dashboard_window import DashboardFrame, FONT_FAMILY


class MainApplicationWindow(QtWidgets.QMainWindow):
    """Core GUI workspace wrapper handling resizing configurations."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Market Analytics Desktop")
        self._set_scaled_geometry()

        self.central_frame = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_frame)

        layout = QtWidgets.QVBoxLayout(self.central_frame)
        layout.setContentsMargins(15, 15, 15, 15)

        self.dashboard = DashboardFrame(self)
        layout.addWidget(self.dashboard)

    def _set_scaled_geometry(self) -> None:
        """Retrieves user screen resolution and configures the standard 3/4 layout scale."""
        screen = QtWidgets.QApplication.primaryScreen()
        screen_geom = screen.availableGeometry()

        target_width = int(screen_geom.width() * 0.75)
        target_height = int(screen_geom.height() * 0.75)

        start_x = int((screen_geom.width() - target_width) / 2) + screen_geom.x()
        start_y = int((screen_geom.height() - target_height) / 2) + screen_geom.y()

        self.setGeometry(start_x, start_y, target_width, target_height)


def _bootstrap_google_fonts() -> None:
    """Streams and registers the highly legible Inter font family directly into the application cache."""
    try:
        font_url = "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Variable.ttf"
        req = urllib.request.Request(font_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            font_data = response.read()
        QtGui.QFontDatabase.addApplicationFontFromData(font_data)
    except Exception:
        pass  # Gracefully drop back to system sans-serif chains if network timeouts strike


def run() -> None:
    """Sets system-level font settings and initiates the event loop execution."""
    app = QtWidgets.QApplication(sys.argv)

    # Initialize typography bindings
    _bootstrap_google_fonts()
    app.setFont(QtGui.QFont(FONT_FAMILY, 9))

    win = MainApplicationWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
