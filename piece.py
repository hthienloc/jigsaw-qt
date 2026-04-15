"""
JigsawPiece Module - Individual Puzzle Elements
Defines the visual representation and state handling for puzzle pieces.
"""

from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsItem
from PySide6.QtGui import QPen
from PySide6.QtCore import Qt
import config

class JigsawPiece(QGraphicsPixmapItem):
    """
    Graphics item representing a single puzzle piece.
    Maintains information about its origin, cluster connectivity, and lock state.
    """
    def __init__(self, pixmap, row: int, col: int, correct_pos, drawn_path):
        super().__init__(pixmap)
        self.row = row
        self.col = col
        self.correct_pos = correct_pos  # Target scene position for snapping
        self.drawn_path = drawn_path    # Vector path for selection highlights
        
        # Interaction Flags
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        
        self.is_locked = False
        self.is_in_tray = True
        self.cluster = [self]      # List of pieces snapped together
        
        self.tray_scale = 0.25      # Scale when residing in the bottom tray
        self.snap_threshold = config.SNAP_THRESHOLD
        
        # High-quality rendering hint
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def paint(self, painter, option, widget):
        """Custom paint implementation to draw selection borders."""
        super().paint(painter, option, widget)
        if self.isSelected() and not self.is_locked:
            painter.setPen(QPen(config.SELECTION_COLOR, 3))
            painter.drawPath(self.drawn_path)
