"""
JigsawBoard Module - Core Logic and Rendering
Handles high-precision puzzle piece generation and blending.
"""

import random
import math
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem
from PySide6.QtGui import QPainterPath, QImage, QPixmap, QPainter, QColor, QPen, QBrush, QTransform
from PySide6.QtCore import Qt, QPointF, QRectF

import config
from piece import JigsawPiece

class ClusterHighlightItem(QGraphicsItem):
    """Special item that draws a glowing border around an entire cluster."""
    def __init__(self, pieces, parent=None):
        super().__init__(parent)
        self.pieces = pieces
        self.setZValue(995) 
        self.setVisible(False)

    def boundingRect(self):
        if not self.pieces: return QRectF()
        rect = self.pieces[0].sceneBoundingRect()
        for p in self.pieces[1:]: rect = rect.united(p.sceneBoundingRect())
        return self.mapFromScene(rect).boundingRect().adjusted(-10,-10,10,10)

    def paint(self, painter, option, widget=None):
        if not self.pieces or any(p.is_in_tray for p in self.pieces): return
        path = QPainterPath()
        for p in self.pieces:
            # Shift path to avoid sub-pixel bleed
            p_path = p.mapToScene(p.mask_path)
            path = path.united(self.mapFromScene(p_path))
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(config.SELECTION_COLOR, 3) # Clean cyan glow
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(path)

