"""
Jigsaw Qt - Main Application Entry Point
A high-performance, responsive jigsaw puzzle game.
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
    """Stylish UI button with interactive hover states."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.hover_callback = None
        self.leave_callback = None
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.15);
                color: #ffffff;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.18);
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
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setStyleSheet("background-color: #1a1a1a; border-bottom: 1px solid #2a2a2a;")
        header.setFixedHeight(64)
        h_layout = QHBoxLayout(header)
        
        brand = QLabel("JIGSAW QT")
        brand.setStyleSheet("font-size: 18px; font-weight: 800; color: #4fc3f7; letter-spacing: 2px;")
        h_layout.addWidget(brand)
        h_layout.addSpacing(20)

        self.btn_load = ModernButton("OPEN IMAGE")
        self.btn_load.clicked.connect(self.select_image)
        h_layout.addWidget(self.btn_load)

        self.btn_preview = ModernButton("GUIDE")
        self.btn_preview.hover_callback = self.scene.show_preview
        self.btn_preview.leave_callback = self.scene.hide_preview
        h_layout.addWidget(self.btn_preview)

        h_layout.addStretch()
        
        self.samples_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")
        if os.path.exists(self.samples_dir):
            files = sorted([f for f in os.listdir(self.samples_dir) if f.lower().endswith((".png", ".jpg"))])
            for f in files[:5]:
                label = os.path.splitext(f)[0].upper()
                btn = ModernButton(label)
                btn.clicked.connect(lambda checked=False, img=f: self.load_sample(img))
                h_layout.addWidget(btn)

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

    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
        if path: self.scene.load_image(path)

    def load_sample(self, filename):
        path = os.path.join(self.samples_dir, filename)
        if os.path.exists(path):
            self.scene.load_image(path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(18, 18, 18))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.Highlight, QColor(79, 195, 247))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    window = JigsawApp()
    window.show()
    sys.exit(app.exec())
