"""
JigsawPiece Module - Individual Puzzle Elements
Handles high-precision rendering and visual edge blending.
"""

from PySide6.QtWidgets import QGraphicsObject, QGraphicsItem
from PySide6.QtGui import QPainter, QPen, QColor, QPixmap
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QPointF

import config

class JigsawPiece(QGraphicsObject):
    def __init__(self, pixmap, row, col, correct_pos, mask_path):
        super().__init__()
        self._pixmap = pixmap
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
        
        self._glow_intensity = 0.0

    @Property(float)
    def glow_intensity(self): return self._glow_intensity
    @glow_intensity.setter
    def glow_intensity(self, val):
        self._glow_intensity = val
        self.update()

    def pulse(self):
        self.anim = QPropertyAnimation(self, b"glow_intensity")
        self.anim.setDuration(400)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

    def boundingRect(self):
        return self._pixmap.rect()

    def paint(self, painter, option, widget=None):
        """Paints piece with AA-fringe mitigation for seamless blending."""
        # Enable high-quality rendering
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # 1. Apply Mask
        painter.setClipPath(self.mask_path)
        
        # 2. Draw Pixmap
        painter.drawPixmap(0, 0, self._pixmap)
        
        # 3. Seamless Blending
        # If a piece is locked, we want ZERO edge artifacts.
        # Anti-aliasing edges can cause 1px gaps if a pen is drawn.
        if not self.is_locked and not self.isSelected():
            # Only draw a VERY faint guide for unfitted pieces to help visibility
            painter.setPen(QPen(QColor(255, 255, 255, 20), 0.5))
            painter.drawPath(self.mask_path)
        else:
            # Explicitly disable pen to avoid default 1px black outline
            painter.setPen(Qt.PenStyle.NoPen)
        
        if self._glow_intensity > 0:
            glow_color = QColor(config.theme.SELECTION_COLOR)
            glow_color.setAlphaF(self._glow_intensity * 0.8)
            painter.setPen(QPen(glow_color, 4))
            painter.drawPath(self.mask_path)
        
        # Selection highlight is handled by the ClusterHighlightItem in the board scene
