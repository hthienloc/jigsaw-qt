"""
JigsawPiece Module - Individual Puzzle Elements
Handles high-precision rendering and visual edge blending.
"""

from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsItem
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt

import config

class JigsawPiece(QGraphicsPixmapItem):
    def __init__(self, pixmap, row, col, correct_pos, mask_path):
        super().__init__(pixmap)
        self.row = row
        self.col = col
        self.correct_pos = correct_pos
        self.mask_path = mask_path
        
        self.is_locked = False
        self.is_in_tray = True
        self.cluster = [self] 
        self.tray_scale = 1.0 
        
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                     QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                     QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

    def paint(self, painter, option, widget=None):
        """Paints piece with AA-fringe mitigation for seamless blending."""
        # Enable high-quality rendering
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # 1. Apply Mask
        painter.setClipPath(self.mask_path)
        
        # 2. Draw Pixmap with slight 'bleed' protection
        # We draw the full pixmap area; clipping defines the edge.
        painter.drawPixmap(0, 0, self.pixmap())
        
        # 3. Seamless Blending: REMOVE BORDER FOR LOCKED PIECES
        # If a piece is locked, we want ZERO edge artifacts.
        # Anti-aliasing edges can cause 1px gaps if a pen is drawn.
        if not self.is_locked and not self.isSelected():
            # Only draw a VERY faint guide for unfitted pieces to help visibility
            painter.setPen(QPen(QColor(255, 255, 255, 20), 0.5))
            painter.drawPath(self.mask_path)
        
        # Selection highlight is handled by the ClusterHighlightItem in the board scene
