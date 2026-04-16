"""
Jigsaw Qt - Main Application Entry Point
A high-performance, responsive jigsaw puzzle game.
"""

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QGraphicsView, 
                             QLabel, QFrame, QComboBox)
from PySide6.QtGui import QColor, QPalette, QPainter, QWheelEvent, QGuiApplication, QIcon
from PySide6.QtCore import Qt, QRectF

import config
from board import JigsawBoard

class ModernButton(QPushButton):
    """Stylish UI button with interactive hover states."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.hover_callback = None
        self.leave_callback = None
        self.setStyleSheet(config.theme.UI_STYLE)

    def enterEvent(self, event):
        if self.hover_callback: self.hover_callback()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.leave_callback: self.leave_callback()
        super().leaveEvent(event)

class JigsawView(QGraphicsView):
    """View container for the Jigsaw graphics scene."""
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background: transparent; border: none;")

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        self.scene().scroll_tray(delta)

class JigsawApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.WINDOW_TITLE)
        
        # Start Maximized for best experience as per user request
        self.setWindowState(Qt.WindowState.WindowMaximized)
        
        self.scene = JigsawBoard()
        self.scene.on_completion_changed = self.update_progress
        
        # Set Window Icon
        icon_path = os.path.join(os.path.dirname(__file__), "io.github.hthienloc.JigsawQt.png")
        if not os.path.exists(icon_path):
            # Fallback for Flatpak or system installation
            icon_path = "/app/share/icons/hicolor/scalable/apps/io.github.hthienloc.JigsawQt.png"
        
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        elif QIcon.hasThemeIcon("io.github.hthienloc.JigsawQt"):
            self.setWindowIcon(QIcon.fromTheme("io.github.hthienloc.JigsawQt"))
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setStyleSheet(f"background-color: {config.theme.HEADER_BG.name()}; border-bottom: 1px solid {config.theme.SEPARATOR_COLOR.name()};")
        header.setFixedHeight(64)
        h_layout = QHBoxLayout(header)
        
        brand = QLabel("JIGSAW QT")
        brand.setStyleSheet("font-size: 18px; font-weight: 800; color: #4fc3f7; letter-spacing: 2px;")
        h_layout.addWidget(brand)
        h_layout.addSpacing(20)

        btn_load = ModernButton("Browse...")
        btn_load.clicked.connect(self._open_file)
        h_layout.addWidget(btn_load)
        
        # Category Dropdown
        self.combo_samples = QComboBox()
        self.combo_samples.setFixedWidth(200)
        self.combo_samples.setStyleSheet(f"""
            QComboBox {{
                background-color: {config.theme.color(QPalette.ColorRole.Button).name()};
                color: {config.theme.TEXT_COLOR.name()};
                padding: 8px;
                border-radius: 4px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {config.theme.BG_COLOR.name()};
                color: {config.theme.TEXT_COLOR.name()};
                selection-background-color: {config.theme.EMPHASIS_COLOR.name()};
            }}
        """)
        self.combo_samples.addItem("Select Sample image...", None)
        self._populate_samples()
        self.combo_samples.currentIndexChanged.connect(self._on_sample_selected)
        h_layout.addWidget(self.combo_samples)

        # Difficulty Dropdown
        self.combo_diff = QComboBox()
        self.combo_diff.setFixedWidth(100)
        self.combo_diff.setStyleSheet(self.combo_samples.styleSheet())
        for level, count in config.DIFFICULTY_PRESETS.items():
            self.combo_diff.addItem(f"{level} ({count})", count)
        self.combo_diff.setCurrentText(f"Normal ({config.TARGET_PIECE_COUNT})")
        self.combo_diff.currentIndexChanged.connect(self._on_difficulty_selected)
        h_layout.addWidget(self.combo_diff)

        self.btn_preview = ModernButton("GUIDE")
        self.btn_preview.hover_callback = self.scene.show_preview
        self.btn_preview.leave_callback = self.scene.hide_preview
        h_layout.addWidget(self.btn_preview)

        self.btn_hint = ModernButton("HINT (H)")
        self.btn_hint.clicked.connect(self.scene.toggle_hint)
        h_layout.addWidget(self.btn_hint)

        self.btn_edges = ModernButton("EDGES (E)")
        self.btn_edges.setCheckable(True)
        self.btn_edges.clicked.connect(self.scene.toggle_edge_filter)
        h_layout.addWidget(self.btn_edges)

        self.btn_retrieve = ModernButton("RETRIEVE (R)")
        self.btn_retrieve.clicked.connect(self.scene.return_unlocked_to_tray)
        h_layout.addWidget(self.btn_retrieve)

        self.btn_shuffle = ModernButton("SHUFFLE (S)")
        self.btn_shuffle.clicked.connect(self.scene.shuffle_tray)
        h_layout.addWidget(self.btn_shuffle)

        h_layout.addSpacing(20)
        self.progress_label = QLabel("COMPLETE: 0%")
        self.progress_label.setStyleSheet("color: #4fc3f7; font-weight: 700; font-size: 14px; min-width: 120px;")
        h_layout.addWidget(self.progress_label)

        h_layout.addStretch()

        layout.addWidget(header)

        self.view = JigsawView(self.scene)
        layout.addWidget(self.view)

    def resizeEvent(self, event):
        """Responsive layout: Updates the graphics engine on window change."""
        super().resizeEvent(event)
        w, h = self.view.width(), self.view.height()
        if w <= 0 or h <= 0: return
        
        self.scene.setSceneRect(0, 0, w, h)
        self.scene.update_layout(w, h)

    def _populate_samples(self):
        """Scans samples/ directory for categorized images."""
        samples_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
        if not os.path.exists(samples_root): return
        
        for category in sorted(os.listdir(samples_root)):
            cat_path = os.path.join(samples_root, category)
            if os.path.isdir(cat_path):
                for img_file in sorted(os.listdir(cat_path)):
                    if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        display_name = f"{category.capitalize()}: {os.path.splitext(img_file)[0].capitalize()}"
                        full_path = os.path.join(cat_path, img_file)
                        self.combo_samples.addItem(display_name, full_path)

    def _on_sample_selected(self, index):
        path = self.combo_samples.itemData(index)
        if path:
            self.scene.load_image(path)
            self.update_progress()

    def _on_difficulty_selected(self, index):
        count = self.combo_diff.itemData(index)
        if count:
            self.scene.target_piece_count = count
            self.scene.reload_current()
            self.update_progress()

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
        if path: 
            self.scene.load_image(path)
            self.update_progress()


    def update_progress(self):
        pct = self.scene.get_completion_percentage()
        self.progress_label.setText(f"COMPLETE: {pct}%")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_H:
            self.scene.toggle_hint()
        elif event.key() == Qt.Key.Key_G:
            # Trigger toggle or just show? Guide is hover-based usually.
            # Let's toggle is_hint_active via G as well for convenience.
            self.scene.toggle_hint()
        elif event.key() == Qt.Key.Key_E:
            self.btn_edges.setChecked(not self.btn_edges.isChecked())
            self.scene.toggle_edge_filter()
        elif event.key() == Qt.Key.Key_S:
            self.scene.shuffle_tray()
        elif event.key() == Qt.Key.Key_R:
            self.scene.return_unlocked_to_tray()
        elif event.key() == Qt.Key.Key_F12:
            self.scene.debug_mode = not self.scene.debug_mode
            self.scene.update()
        super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Inherit system palette
    app.setPalette(QGuiApplication.palette())
    app.setFont(config.theme.MAIN_FONT)
    
    window = JigsawApp()
    window.show()
    sys.exit(app.exec())
