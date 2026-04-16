from PySide6.QtGui import QColor, QGuiApplication, QPalette, QFont
from PySide6.QtCore import Qt

# Window Settings
WINDOW_TITLE = "Jigsaw Qt - Casual Puzzle Game"
DEFAULT_WIDTH = 1150
DEFAULT_HEIGHT = 850

# Jigsaw Board Layout (Ratios)
TRAY_RATIO = 0.15           # Tray takes 15% of vertical height
BOARD_USE_RATIO = 0.95     # Image uses 95% of available canvas space
TAB_SIZE_RATIO = 0.18      # Jigsaw tab relative size
OVERSCAN_PADDING = 8       # Safety margin for high-DPI scaling
SNAP_THRESHOLD = 30        # Pixel distance for snapping
TARGET_PIECE_COUNT = 24    # Default level

DIFFICULTY_PRESETS = {
    "Easy": 12,
    "Normal": 24,
    "Hard": 48,
    "Expert": 96
}

# interaction & UI
TRAY_SLOT_WIDTH = 120
TRAY_START_X = 50
PREVIEW_OPACITY = 0.5
LOCKED_Z_VALUE = 0
DRAGGING_Z_OFFSET = 1000
HINT_OPACITY = 0.2

class SystemTheme:
    """Dynamically resolves colors and fonts based on system settings."""
    @staticmethod
    def palette():
        return QGuiApplication.palette()

    @staticmethod
    def color(role, group=QPalette.ColorGroup.Active):
        return SystemTheme.palette().color(group, role)

    @property
    def BG_COLOR(self): return self.color(QPalette.ColorRole.Window)
    @property
    def BOARD_AREA_BG(self): return self.color(QPalette.ColorRole.Base)
    @property
    def TRAY_BG_COLOR(self): 
        c = self.color(QPalette.ColorRole.Window)
        return c.lighter(110) if c.lightness() < 128 else c.darker(110)
    
    @property
    def SEPARATOR_COLOR(self): return self.color(QPalette.ColorRole.Mid)
    @property
    def TEXT_COLOR(self): return self.color(QPalette.ColorRole.WindowText)
    @property
    def EMPHASIS_COLOR(self): return self.color(QPalette.ColorRole.Highlight)
    
    @property
    def GUIDE_COLOR(self): 
        c = self.color(QPalette.ColorRole.Highlight)
        c.setAlpha(120)
        return c
    
    @property
    def SELECTION_COLOR(self): return self.color(QPalette.ColorRole.Highlight)
    @property
    def PROGRESS_COLOR(self): return self.color(QPalette.ColorRole.Highlight)

    @property
    def HEADER_BG(self):
        c = self.color(QPalette.ColorRole.Window)
        return c.darker(120) if c.lightness() > 128 else c.lighter(120)

    @property
    def MAIN_FONT(self): return QGuiApplication.font()
    
    @property
    def UI_STYLE(self):
        # Return a QSS snippet that applies system colors to ModernButtons
        bg = self.color(QPalette.ColorRole.Button).name(QColor.NameFormat.HexArgb)
        text = self.color(QPalette.ColorRole.ButtonText).name(QColor.NameFormat.HexArgb)
        highlight = self.color(QPalette.ColorRole.Highlight).name(QColor.NameFormat.HexArgb)
        return f"""
            QPushButton {{
                background-color: {bg};
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: {text};
                padding: 10px 20px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {highlight};
                color: white;
            }}
        """

theme = SystemTheme()