class JigsawBoard(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pieces = []
        self.original_image = None
        self.rows = 0
        self.cols = 0
        self.tray_rect = QRectF()
        self.board_rect = QRectF()
        self.highlight_item = None
        self.preview_item = None
        self.tray_scroll_offset = 0
        
        self.creation_w = config.DEFAULT_WIDTH
        self.creation_h = config.DEFAULT_HEIGHT

    def load_image(self, image_path: str):
        img_obj = QImage(image_path)
        if img_obj.isNull(): return
        self.original_image = img_obj
        img_aspect = self.original_image.width() / self.original_image.height()
        self.rows = max(2, round(math.sqrt(config.TARGET_PIECE_COUNT / img_aspect)))
        self.cols = max(2, round(config.TARGET_PIECE_COUNT / self.rows))
        
        if self.width() > 0:
            self.creation_w, self.creation_h = self.width(), self.height()
        self._create_puzzle(self.creation_w, self.creation_h)

    def _create_puzzle(self, w, h):
        self.clear()
        self.pieces = []
        
        tray_h = h * config.TRAY_RATIO
        board_h = h - tray_h
        self.tray_rect = QRectF(0, h - tray_h, w, tray_h)
        self.board_rect = QRectF(0, 0, w, board_h)
        
        target_w = w * config.BOARD_USE_RATIO
        target_h = board_h * config.BOARD_USE_RATIO
        scaled_img = self.original_image.scaled(int(target_w), int(target_h), 
                                               Qt.AspectRatioMode.KeepAspectRatio, 
                                               Qt.TransformationMode.SmoothTransformation)
        
        # FLOAT PRECISION PIECE SIZES to avoid gaps
        pw = scaled_img.width() / self.cols
        ph = scaled_img.height() / self.rows
        
        tab_size = min(pw, ph) * config.TAB_SIZE_RATIO
        # Dilate masks slightly (0.5px) to over-fill and blend edges
        padding = math.ceil(tab_size) + config.OVERSCAN_PADDING
        
        off_x = (w - scaled_img.width()) / 2
        off_y = (board_h - scaled_img.height()) / 2

        h_tabs = [[random.choice([1, -1]) for _ in range(self.cols-1)] for _ in range(self.rows)]
        v_tabs = [[random.choice([1, -1]) for _ in range(self.cols)] for _ in range(self.rows-1)]

        for r in range(self.rows):
            for c in range(self.cols):
                path = QPainterPath(); path.moveTo(0, 0)
                # Use floats for lineTo/cubicTo directly
                if r > 0: self._add_tab(path, pw, ph, tab_size, -v_tabs[r-1][c], "top")
                else: path.lineTo(pw, 0)
                if c < self.cols-1: self._add_tab(path, pw, ph, tab_size, h_tabs[r][c], "right")
                else: path.lineTo(pw, ph)
                if r < self.rows-1: self._add_tab(path, pw, ph, tab_size, v_tabs[r][c], "bottom")
                else: path.lineTo(0, ph)
                if c > 0: self._add_tab(path, pw, ph, tab_size, -h_tabs[r][c-1], "left")
                else: path.lineTo(0, 0)

                pix = QPixmap(int(pw + 2*padding), int(ph + 2*padding)); pix.fill(Qt.GlobalColor.transparent)
                pnt = QPainter(pix); pnt.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                # Slice with sub-pixel offsets
                pnt.drawImage(QRectF(padding, padding, pw, ph), scaled_img, QRectF(c*pw, r*ph, pw, ph))
                # Fill outside area to ensure tab content exists
                pnt.drawImage(0, 0, scaled_img, int(c*pw - padding), int(r*ph - padding), int(pw + 2*padding), int(ph + 2*padding))
                pnt.end()
                
                cx, cy = c * pw - padding + off_x, r * ph - padding + off_y
                piece = JigsawPiece(pix, r, c, QPointF(cx, cy), path.translated(padding, padding))
                piece.tray_scale = config.TRAY_SLOT_WIDTH / pix.width()
                piece.tray_scale = min(piece.tray_scale, 0.5)
                self.addItem(piece); self.pieces.append(piece)

        self.preview_item = QGraphicsPixmapItem(QPixmap.fromImage(scaled_img))
        self.preview_item.setPos(off_x, off_y); self.preview_item.setZValue(999); self.preview_item.setOpacity(config.PREVIEW_OPACITY)
        self.preview_item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.preview_item.hide(); self.addItem(self.preview_item)
        
        self.highlight_item = ClusterHighlightItem([]); self.addItem(self.highlight_item)
        self._repack_tray()

    def update_layout(self, w, h):
        if w <= 0 or not self.pieces: return
        self.tray_rect = QRectF(0, h - h*config.TRAY_RATIO, w, h*config.TRAY_RATIO)
        self.board_rect = QRectF(0, 0, w, h - h*config.TRAY_RATIO)
        self._repack_tray()

    def _add_tab(self, path, w, h, tab_size, direction, side):
        mx, my = w / 2.0, h / 2.0
        ts = tab_size * direction
        if side == "top":
            ts = -ts
            path.lineTo(mx - tab_size*0.5, 0)
            path.cubicTo(mx - tab_size*0.5, ts*0.2, mx - tab_size*0.8, ts*0.4, mx - tab_size*0.8, ts)
            path.cubicTo(mx - tab_size*0.8, ts*1.3, mx + tab_size*0.8, ts*1.3, mx + tab_size*0.8, ts)
            path.cubicTo(mx + tab_size*0.8, ts*0.4, mx + tab_size*0.5, ts*0.2, mx + tab_size*0.5, 0)
            path.lineTo(w, 0)
        elif side == "right":
            path.lineTo(w, my - tab_size*0.5)
            path.cubicTo(w + ts*0.2, my - tab_size*0.5, w + ts*0.4, my - tab_size*0.8, w + ts, my - tab_size*0.8)
            path.cubicTo(w + ts*1.3, my - tab_size*0.8, w + ts*1.3, my + tab_size*0.8, w + ts, my + tab_size*0.8)
            path.cubicTo(w + ts*0.4, my + tab_size*0.8, w + ts*0.2, my + tab_size*0.5, w, my + tab_size*0.5)
            path.lineTo(w, h)
        elif side == "bottom":
            path.lineTo(mx + tab_size*0.5, h)
            path.cubicTo(mx + tab_size*0.5, h + ts*0.2, mx + tab_size*0.8, h + ts*0.4, mx + tab_size*0.8, h + ts)
            path.cubicTo(mx + tab_size*0.8, h + ts*1.3, mx - tab_size*0.8, h + ts*1.3, mx - tab_size*0.8, h + ts)
            path.cubicTo(mx - tab_size*0.8, h + ts*0.4, mx - tab_size*0.5, h + ts*0.2, mx - tab_size*0.5, h)
            path.lineTo(0, h)
        elif side == "left":
            ts = -ts
            path.lineTo(0, my + tab_size*0.5)
            path.cubicTo(ts*0.2, my + tab_size*0.5, ts*0.4, my + tab_size*0.8, ts, my + tab_size*0.8)
            path.cubicTo(ts*1.3, my + tab_size*0.8, ts*1.3, my - tab_size*0.8, ts, my - tab_size*0.8)
            path.cubicTo(ts*0.4, my - tab_size*0.8, ts*0.2, my - tab_size*0.5, 0, my - tab_size*0.5)
            path.lineTo(0, 0)

    def scroll_tray(self, delta: float):
        self.tray_scroll_offset += delta
        if self.pieces:
            in_tray = [p for p in self.pieces if p.is_in_tray]
            total_w = len(in_tray) * config.TRAY_SLOT_WIDTH
            max_scroll = max(0, total_w - self.tray_rect.width() + 100)
            self.tray_scroll_offset = max(-max_scroll, min(0, self.tray_scroll_offset))
        self._repack_tray()

    def show_preview(self):
        if self.preview_item: 
            self.preview_item.setOpacity(1.0); self.preview_item.show()
            for p in self.pieces: p.hide()

    def hide_preview(self):
        if self.preview_item: 
            self.preview_item.hide()
            for p in self.pieces: p.show()

    def _repack_tray(self):
        tray_pieces = [p for p in self.pieces if p.is_in_tray and not p.is_locked]
        start_x = config.TRAY_START_X + self.tray_scroll_offset
        y_pos = self.tray_rect.top() + (self.tray_rect.height() * config.TRAY_PIECE_Y_OFFSET)
        for i, p in enumerate(tray_pieces):
            p.setPos(start_x + i * config.TRAY_SLOT_WIDTH, y_pos)
            p.setScale(p.tray_scale)

    def mousePressEvent(self, event):
        pos = event.scenePos()
        trans = self.views()[0].viewportTransform() if self.views() else QTransform()
        item = self.itemAt(pos, trans)
        for scene_item in self.items(): scene_item.setSelected(False)
        if isinstance(item, JigsawPiece) and not item.is_locked:
            for p in item.cluster: p.setSelected(True)
            max_z = max((p.zValue() for p in self.pieces), default=1)
            for p in item.cluster: p.setZValue(max_z + 1)
            if self.highlight_item:
                self.highlight_item.pieces = item.cluster
                self.highlight_item.prepareGeometryChange(); self.highlight_item.setVisible(True); self.highlight_item.update()
        else:
            if self.highlight_item: self.highlight_item.setVisible(False)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self._update_highlight_pos()
        moved_clusters = set()
        for item in self.selectedItems():
            if isinstance(item, JigsawPiece) and not item.is_locked:
                cid = id(item.cluster)
                if cid in moved_clusters: continue
                if item.y() < self.tray_rect.top() - 20 and item.is_in_tray:
                    for p in item.cluster: p.setScale(1.0); p.is_in_tray = False
                    self._repack_tray()
                elif item.y() > self.tray_rect.top() and not item.is_in_tray:
                    for p in item.cluster: p.setScale(p.tray_scale); p.is_in_tray = True
                    self._repack_tray()
                for other in item.cluster:
                    if other != item: other.setPos(item.pos() + (other.correct_pos - item.correct_pos))
                moved_clusters.add(cid)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        for item in self.selectedItems():
            if isinstance(item, JigsawPiece) and not item.is_locked:
                if (item.pos() - item.correct_pos).manhattanLength() < config.SNAP_THRESHOLD:
                    self._snap_piece_to_board(item)
                    continue
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
        self._update_highlight_pos()

    def _update_highlight_pos(self):
        if self.highlight_item and self.highlight_item.isVisible():
            self.highlight_item.prepareGeometryChange(); self.highlight_item.update()

    def _snap_piece_to_board(self, item):
        for p in item.cluster:
            p.setPos(p.correct_pos); p.is_locked = True
            p.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            p.setZValue(config.LOCKED_Z_VALUE); p.is_in_tray = False; p.setScale(1.0)
        if self.highlight_item: self.highlight_item.setVisible(False)
        self.check_win()

    def check_win(self):
        if all(p.is_locked for p in self.pieces): print("Winner!")

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, config.BG_COLOR)
        painter.fillRect(self.board_rect, config.BOARD_AREA_BG)
        painter.fillRect(self.tray_rect, config.TRAY_BG_COLOR)
        painter.setPen(QPen(config.SEPARATOR_COLOR, 2))
        painter.drawLine(0, self.tray_rect.top(), self.sceneRect().width(), self.tray_rect.top())
        if self.preview_item:
            pr = self.preview_item.pixmap().rect()
            guide_rect = QRectF(self.preview_item.pos().x(), self.preview_item.pos().y(), pr.width(), pr.height())
            painter.setPen(QPen(config.GUIDE_COLOR, 2, Qt.PenStyle.DashLine))
            painter.drawRect(guide_rect)
