"""
JigsawBoard Module - Core Logic and Rendering
Handles puzzle piece generation, layout management, and game interaction.
"""

import random
import math
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem
from PySide6.QtGui import QPainterPath, QImage, QPixmap, QPainter, QColor, QPen, QBrush, QTransform
from PySide6.QtCore import Qt, QPointF, QRectF

import config
from piece import JigsawPiece

class JigsawBoard(QGraphicsScene):
    """
    Core Graphics Scene for the Jigsaw game.
    Manages the game board area, the bottom piece tray, and interaction logic.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pieces = []
        self.image = None
        self.rows = 4
        self.cols = 4
        self.tray_rect = QRectF()
        self.board_rect = QRectF()
        self.tray_scroll_offset = 0
        self.preview_item = None

    def load_image(self, image_path: str, rows: int = 4, cols: int = 4):
        """
        Initializes a new puzzle from an image file.
        Scales the image, generates piece geometry, and populates the tray.
        """
        # Calculate dynamic scene dimensions
        w_scene = self.width() if self.width() > 0 else config.DEFAULT_WIDTH
        h_scene = self.height() if self.height() > 0 else config.DEFAULT_HEIGHT
        
        self.tray_rect = QRectF(0, h_scene - config.TRAY_HEIGHT, w_scene, config.TRAY_HEIGHT)
        self.board_rect = QRectF(0, 0, w_scene, h_scene - config.TRAY_HEIGHT)
        
        self.clear()
        self.pieces = []
        self.rows, self.cols = rows, cols
        
        original_img = QImage(image_path)
        # Scale image to 80% of board area
        target_w = self.board_rect.width() * config.BOARD_MARGIN_RATIO
        target_h = self.board_rect.height() * config.BOARD_MARGIN_RATIO
        self.image = original_img.scaled(int(target_w), int(target_h), 
                                         Qt.AspectRatioMode.KeepAspectRatio, 
                                         Qt.TransformationMode.SmoothTransformation)
        
        w_piece = self.image.width() // cols
        h_piece = self.image.height() // rows
        board_offset = QPointF((self.board_rect.width() - self.image.width()) / 2,
                               (self.board_rect.height() - self.image.height()) / 2)
        
        tab_size = min(w_piece, h_piece) * config.TAB_SIZE_RATIO
        
        # Generate stable tab directions
        h_tabs = [[random.choice([1, -1]) for _ in range(cols-1)] for _ in range(rows)]
        v_tabs = [[random.choice([1, -1]) for _ in range(cols)] for _ in range(rows-1)]

        for r in range(rows):
            for c in range(cols):
                path = QPainterPath()
                path.moveTo(0, 0)
                # Build piece boundary path
                if r > 0: self._add_tab(path, w_piece, h_piece, tab_size, v_tabs[r-1][c], "top")
                else: path.lineTo(w_piece, 0)
                if c < cols - 1: self._add_tab(path, w_piece, h_piece, tab_size, h_tabs[r][c], "right")
                else: path.lineTo(w_piece, h_piece)
                if r < rows - 1: self._add_tab(path, w_piece, h_piece, tab_size, v_tabs[r][c], "bottom")
                else: path.lineTo(0, h_piece)
                if c > 0: self._add_tab(path, w_piece, h_piece, tab_size, -h_tabs[r][c-1], "left")
                else: path.lineTo(0, 0)

                # Create piece pixmap with overscan padding for clean edges
                padding = math.ceil(tab_size) + config.OVERSCAN_PADDING
                pw, ph = w_piece + 2*padding, h_piece + 2*padding
                
                # Use Transparent White fill to prevent fringe bleeding into dark colors
                img_out = QImage(pw, ph, QImage.Format.Format_ARGB32_Premultiplied)
                img_out.fill(QColor(255, 255, 255, 0))
                
                pnt = QPainter(img_out)
                pnt.setRenderHint(QPainter.RenderHint.Antialiasing)
                pnt.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                # Draw underlying image shifted
                pnt.drawImage(padding - c*w_piece, padding - r*h_piece, self.image)
                
                # Apply path mask
                mask_path = path.translated(padding, padding)
                pnt.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
                pnt.setPen(Qt.PenStyle.NoPen) 
                pnt.fillPath(mask_path, QBrush(Qt.GlobalColor.white))
                pnt.end()
                
                # Align correct_pos to integers
                cx = int(c*w_piece - padding + board_offset.x())
                cy = int(r*h_piece - padding + board_offset.y())
                
                piece = JigsawPiece(QPixmap.fromImage(img_out), r, c, QPointF(cx, cy), mask_path)
                piece.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
                self.addItem(piece)
                self.pieces.append(piece)
            
        # Create preview item (semi-transparent guide)
        self.preview_item = QGraphicsPixmapItem(QPixmap.fromImage(self.image))
        self.preview_item.setPos(board_offset)
        self.preview_item.setZValue(config.DRAGGING_Z_OFFSET * 2)
        self.preview_item.setOpacity(config.PREVIEW_OPACITY)
        self.preview_item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.preview_item.hide()
        self.addItem(self.preview_item)

        self._repack_tray()

    def scroll_tray(self, delta: float):
        """Updates tray scroll offset and repacks."""
        self.tray_scroll_offset += delta
        if self.pieces:
            in_tray = [p for p in self.pieces if p.is_in_tray]
            total_w = len(in_tray) * config.TRAY_SLOT_WIDTH
            max_scroll = max(0, total_w - self.tray_rect.width() + 100)
            self.tray_scroll_offset = max(-max_scroll, min(0, self.tray_scroll_offset))
        self._repack_tray()

    def show_preview(self):
        """Displays the reference image at full opacity."""
        if self.preview_item:
            self.preview_item.setOpacity(1.0)
            self.preview_item.show()
            for p in self.pieces: p.hide()

    def hide_preview(self):
        """Hides the reference image and restores pieces."""
        if self.preview_item:
            self.preview_item.hide()
            for p in self.pieces: p.show()

    def _repack_tray(self):
        """Renders the tray area with currently available pieces."""
        tray_pieces = [p for p in self.pieces if p.is_in_tray and not p.is_locked]
        start_x = config.TRAY_START_X + self.tray_scroll_offset
        y_pos = self.tray_rect.top() + config.TRAY_PIECE_Y_OFFSET
        for i, p in enumerate(tray_pieces):
            p.setPos(start_x + i * config.TRAY_SLOT_WIDTH, y_pos)
            p.setScale(p.tray_scale)

    def mousePressEvent(self, event):
        """Handles piece selection and Z-ordering."""
        pos = event.scenePos()
        trans = self.views()[0].viewportTransform() if self.views() else QTransform()
        item = self.itemAt(pos, trans)
        if isinstance(item, JigsawPiece) and not item.is_locked:
            max_z = max((p.zValue() for p in self.pieces), default=1)
            item.setZValue(max_z + 1)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handles piece movement and tray/board transitions."""
        super().mouseMoveEvent(event)
        moved_clusters = set()
        for item in self.selectedItems():
            if isinstance(item, JigsawPiece) and not item.is_locked:
                cid = id(item.cluster)
                if cid in moved_clusters: continue
                
                # Check tray <-> board transition
                if item.y() < self.tray_rect.top() - 20 and item.is_in_tray:
                    for p in item.cluster:
                        p.setScale(1.0)
                        p.is_in_tray = False
                    self._repack_tray()
                elif item.y() > self.tray_rect.top() and not item.is_in_tray:
                    for p in item.cluster:
                        p.setScale(p.tray_scale)
                        p.is_in_tray = True
                    self._repack_tray()

                # Sync cluster movement
                for other in item.cluster:
                    if other != item:
                        other.setPos(item.pos() + (other.correct_pos - item.correct_pos))
                moved_clusters.add(cid)

    def mouseReleaseEvent(self, event):
        """Handles piece snapping and cluster merging."""
        super().mouseReleaseEvent(event)
        for item in self.selectedItems():
            if isinstance(item, JigsawPiece) and not item.is_locked:
                # Snap to absolute board position
                if (item.pos() - item.correct_pos).manhattanLength() < config.SNAP_THRESHOLD:
                    self._snap_piece_to_board(item)
                    continue
                # Snap to neighbors
                for other in self.pieces:
                    if other == item or other.is_in_tray: continue
                    rel = item.correct_pos - other.correct_pos
                    if (item.pos() - (other.pos() + rel)).manhattanLength() < config.SNAP_THRESHOLD:
                        item.setPos(other.pos() + rel)
                        if other not in item.cluster:
                            new_c = list(set(item.cluster + other.cluster))
                            for p in new_c: p.cluster = new_c
                        if other.is_locked: self._snap_piece_to_board(item)
                        break

    def _snap_piece_to_board(self, item):
        """Locks a piece or cluster onto its final correct position."""
        for p in item.cluster:
            p.setPos(p.correct_pos)
            p.is_locked = True
            p.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            p.setZValue(config.LOCKED_Z_VALUE)
            p.is_in_tray = False
            p.setScale(1.0)
        self.check_win()

    def check_win(self):
        """Polls game state for victory condition."""
        if all(p.is_locked for p in self.pieces):
            print("Winner!")

    def _add_tab(self, path, w, h, tab_size, direction, side):
        """Internal helper to add a jigsaw tab (concave or convex) to a side."""
        mx, my = w / 2, h / 2
        ts, neck = tab_size * direction, tab_size * 0.5
        if side == "top":
            path.lineTo(mx - neck, 0)
            path.cubicTo(mx - neck, ts*0.2, mx - tab_size*0.8, ts*0.2, mx - tab_size, ts)
            path.cubicTo(mx - tab_size, ts*1.3, mx + tab_size, ts*1.3, mx + tab_size, ts)
            path.cubicTo(mx + tab_size*0.8, ts*0.2, mx + neck, ts*0.2, mx + neck, 0)
            path.lineTo(w, 0)
        elif side == "right":
            path.lineTo(w, my - neck)
            path.cubicTo(w + ts*0.2, my - neck, w + ts*0.2, my - tab_size*0.8, w + ts, my - tab_size)
            path.cubicTo(w + ts*1.3, my - tab_size, w + ts*1.3, my + tab_size, w + ts, my + tab_size)
            path.cubicTo(w + ts*0.2, my + tab_size*0.8, w + ts*0.2, my + neck, w, my + neck)
            path.lineTo(w, h)
        elif side == "bottom":
            path.lineTo(mx + neck, h)
            path.cubicTo(mx + neck, h + ts*0.2, mx + tab_size*0.8, h + ts*0.2, mx + tab_size, h + ts)
            path.cubicTo(mx + tab_size, h + ts*1.3, mx - tab_size, h + ts*1.3, mx - tab_size, h + ts)
            path.cubicTo(mx - tab_size*0.8, h + ts*0.2, mx - neck, h + ts*0.2, mx - neck, h)
            path.lineTo(0, h)
        elif side == "left":
            path.lineTo(0, my + neck)
            path.cubicTo(-ts*0.2, my + neck, -ts*0.2, my + tab_size*0.8, -ts, my + tab_size)
            path.cubicTo(-ts*1.3, my + tab_size, -ts*1.3, my - tab_size, -ts, my - tab_size)
            path.cubicTo(-ts*0.2, my - tab_size*0.8, -ts*0.2, my - neck, 0, my - neck)
            path.lineTo(0, 0)

    def drawBackground(self, painter, rect):
        """Renders the scene background and layout guides."""
        painter.fillRect(rect, config.BG_COLOR)
        painter.fillRect(self.tray_rect, config.TRAY_BG_COLOR)
        painter.setPen(QPen(config.SEPARATOR_COLOR, 2))
        painter.drawLine(0, self.tray_rect.top(), self.sceneRect().width(), self.tray_rect.top())
        if self.image:
            off_x = (self.board_rect.width() - self.image.width()) / 2
            off_y = (self.board_rect.height() - self.image.height()) / 2
            painter.setPen(QPen(config.GUIDE_COLOR, 2, Qt.PenStyle.DashLine))
            painter.drawRect(off_x, off_y, self.image.width(), self.image.height())
