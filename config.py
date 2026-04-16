from PySide6.QtGui import QColor

# Window Settings
WINDOW_TITLE = "Jigsaw Qt - Casual Puzzle Game"
DEFAULT_WIDTH = 1150
DEFAULT_HEIGHT = 850

# Jigsaw Board Layout (Ratios)
TRAY_RATIO = 0.2           # Tray takes 20% of vertical height
BOARD_USE_RATIO = 0.95     # Image uses 95% of available canvas space
TAB_SIZE_RATIO = 0.18      # Jigsaw tab relative size
OVERSCAN_PADDING = 8       # Safety margin for high-DPI scaling
SNAP_THRESHOLD = 30        # Pixel distance for snapping
TARGET_PIECE_COUNT = 24    # Desired piece quantity

# interaction & UI
TRAY_SLOT_WIDTH = 120
TRAY_START_X = 50
TRAY_PIECE_Y_OFFSET = 0.3  # Relative to tray height
PREVIEW_OPACITY = 0.6
LOCKED_Z_VALUE = 0
DRAGGING_Z_OFFSET = 1000

# Colors
BG_COLOR = QColor(25, 25, 25)
BOARD_AREA_BG = QColor(33, 33, 33) 
TRAY_BG_COLOR = QColor(20, 20, 20)
SEPARATOR_COLOR = QColor(45, 45, 45)
GUIDE_COLOR = QColor(79, 195, 247, 100) # Stronger Cyan Guide
SELECTION_COLOR = QColor(79, 195, 247, 220)
