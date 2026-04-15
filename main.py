"""
Jigsaw Qt - Main Application Entry Point
A high-performance, window-responsive puzzle game built with PySide6.
"""

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QGraphicsView, 
                             QLabel, QFrame)
from PySide6.QtGui import QColor, QPalette, QPainter, QWheelEvent
from PySide6.QtCore import Qt, QRectF

import config
from board import JigsawBoard

class ModernButton(QPushButton):
    """Stylish UI button with hover states for a premium feel."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.hover_callback = None
        self.leave_callback = None
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                color: #ffffff;
                padding: 10px 24px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(79, 195, 247, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(79, 195, 247, 0.2);
            }
        """)

    def enterEvent(self, event):
        if self.hover_callback: self.hover_callback()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.leave_callback: self.leave_callback()
        super().leaveEvent(event)

class JigsawView(QGraphicsView):
    """Custom view providing stable framing and wheel-based tray interaction."""
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background: transparent; border: none;")

    def wheelEvent(self, event: QWheelEvent):
        """Directs mouse wheel input to the horizontal tray scroll logic."""
        delta = event.angleDelta().y()
        self.scene().scroll_tray(delta)

class JigsawApp(QMainWindow):
    """Main Application Controller."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.WINDOW_TITLE)
        self.resize(config.DEFAULT_WIDTH, config.DEFAULT_HEIGHT)
        
        self.scene = JigsawBoard()
        
        # UI Layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar
        header = QFrame()
        header.setStyleSheet("background-color: #1a1a1a; border-bottom: 1px solid #2a2a2a;")
        header.setFixedHeight(64)
        h_layout = QHBoxLayout(header)
        
        brand = QLabel("JIGSAW QT")
        brand.setStyleSheet("font-size: 18px; font-weight: 800; color: #4fc3f7; letter-spacing: 2px;")
        h_layout.addWidget(brand)
        h_layout.addSpacing(30)

        self.btn_load = ModernButton("LOAD IMAGE")
        self.btn_load.clicked.connect(self.select_image)
        h_layout.addWidget(self.btn_load)

        self.btn_preview = ModernButton("GUIDE VIEW")
        self.btn_preview.hover_callback = self.scene.show_preview
        self.btn_preview.leave_callback = self.scene.hide_preview
        h_layout.addWidget(self.btn_preview)

        h_layout.addStretch()
        
        # Load sample thumbnails
        self.samples_dir = "/home/loccun/.gemini/antigravity/brain/ce75c0c6-810e-4799-bde2-968a96776fe6/"
        if os.path.exists(self.samples_dir):
            samples = [f for f in os.listdir(self.samples_dir) if f.endswith(".png")]
            for s in samples[:3]:
                btn = ModernButton(f"SAMPLE {s.split('_')[0][-1]}")
                btn.clicked.connect(lambda checked=False, img=s: self.load_sample(img))
                h_layout.addWidget(btn)

        layout.addWidget(header)

        # Game Workspace
        self.view = JigsawView(self.scene)
        layout.addWidget(self.view)

    def resizeEvent(self, event):
        """Responsive layout update."""
        super().resizeEvent(event)
        new_size = event.size()
        self.scene.setSceneRect(0, 0, new_size.width(), self.view.height())
        if self.scene.pieces:
            # Update tray boundary to match new window height
            self.scene.tray_rect = QRectF(0, new_size.height() - config.TRAY_HEIGHT - 64, 
                                         new_size.width(), config.TRAY_HEIGHT)
            self.scene._repack_tray()

    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
        if path: self.scene.load_image(path)

    def load_sample(self, filename):
        path = os.path.join(self.samples_dir, filename)
        self.scene.load_image(path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Global Dark Palette
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(18, 18, 18))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(18, 18, 18))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(79, 195, 247))
    palette.setColor(QPalette.Highlight, QColor(79, 195, 247))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    window = JigsawApp()
    window.show()
    sys.exit(app.exec())
