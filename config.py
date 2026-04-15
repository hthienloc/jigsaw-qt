from PySide6.QtGui import QColor

# Window Settings
WINDOW_TITLE = "Jigsaw Qt - Casual Puzzle Game"
DEFAULT_WIDTH = 1100
DEFAULT_HEIGHT = 800

# Jigsaw Board Logic
TRAY_HEIGHT = 150
BOARD_MARGIN_RATIO = 0.8  # Image takes 80% of board area
TAB_SIZE_RATIO = 0.2      # Tab is 20% of piece size
OVERSCAN_PADDING = 8      # Safety margin for anti-fringe
SNAP_THRESHOLD = 30       # Manhattan distance for snapping
TARGET_PIECE_SIZE = 200    # Optimal size for a puzzle piece

# interaction & UI
TRAY_SLOT_WIDTH = 120
TRAY_START_X = 50
TRAY_PIECE_Y_OFFSET = 30
PREVIEW_OPACITY = 0.5
LOCKED_Z_VALUE = 0
DRAGGING_Z_OFFSET = 1000

# Colors
BG_COLOR = QColor(30, 30, 30)
TRAY_BG_COLOR = QColor(25, 25, 25)
SEPARATOR_COLOR = QColor(50, 50, 50)
GUIDE_COLOR = QColor(255, 255, 255, 20)
SELECTION_COLOR = QColor(255, 255, 255, 150)
