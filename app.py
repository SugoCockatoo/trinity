# main.py
# Trinity IDE - Neon Forge Edition
# Architecture: High-Performance Asynchronous Runtime (PyQt5)

import sys
import os
import json
import math
import tempfile
import shutil
from pathlib import Path

from PyQt5.QtCore import (
    Qt, QProcess, QProcessEnvironment, QDir, QRect, QSize, QRegExp,
    QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty, QObject
)
from PyQt5.QtGui import (
    QFont, QColor, QTextFormat, QPainter, QPixmap,
    QSyntaxHighlighter, QTextCharFormat, QLinearGradient, QPen,
    QPalette, QBrush, QFontDatabase
)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileSystemModel, QTreeView, QPlainTextEdit, QTextEdit,
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QAction, QFileDialog,
    QSplitter, QMessageBox, QToolBar, QLabel, QComboBox, QDockWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog, QSizePolicy,
    QGraphicsOpacityEffect, QFrame
)

# ─────────────────────────── Logo Path ───────────────────────────
# Set this to the path of your logo image (PNG, JPG, SVG, etc.)
# Leave as empty string to use the animated text fallback.
LOGO_IMAGE_PATH = ""   # e.g. r"C:\assets\trinity_logo.png" or "/home/user/logo.png"


ORANGE_FIRE  = "#FF6B00"
ORANGE_GLOW  = "#FF8C38"
ORANGE_SOFT  = "#FFB36B"
BLUE_DEEP    = "#0B2CFF"
BLUE_MID     = "#1E66F5"
BLUE_SKY     = "#38BFFF"
BLUE_ICE     = "#7DD3FC"
BG_VOID      = "#080810"
BG_DARK      = "#0D0D18"
BG_PANEL     = "#10101E"
BG_SURFACE   = "#14142A"
BG_ELEVATED  = "#1A1A30"
BORDER_DIM   = "#1E1E38"
BORDER_GLOW  = "#2A2A50"
TEXT_PRIMARY  = "#E8E8F8"
TEXT_SECONDARY= "#8888BB"
TEXT_MUTED   = "#44445A"

# Syntax highlight palette
SYN_KEYWORD   = "#FF6B00"   # orange — keywords pop
SYN_FUNCTION  = "#38BFFF"   # sky blue — function names
SYN_CLASS     = "#FFB36B"   # soft orange — classes
SYN_STRING    = "#4ADE80"   # green — strings
SYN_COMMENT   = "#555577"   # muted purple-grey
SYN_NUMBER    = "#C084FC"   # violet — numbers
SYN_OPERATOR  = "#1E66F5"   # blue — operators
SYN_BUILTIN   = "#FB923C"   # warm orange — builtins
SYN_DECORATOR = "#FF6B00"   # orange — decorators
SYN_SELF      = "#60A5FA"   # blue — self/cls
SYN_VARIABLE  = "#CBD5E1"   # light slate for general vars
SYN_TYPE      = "#38BFFF"   # sky blue for type hints
SYN_INDENT    = "#1E1E38"   # subtle indent guides


# ─────────────────────────── Utility ───────────────────────────

def is_text_or_json(path: str) -> bool:
    ext = Path(path).suffix.lower()
    return ext in {'.py', '.txt', '.md', '.json', '.cpp', '.h', '.c', '.hpp', '.js', '.ts', '.html', '.css'}

def detect_language(path: str) -> str:
    ext = Path(path).suffix.lower()
    return {
        '.py': 'Python', '.cpp': 'C++', '.cc': 'C++', '.c': 'C++',
        '.h': 'C++', '.hpp': 'C++',
    }.get(ext, 'Python')


# ─────────────────────────── Line Number Area ───────────────────────────

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor
        self.setFixedWidth(self.code_editor.line_number_area_width())

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


# ─────────────────────────── Trinity Editor ───────────────────────────

class TrinityEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

        font = QFont("JetBrains Mono", 11)
        if font.exactMatch():
            self.setFont(font)
        else:
            for fallback in ["Cascadia Code", "Fira Code", "Consolas", "Menlo", "Courier New"]:
                f = QFont(fallback, 11)
                if f.exactMatch():
                    self.setFont(f)
                    break
            else:
                self.setFont(QFont("Courier New", 11))

        self.setLineWrapMode(QPlainTextEdit.NoWrap)

        # Tab = 4 spaces
        try:
            self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)
        except AttributeError:
            self.setTabStopWidth(self.fontMetrics().horizontalAdvance(' ') * 4)

        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background: {BG_DARK};
                color: {TEXT_PRIMARY};
                border: none;
                selection-background-color: #1E3A5F;
                padding-left: 6px;
            }}
        """)

    def line_number_area_width(self):
        digits = max(1, len(str(max(1, self.blockCount()))))
        space = 20 + self.fontMetrics().horizontalAdvance('9') * digits
        return space + 16

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def highlight_current_line(self):
        extra = []
        if not self.isReadOnly():
            sel = QTextEdit.ExtraSelection()
            sel.format.setBackground(QColor("#131328"))
            sel.format.setProperty(QTextFormat.FullWidthSelection, True)
            sel.cursor = self.textCursor()
            sel.cursor.clearSelection()
            extra.append(sel)
        self.setExtraSelections(extra)

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        # Gradient side-panel
        grad = QLinearGradient(0, 0, self.line_number_area.width(), 0)
        grad.setColorAt(0, QColor(BG_VOID))
        grad.setColorAt(1, QColor(BG_DARK))
        painter.fillRect(event.rect(), QBrush(grad))

        # Right accent line
        painter.setPen(QPen(QColor(BORDER_GLOW), 1))
        painter.drawLine(self.line_number_area.width() - 1, event.rect().top(),
                         self.line_number_area.width() - 1, event.rect().bottom())

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        current_line = self.textCursor().blockNumber()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                if current_line == block_number:
                    painter.setPen(QColor(ORANGE_GLOW))
                    # Highlight background for current line number
                    painter.fillRect(0, top, self.line_number_area.width() - 1,
                                     self.fontMetrics().height(), QColor("#1A0F00"))
                else:
                    painter.setPen(QColor(TEXT_MUTED))
                painter.drawText(
                    0, top,
                    self.line_number_area.width() - 14,
                    self.fontMetrics().height(),
                    Qt.AlignRight, number
                )
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1


# ─────────────────────────── Syntax Highlighters ───────────────────────────

def _fmt(color, bold=False, italic=False):
    f = QTextCharFormat()
    f.setForeground(QColor(color))
    if bold:   f.setFontWeight(QFont.Bold)
    if italic: f.setFontItalic(True)
    return f


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        # Decorators  @something
        self.rules.append((QRegExp(r"@[A-Za-z_][A-Za-z0-9_.]*"), _fmt(SYN_DECORATOR, bold=True)))

        # Keywords
        kws = [
            "False", "None", "True", "and", "as", "assert", "async", "await",
            "break", "class", "continue", "def", "del", "elif", "else", "except",
            "finally", "for", "from", "global", "if", "import", "in", "is",
            "lambda", "nonlocal", "not", "or", "pass", "raise", "return",
            "try", "while", "with", "yield"
        ]
        for kw in kws:
            self.rules.append((QRegExp(r"\b" + kw + r"\b"), _fmt(SYN_KEYWORD, bold=True)))

        # Built-ins
        builtins = ["print", "len", "range", "int", "str", "float", "list", "dict",
                    "set", "tuple", "bool", "type", "isinstance", "open", "super",
                    "enumerate", "zip", "map", "filter", "sorted", "reversed",
                    "hasattr", "getattr", "setattr", "callable", "input", "abs",
                    "max", "min", "sum", "any", "all", "repr", "id", "dir"]
        for b in builtins:
            self.rules.append((QRegExp(r"\b" + b + r"\b"), _fmt(SYN_BUILTIN)))

        # self / cls
        self.rules.append((QRegExp(r"\b(self|cls)\b"), _fmt(SYN_SELF, bold=True)))

        # Type hints  (: int, -> str)
        self.rules.append((QRegExp(r"\b(int|str|float|bool|list|dict|set|tuple|None|Optional|Union|Any|List|Dict|Tuple|Set|Type|Callable)\b"), _fmt(SYN_TYPE)))

        # Class names after 'class '
        self.rules.append((QRegExp(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)"), _fmt(SYN_CLASS, bold=True)))

        # Function/method names after 'def '
        self.rules.append((QRegExp(r"\bdef\s+([A-Za-z_][A-Za-z0-9_]*)"), _fmt(SYN_FUNCTION, bold=True)))

        # Function calls  name(
        self.rules.append((QRegExp(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*(?=\()"), _fmt(SYN_FUNCTION)))

        # Numbers
        self.rules.append((QRegExp(r"\b[0-9]+(\.[0-9]+)?(e[+-]?[0-9]+)?\b"), _fmt(SYN_NUMBER)))
        self.rules.append((QRegExp(r"\b0x[0-9A-Fa-f]+\b"), _fmt(SYN_NUMBER)))

        # Operators
        self.rules.append((QRegExp(r"[+\-*/%&|^~<>=!]+"), _fmt(SYN_OPERATOR)))

        # Triple-quoted strings (handled in highlightBlock separately)
        # Double-quoted strings
        self.rules.append((QRegExp(r'"[^"\\]*(\\.[^"\\]*)*"'), _fmt(SYN_STRING)))
        # Single-quoted strings
        self.rules.append((QRegExp(r"'[^'\\]*(\\.[^'\\]*)*'"), _fmt(SYN_STRING)))

        # Comments  # ...
        self.rules.append((QRegExp(r"#[^\n]*"), _fmt(SYN_COMMENT, italic=True)))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            i = pattern.indexIn(text)
            while i >= 0:
                length = pattern.matchedLength()
                if pattern.captureCount() >= 1:
                    cap = pattern.cap(1)
                    if cap:
                        pos = pattern.pos(1)
                        self.setFormat(pos, len(cap), fmt)
                    else:
                        self.setFormat(i, length, fmt)
                else:
                    self.setFormat(i, length, fmt)
                i = pattern.indexIn(text, i + max(1, length))


class CppHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        # Preprocessor
        self.rules.append((QRegExp(r"#\s*(include|define|ifdef|ifndef|endif|pragma|if|else|elif)\b.*"), _fmt(SYN_DECORATOR, bold=True)))

        # Keywords
        kws = ["auto", "break", "case", "class", "const", "continue", "default",
               "delete", "do", "double", "else", "enum", "explicit", "extern",
               "false", "float", "for", "friend", "goto", "if", "inline", "int",
               "long", "mutable", "namespace", "new", "nullptr", "operator",
               "private", "protected", "public", "register", "return", "short",
               "signed", "sizeof", "static", "struct", "switch", "template",
               "this", "throw", "true", "try", "typedef", "typename", "union",
               "unsigned", "using", "virtual", "void", "volatile", "while"]
        for kw in kws:
            self.rules.append((QRegExp(r"\b" + kw + r"\b"), _fmt(SYN_KEYWORD, bold=True)))

        # Types
        self.rules.append((QRegExp(r"\b(std|string|vector|map|set|pair|shared_ptr|unique_ptr|array|cout|cin|endl)\b"), _fmt(SYN_TYPE)))

        # Class / struct names
        self.rules.append((QRegExp(r"\b(class|struct)\s+([A-Za-z_][A-Za-z0-9_]*)"), _fmt(SYN_CLASS, bold=True)))

        # Function names
        self.rules.append((QRegExp(r"\b([A-Za-z_][A-Za-z0-9_:]*)\s*(?=\()"), _fmt(SYN_FUNCTION)))

        # Numbers
        self.rules.append((QRegExp(r"\b[0-9]+(\.[0-9]+)?(f|L|u|ul)?\b"), _fmt(SYN_NUMBER)))

        # Strings
        self.rules.append((QRegExp(r'"[^"\\]*(\\.[^"\\]*)*"'), _fmt(SYN_STRING)))
        self.rules.append((QRegExp(r"'[^'\\]*(\\.[^'\\]*)*'"), _fmt(SYN_STRING)))

        # Operators
        self.rules.append((QRegExp(r"[+\-*/%&|^~<>=!:?]+"), _fmt(SYN_OPERATOR)))

        # Comments
        self.rules.append((QRegExp(r"//[^\n]*"), _fmt(SYN_COMMENT, italic=True)))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            i = pattern.indexIn(text)
            while i >= 0:
                length = pattern.matchedLength()
                if pattern.captureCount() >= 1:
                    cap = pattern.cap(1)
                    if cap:
                        pos = pattern.pos(1)
                        self.setFormat(pos, len(cap), fmt)
                    else:
                        self.setFormat(i, length, fmt)
                else:
                    self.setFormat(i, length, fmt)
                i = pattern.indexIn(text, i + max(1, length))


# ─────────────────────────── Animated Run Button ───────────────────────────

class PulseButton(QPushButton):
    """A button that pulses with a glowing border while running."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._glow = 0
        self._pulsing = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._step = 0
        self.setMinimumWidth(100)
        self._update_style(idle=True)

    def _tick(self):
        self._step = (self._step + 5) % 360
        glow = int((math.sin(math.radians(self._step)) + 1) / 2 * 255)
        r = 200 + int(glow * 0.2)
        g = int(glow * 0.27)
        b = 0
        color = "#{:02X}{:02X}{:02X}".format(min(255,r), min(255,g), min(255,b))
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #3D0000, stop:1 #1A0A00);
                color: #FFFFFF;
                font-weight: 900;
                font-size: 12px;
                letter-spacing: 2px;
                border: 2px solid {color};
                border-radius: 8px;
                padding: 6px 18px;
            }}
        """)

    def start_pulse(self):
        self._pulsing = True
        self._step = 0
        self._timer.start(30)

    def stop_pulse(self):
        self._pulsing = False
        self._timer.stop()
        self._update_style(idle=True)

    def _update_style(self, idle=True):
        if idle:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 {ORANGE_FIRE}, stop:1 #FF9500);
                    color: #000000;
                    font-weight: 900;
                    font-size: 12px;
                    letter-spacing: 2px;
                    border: none;
                    border-radius: 8px;
                    padding: 6px 18px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 #FF8800, stop:1 #FFB500);
                }}
                QPushButton:pressed {{
                    background: {ORANGE_FIRE};
                }}
            """)


# ─────────────────────────── Main Window ───────────────────────────


# ─────────────────────────── Animated Logo Label ───────────────────────────

class AnimatedLogoLabel(QLabel):
    """TRINITY brand label that cycles through a subtle color-shift glow."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._step = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)
        self.setFixedHeight(30)
        self._tick()

    def _tick(self):
        self._step = (self._step + 2) % 360
        t = (math.sin(math.radians(self._step)) + 1) / 2   # 0..1
        # Interpolate orange → blue
        r = int(0xFF * (1 - t) + 0x38 * t)
        g = int(0x6B * (1 - t) + 0xBF * t)
        b = int(0x00 * (1 - t) + 0xFF * t)
        color = "#{:02X}{:02X}{:02X}".format(r, g, b)
        self.setStyleSheet(f"""
            font-weight: 900;
            font-size: 16px;
            letter-spacing: 3px;
            color: {color};
            padding-right: 12px;
        """)


# ─────────────────────────── Typewriter Console Intro ───────────────────────────

class TypewriterIntro:
    """Writes a boot sequence into a QPlainTextEdit character by character."""
    LINES = [
        "╔══════════════════════════════════════════════╗",
        "║        TRINITY — Neon Forge IDE  v2.0        ║",
        "╚══════════════════════════════════════════════╝",
        "",
        "  Engine     : Trinity Runtime (C / C++ / Python)",
        "  Highlighter: Neon Forge Syntax Engine",
        "  Status      : ✓ All systems nominal",
        "",
        "  Open a file or start typing to begin.",
        "",
    ]

    def __init__(self, console):
        self._console = console
        self._line_idx = 0
        self._char_idx = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(12)

    def _tick(self):
        if self._line_idx >= len(self.LINES):
            self._timer.stop()
            return
        line = self.LINES[self._line_idx]
        if self._char_idx < len(line):
            # Append character to last block
            cursor = self._console.textCursor()
            cursor.movePosition(cursor.End)
            cursor.insertText(line[self._char_idx])
            self._console.setTextCursor(cursor)
            self._char_idx += 1
        else:
            self._console.appendPlainText("")
            self._line_idx += 1
            self._char_idx = 0


# ─────────────────────────── Status Bar Pulse ───────────────────────────

class StatusBarPulse:
    """Animates a dot on the status bar to show the IDE is alive."""
    STATES = ["●", "○"]
    def __init__(self, status_bar, base_text="  Ready  ·  Trinity Neon Forge  ·  Python"):
        self._sb = status_bar
        self._base = base_text
        self._idx = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(900)

    def _tick(self):
        dot = self.STATES[self._idx % 2]
        self._sb.showMessage(f"  {dot}  {self._base.strip()}")
        self._idx += 1

    def set_base(self, text):
        self._base = text


GLOBAL_STYLE = f"""
QMainWindow, QWidget {{
    background: {BG_VOID};
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', -apple-system, 'Helvetica Neue', sans-serif;
    font-size: 13px;
}}

/* ── Scrollbars ── */
QScrollBar:vertical {{
    background: {BG_VOID};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_GLOW};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {BLUE_MID};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: {BG_VOID};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER_GLOW};
    border-radius: 4px;
}}
QScrollBar::handle:horizontal:hover {{ background: {BLUE_MID}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

/* ── Tree / File Explorer ── */
QTreeView {{
    background: {BG_PANEL};
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER_DIM};
    border-radius: 10px;
    padding: 4px;
    outline: none;
}}
QTreeView::item {{
    padding: 5px 4px;
    border-radius: 6px;
}}
QTreeView::item:hover {{
    background: {BG_ELEVATED};
    color: {TEXT_PRIMARY};
}}
QTreeView::item:selected {{
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #0B1A33, stop:1 #0D2240);
    color: #FFFFFF;
    border-left: 3px solid {ORANGE_FIRE};
}}
QTreeView::branch {{
    background: transparent;
}}

/* ── Table (Variables) ── */
QTableWidget {{
    background: {BG_PANEL};
    color: {TEXT_PRIMARY};
    gridline-color: {BORDER_DIM};
    border: 1px solid {BORDER_DIM};
    border-radius: 10px;
}}
QTableWidget::item {{ padding: 6px; }}
QTableWidget::item:selected {{
    background: #0B2040;
    color: #FFFFFF;
}}

/* ── Buttons ── */
QPushButton {{
    background: {BG_ELEVATED};
    color: {ORANGE_SOFT};
    border: 1px solid {BORDER_GLOW};
    padding: 6px 16px;
    border-radius: 8px;
    font-weight: 600;
}}
QPushButton:hover {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #0A1C36, stop:1 #06152A);
    border-color: {BLUE_SKY};
    color: #FFFFFF;
}}
QPushButton:pressed {{
    background: {BG_DARK};
    border-color: {ORANGE_FIRE};
}}

/* ── Toolbar ── */
QToolBar {{
    background: {BG_PANEL};
    border-bottom: 1px solid {BORDER_DIM};
    spacing: 6px;
    padding: 6px 10px;
}}
QToolBar QToolButton {{
    background: transparent;
    color: {TEXT_SECONDARY};
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    font-weight: 500;
}}
QToolBar QToolButton:hover {{
    background: {BG_ELEVATED};
    color: {TEXT_PRIMARY};
}}
QToolBar QToolButton:pressed {{
    background: {BG_SURFACE};
}}

/* ── Labels ── */
QLabel {{
    color: {TEXT_SECONDARY};
    font-weight: 500;
    background: transparent;
}}

/* ── ComboBox ── */
QComboBox {{
    background: {BG_SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_GLOW};
    padding: 5px 12px;
    border-radius: 8px;
    min-width: 100px;
    font-weight: 600;
}}
QComboBox:hover {{ border-color: {BLUE_SKY}; }}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background: {BG_SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_GLOW};
    selection-background-color: {BG_ELEVATED};
}}

/* ── Headers ── */
QHeaderView::section {{
    background: {BG_SURFACE};
    color: {TEXT_MUTED};
    padding: 6px 8px;
    border: none;
    border-bottom: 1px solid {BORDER_DIM};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}}

/* ── Splitters ── */
QSplitter::handle {{
    background: {BORDER_DIM};
}}
QSplitter::handle:horizontal {{ width: 2px; }}
QSplitter::handle:vertical {{ height: 2px; }}
QSplitter::handle:hover {{
    background: {ORANGE_FIRE};
}}

/* ── Dock Widgets ── */
QDockWidget {{
    color: {TEXT_PRIMARY};
    font-weight: 700;
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}}
QDockWidget::title {{
    background: {BG_PANEL};
    padding: 8px 12px;
    font-size: 10px;
    letter-spacing: 2px;
    color: {BLUE_SKY};
    text-transform: uppercase;
    border-bottom: 1px solid {BORDER_DIM};
}}

/* ── Message Boxes ── */
QMessageBox {{
    background: {BG_PANEL};
}}
"""



# ─────────────────────────── Console Dot Animation ───────────────────────────

class ConsoleDotAnimation:
    """Cycles a dot in a QLabel to show the engine is running."""
    FRAMES = ["◎", "◉", "●", "◉"]
    def __init__(self, label: QLabel):
        self._label = label
        self._idx = 0
        self._original = label.text()
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)

    def start(self):
        self._timer.start(200)

    def stop(self):
        self._timer.stop()
        self._label.setText(self._original)

    def _tick(self):
        self._label.setText(self.FRAMES[self._idx % len(self.FRAMES)])
        self._idx += 1



# ─────────────────────────── File Tab Widget ───────────────────────────

class FileTab(QWidget):
    """A single closeable file tab."""
    clicked    = None   # assigned per-instance below
    close_req  = None

    def __init__(self, path: str, on_click, on_close, parent=None):
        super().__init__(parent)
        self._path = path
        self._active = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 6, 0)
        layout.setSpacing(6)

        self._label = QLabel(Path(path).name)
        self._label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            color: {TEXT_SECONDARY};
            background: transparent;
        """)

        self._close_btn = QPushButton("✕")
        self._close_btn.setFixedSize(16, 16)
        self._close_btn.setCursor(Qt.PointingHandCursor)
        self._close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_MUTED};
                border: none;
                font-size: 10px;
                font-weight: 700;
                padding: 0;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background: rgba(255,107,0,0.25);
                color: {ORANGE_GLOW};
            }}
        """)
        self._close_btn.clicked.connect(lambda: on_close(self._path))

        layout.addWidget(self._label)
        layout.addWidget(self._close_btn)

        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(32)
        self._on_click = on_click
        self._set_style(active=False)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._on_click(self._path)

    def set_active(self, active: bool):
        self._active = active
        self._set_style(active)

    def _set_style(self, active: bool):
        if active:
            self._label.setStyleSheet(f"""
                font-size: 12px;
                font-weight: 600;
                color: {TEXT_PRIMARY};
                background: transparent;
            """)
            self.setStyleSheet(f"""
                FileTab {{
                    background: {BG_DARK};
                    border-radius: 8px 8px 0 0;
                    border-top: 2px solid {ORANGE_FIRE};
                }}
            """)
        else:
            self._label.setStyleSheet(f"""
                font-size: 12px;
                font-weight: 600;
                color: {TEXT_MUTED};
                background: transparent;
            """)
            self.setStyleSheet(f"""
                FileTab {{
                    background: transparent;
                    border-radius: 8px 8px 0 0;
                    border-top: 2px solid transparent;
                }}
                FileTab:hover {{
                    background: {BG_ELEVATED};
                }}
            """)


class EditorTabBar(QWidget):
    """Horizontal strip of FileTab widgets with empty-state label."""

    def __init__(self, window, parent=None):
        super().__init__(parent)
        self._window = window          # TrinityMainWindow reference
        self._tabs: dict[str, FileTab] = {}   # path → tab widget
        self._active_path: str | None = None

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(2)
        self._layout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

        self._empty_lbl = QLabel("  No file open")
        self._empty_lbl.setStyleSheet(f"""
            color: {TEXT_MUTED};
            font-size: 12px;
            font-style: italic;
            padding: 6px 8px 0 8px;
        """)
        self._layout.addWidget(self._empty_lbl)

    def open_tab(self, path: str):
        """Add a new tab for *path*, or switch to it if already open."""
        if path in self._tabs:
            self._activate(path)
            return
        self._empty_lbl.hide()
        tab = FileTab(path, self._activate, self._close, self)
        self._tabs[path] = tab
        self._layout.addWidget(tab)
        self._activate(path)

    def _activate(self, path: str):
        if self._active_path and self._active_path in self._tabs:
            self._tabs[self._active_path].set_active(False)
        self._active_path = path
        self._tabs[path].set_active(True)
        # Tell the window to actually load/switch to this file
        if self._window.current_file_path != path:
            self._window._switch_to_file(path)

    def _close(self, path: str):
        if path not in self._tabs:
            return
        tab = self._tabs.pop(path)
        self._layout.removeWidget(tab)
        tab.deleteLater()

        if not self._tabs:
            # No tabs left → blank editor
            self._active_path = None
            self._empty_lbl.show()
            self._window._close_all_files()
        elif self._active_path == path:
            # Switch to the last remaining tab
            next_path = list(self._tabs.keys())[-1]
            self._activate(next_path)
            self._window._switch_to_file(next_path)


class TrinityMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('TRINITY — Neon Forge IDE')
        self.resize(1380, 860)
        self.setMinimumSize(960, 600)

        self.process = None
        self.temp_dir = None
        self.current_file_path = None
        self.highlighter = None

        self.setStyleSheet(GLOBAL_STYLE)

        self._create_actions()
        self._build_header_bar()
        self._create_explorer()
        self._create_editor_and_console()
        self._create_runtime_variables_panel()

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(self.explorer_dock)
        main_splitter.addWidget(self.editor_console_widget)
        main_splitter.setStretchFactor(1, 5)
        main_splitter.setSizes([240, 1100])

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 6, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(main_splitter)
        self.setCentralWidget(container)

        # Status bar
        self.statusBar().setStyleSheet(f"""
            QStatusBar {{
                background: {BG_PANEL};
                color: {TEXT_MUTED};
                border-top: 1px solid {BORDER_DIM};
                font-size: 11px;
                padding: 2px 10px;
            }}
        """)
        self.statusBar().showMessage("  Ready  ·  Trinity Neon Forge  ·  Python")

        # ── Startup animations ──
        self._status_pulse = StatusBarPulse(self.statusBar())
        # Typewriter boot sequence (starts after a short delay)
        QTimer.singleShot(200, self._start_typewriter)

    def _start_typewriter(self):
        self._typewriter = TypewriterIntro(self.console)

    # ── Actions ──

    def _create_actions(self):
        self.action_new_file    = QAction('  New File', self)
        self.action_new_file.triggered.connect(self.create_new_file)
        self.action_open_file   = QAction('  Open File', self)
        self.action_open_file.triggered.connect(self.open_file_dialog)
        self.action_open_folder = QAction('  Open Folder', self)
        self.action_open_folder.triggered.connect(self.open_folder_dialog)
        self.action_save        = QAction('  Save', self)
        self.action_save.triggered.connect(self.save_current_file)
        self.action_create_env  = QAction('  Create Env', self)
        self.action_create_env.triggered.connect(self.create_env_dialog)

    # ── Toolbar / Header ──

    def _build_header_bar(self):
        toolbar = QToolBar('Main Navigation')
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # Logo / Brand
        logo = QLabel()
        logo_pix = QPixmap(LOGO_IMAGE_PATH) if LOGO_IMAGE_PATH else QPixmap()
        if not logo_pix.isNull():
            logo.setPixmap(logo_pix.scaledToHeight(28, Qt.SmoothTransformation))
            toolbar.addWidget(logo)
        else:
            # Animated text logo fallback
            anim_logo = AnimatedLogoLabel("⬡ TRINITY")
            toolbar.addWidget(anim_logo)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"color: {BORDER_GLOW}; margin: 4px 6px;")
        toolbar.addWidget(sep)

        toolbar.addAction(self.action_new_file)
        toolbar.addAction(self.action_open_file)
        toolbar.addAction(self.action_open_folder)
        toolbar.addAction(self.action_save)
        toolbar.addAction(self.action_create_env)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        # Language selector
        lang_lbl = QLabel("Lang:")
        lang_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-weight: 700; letter-spacing: 1px;")
        toolbar.addWidget(lang_lbl)

        self.lang_select = QComboBox()
        self.lang_select.addItems(['Python', 'C++'])
        self.lang_select.currentTextChanged.connect(self._on_lang_changed)
        toolbar.addWidget(self.lang_select)

        # Run button
        self.run_btn = PulseButton('▶  RUN')
        self.run_btn.clicked.connect(self.run_code)
        toolbar.addWidget(self.run_btn)

    def _on_lang_changed(self, lang):
        self._reattach_highlighter(lang)
        self.statusBar().showMessage(f"  Language switched to {lang}")

    def _reattach_highlighter(self, lang=None):
        lang = lang or self.lang_select.currentText()
        if self.highlighter:
            self.highlighter.setDocument(None)
        if lang == 'C++':
            self.highlighter = CppHighlighter(self.editor.document())
        else:
            self.highlighter = PythonHighlighter(self.editor.document())

    # ── File Explorer ──

    def _create_explorer(self):
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setHeaderHidden(True)
        for i in range(1, 4):
            self.tree.setColumnHidden(i, True)
        self.tree.clicked.connect(self.on_explorer_clicked)
        self.tree.setAnimated(True)
        self.tree.setIndentation(18)

        self.explorer_dock = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        header = QWidget()
        header.setStyleSheet(f"""
            background: {BG_SURFACE};
            border-radius: 10px 10px 0 0;
            border-bottom: 1px solid {BORDER_DIM};
        """)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(10, 8, 10, 8)

        icon_lbl = QLabel("◈")
        icon_lbl.setStyleSheet(f"color: {ORANGE_FIRE}; font-size: 14px; background: transparent;")
        title_lbl = QLabel("EXPLORER")
        title_lbl.setStyleSheet(f"""
            font-size: 10px;
            font-weight: 800;
            color: {TEXT_MUTED};
            letter-spacing: 2px;
            background: transparent;
        """)
        h_lay.addWidget(icon_lbl)
        h_lay.addWidget(title_lbl)
        h_lay.addStretch()

        layout.addWidget(header)
        layout.addWidget(self.tree)
        self.explorer_dock.setLayout(layout)
        self.explorer_dock.setMinimumWidth(200)

    # ── Editor + Console ──

    def _create_editor_and_console(self):
        self.editor = TrinityEditor()
        self.editor.setPlaceholderText('# Start writing beautiful code...')
        self.highlighter = PythonHighlighter(self.editor.document())

        # Tab bar header for editor
        editor_header = QWidget()
        editor_header.setStyleSheet(f"""
            background: {BG_SURFACE};
            border-radius: 10px 10px 0 0;
        """)
        eh_lay = QHBoxLayout(editor_header)
        eh_lay.setContentsMargins(8, 6, 12, 0)
        eh_lay.setSpacing(0)

        self.tab_bar = EditorTabBar(self)
        eh_lay.addWidget(self.tab_bar)
        eh_lay.addStretch()

        # Info badge
        self.info_lbl = QLabel("")
        self.info_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; padding-bottom: 4px;")
        eh_lay.addWidget(self.info_lbl)

        editor_wrapper = QWidget()
        ew_lay = QVBoxLayout(editor_wrapper)
        ew_lay.setContentsMargins(0, 0, 0, 0)
        ew_lay.setSpacing(0)
        ew_lay.addWidget(editor_header)
        ew_lay.addWidget(self.editor)

        # Console
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 10))
        self.console.setStyleSheet(f"""
            QPlainTextEdit {{
                background: {BG_VOID};
                color: #8A9BB0;
                border: none;
                padding: 8px 12px;
                font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
                font-size: 11px;
            }}
        """)

        console_header = QWidget()
        console_header.setFixedHeight(34)
        console_header.setStyleSheet(f"""
            background: {BG_SURFACE};
            border-top: 1px solid {BORDER_DIM};
        """)
        ch_lay = QHBoxLayout(console_header)
        ch_lay.setContentsMargins(14, 0, 14, 0)

        c_icon = QLabel("◎")
        c_icon.setStyleSheet(f"color: {BLUE_SKY}; font-size: 12px; background: transparent;")
        self.console_icon = c_icon
        c_lbl = QLabel("TERMINAL OUTPUT")
        c_lbl.setStyleSheet(f"""
            font-size: 10px;
            font-weight: 800;
            color: {TEXT_MUTED};
            letter-spacing: 2px;
            background: transparent;
        """)
        clear_btn = QPushButton("Clear")
        clear_btn.setFixedSize(56, 22)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_MUTED};
                border: 1px solid {BORDER_DIM};
                border-radius: 4px;
                font-size: 10px;
                padding: 2px 6px;
            }}
            QPushButton:hover {{
                border-color: {ORANGE_FIRE};
                color: {ORANGE_GLOW};
            }}
        """)
        clear_btn.clicked.connect(self.console.clear)
        ch_lay.addWidget(c_icon)
        ch_lay.addWidget(c_lbl)
        ch_lay.addStretch()
        ch_lay.addWidget(clear_btn)

        console_box = QWidget()
        cb_lay = QVBoxLayout(console_box)
        cb_lay.setContentsMargins(0, 0, 0, 0)
        cb_lay.setSpacing(0)
        cb_lay.addWidget(console_header)
        cb_lay.addWidget(self.console)

        inner_splitter = QSplitter(Qt.Vertical)
        inner_splitter.addWidget(editor_wrapper)
        inner_splitter.addWidget(console_box)
        inner_splitter.setStretchFactor(0, 4)
        inner_splitter.setSizes([620, 180])

        self.editor_console_widget = inner_splitter
        self._console_dot = ConsoleDotAnimation(self.console_icon)

    # ── Variables Panel ──

    def _create_runtime_variables_panel(self):
        dock = QDockWidget('⚙  ENV VARIABLES', self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.BottomDockWidgetArea)

        self.vars_table = QTableWidget(0, 2)
        self.vars_table.setHorizontalHeaderLabels(['KEY', 'VALUE'])
        self.vars_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vars_table.verticalHeader().setVisible(False)
        self.vars_table.setShowGrid(True)

        add_btn = QPushButton('+ Add Variable')
        add_btn.clicked.connect(self.add_variable_row)
        remove_btn = QPushButton('✕ Remove')
        remove_btn.clicked.connect(self.remove_selected_vars)

        layout = QVBoxLayout()
        layout.setContentsMargins(8, 10, 8, 8)
        layout.setSpacing(8)
        layout.addWidget(self.vars_table)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        layout.addLayout(btn_layout)

        widget = QWidget()
        widget.setLayout(layout)
        dock.setWidget(widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    # ── File Operations ──

    def on_explorer_clicked(self, index):
        path = self.model.filePath(index)
        if os.path.isdir(path):
            return
        if is_text_or_json(path):
            self.load_file(path)
            # Auto-select language
            lang = detect_language(path)
            idx = self.lang_select.findText(lang)
            if idx >= 0:
                self.lang_select.setCurrentIndex(idx)
        else:
            self.console.appendPlainText('[Info] Binary or asset — skipping preview.')

    def create_new_file(self):
        fname, ok = QInputDialog.getText(self, 'New File', 'File name:')
        if not ok or not fname.strip():
            return
        root = self.model.rootDirectory().absolutePath() or os.getcwd()
        path = os.path.join(root, fname)
        parent_dir = os.path.dirname(path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write('')
        self.current_file_path = path
        self.editor.setPlainText('')
        self._update_tab(path)
        self.tab_bar.open_tab(path)
        self.model.setRootPath(self.model.rootPath())  # refresh tree
        self.statusBar().showMessage(f"  Created: {path}")

    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Open File', os.getcwd())
        if path:
            self.load_file(path)

    def open_folder_dialog(self):
        path = QFileDialog.getExistingDirectory(self, 'Open Folder', os.getcwd())
        if path:
            self.model.setRootPath(path)
            self.tree.setRootIndex(self.model.index(path))
            self.statusBar().showMessage(f"  Workspace: {path}")

    def load_file(self, path: str):
        try:
            if Path(path).suffix.lower() == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                text = json.dumps(data, indent=2)
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
            self.current_file_path = path
            self.editor.setPlainText(text)
            self._update_tab(path)
            self._reattach_highlighter()
            self.tab_bar.open_tab(path)
            self.console.appendPlainText(f'[Open] {path}')
            self.statusBar().showMessage(f"  {path}")
            # Fade-in the editor when a new file loads
            self._fade_in_editor()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Could not open file:\n{e}')

    def _fade_in_editor(self):
        """Briefly fades the editor opacity from 0 → 1 for a smooth file-load feel."""
        effect = QGraphicsOpacityEffect(self.editor)
        self.editor.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(300)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.finished.connect(lambda: self.editor.setGraphicsEffect(None))
        anim.start()
        self._fade_anim = anim  # keep reference

    def _update_tab(self, path):
        lang = detect_language(path)
        self.info_lbl.setText(f"{lang}  ·  UTF-8")

    def _switch_to_file(self, path: str):
        """Load a file into the editor without adding a new tab (already exists)."""
        try:
            if Path(path).suffix.lower() == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                text = json.dumps(data, indent=2)
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
            self.current_file_path = path
            self.editor.setPlainText(text)
            self._update_tab(path)
            self._reattach_highlighter()
            self._fade_in_editor()
            self.statusBar().showMessage(f"  {path}")
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Could not switch to file:\n{e}')

    def _close_all_files(self):
        """Clear editor state when all tabs are closed."""
        self.current_file_path = None
        self.editor.setPlainText('')
        self.editor.setPlaceholderText('# Start writing beautiful code...')
        self.info_lbl.setText('')
        if self.highlighter:
            self.highlighter.setDocument(None)
            self.highlighter = None
        self.statusBar().showMessage("  No file open  ·  Trinity Neon Forge")

    def save_current_file(self):
        path = self.current_file_path
        if not path:
            path, _ = QFileDialog.getSaveFileName(self, 'Save File', os.getcwd())
            if not path:
                return
            self.current_file_path = path
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.console.appendPlainText(f'[Saved] {path}')
            self.model.setRootPath(self.model.rootPath())  # refresh tree
            self.statusBar().showMessage(f"  Saved: {path}")
        except Exception as e:
            QMessageBox.warning(self, 'Save Error', f'Failed to save:\n{e}')

    # ── Variable Table ──

    def add_variable_row(self):
        r = self.vars_table.rowCount()
        self.vars_table.insertRow(r)
        self.vars_table.setItem(r, 0, QTableWidgetItem('KEY'))
        self.vars_table.setItem(r, 1, QTableWidgetItem('value'))

    def remove_selected_vars(self):
        for idx in sorted({i.row() for i in self.vars_table.selectedIndexes()}, reverse=True):
            self.vars_table.removeRow(idx)

    def get_variables_as_env(self):
        env = os.environ.copy()
        for r in range(self.vars_table.rowCount()):
            n = self.vars_table.item(r, 0)
            v = self.vars_table.item(r, 1)
            if n and v:
                env[n.text()] = v.text()
        return env

    # ── Run / Execute ──

    def run_code(self):
        if self.process and self.process.state() == QProcess.Running:
            self.console.appendPlainText("[Engine] Stopping...")
            self.process.kill()
            return

        if not self.current_file_path:
            self.save_current_file()
            if not self.current_file_path:
                return
        else:
            self.save_current_file()

        lang = self.lang_select.currentText()
        env_vars = self.get_variables_as_env()

        self.process = QProcess(self)
        q_env = self.process.processEnvironment()
        for k, v in env_vars.items():
            q_env.insert(k, v)
        self.process.setProcessEnvironment(q_env)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._handle_console_stream)
        self.process.finished.connect(self._handle_execution_finished)

        self.run_btn.setText('◼  STOP')
        self.run_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #8B0000, stop:1 #500000);
                color: #FFFFFF;
                font-weight: 900;
                font-size: 12px;
                letter-spacing: 2px;
                border: 2px solid #CC0000;
                border-radius: 8px;
                padding: 6px 18px;
            }}
        """)
        self.run_btn.start_pulse()
        self._console_dot.start()

        if lang == 'Python':
            python_exec = sys.executable or 'python'
            self.console.appendPlainText(f'\n▶ Running with {python_exec}\n{"─"*60}')
            self.process.start(python_exec, [self.current_file_path])
        elif lang == 'C++':
            self._compile_and_run_cpp()

    def _compile_and_run_cpp(self):
        if not self.current_file_path.endswith(('.cpp', '.cc', '.c')):
            QMessageBox.warning(self, 'Wrong File', 'Please open a C/C++ source file first.')
            self._reset_run_button()
            return
        self.temp_dir = tempfile.mkdtemp(prefix='trinity_cpp_')
        exe_path = os.path.join(self.temp_dir, 'a.out.exe' if os.name == 'nt' else 'a.out')
        self.console.appendPlainText(f'\n🛠  Compiling with g++...\n{"─"*60}')
        self.process.start('g++', [self.current_file_path, '-O2', '-std=c++17', '-o', exe_path])
        self.process.finished.disconnect()
        self.process.finished.connect(lambda code, status: self._handle_cpp_compilation_done(code, exe_path))

    def _handle_cpp_compilation_done(self, exit_code, exe_path):
        if exit_code == 0:
            self.console.appendPlainText('\n✓ Compiled. Running...')
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyReadStandardOutput.connect(self._handle_console_stream)
            self.process.finished.connect(self._handle_execution_finished)
            self.process.start(exe_path)
        else:
            self.console.appendPlainText('\n✗ Compilation failed.')
            self._reset_run_button()
            self._cleanup_temp_dir()

    def _handle_console_stream(self):
        data = self.process.readAllStandardOutput()
        text = data.data().decode(errors='replace')
        self.console.insertPlainText(text)
        self.console.ensureCursorVisible()

    def _handle_execution_finished(self, exit_code, exit_status):
        self.console.appendPlainText(f'\n{"─"*60}\n✓ Finished — exit code {exit_code}')
        self._reset_run_button()
        self._cleanup_temp_dir()
        self.statusBar().showMessage(f"  Done — exit {exit_code}")
        # Flash the console border green on success, red on failure
        self._flash_console(success=(exit_code == 0))

    def _reset_run_button(self):
        self.run_btn.stop_pulse()  # also restores idle style
        self.run_btn.setText('▶  RUN')
        self._console_dot.stop()

    def _flash_console(self, success=True):
        """Briefly tints the console background to signal run result."""
        color = "#0D2B0D" if success else "#2B0D0D"
        original = f"background: {BG_VOID};"
        flash_style = f"""
            QPlainTextEdit {{
                background: {color};
                color: #8A9BB0;
                border: none;
                padding: 8px 12px;
                font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
                font-size: 11px;
            }}
        """
        self.console.setStyleSheet(flash_style)
        QTimer.singleShot(600, lambda: self.console.setStyleSheet(f"""
            QPlainTextEdit {{
                background: {BG_VOID};
                color: #8A9BB0;
                border: none;
                padding: 8px 12px;
                font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
                font-size: 11px;
            }}
        """))

    def _cleanup_temp_dir(self):
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception:
                pass
            self.temp_dir = None

    def create_env_dialog(self):
        choice, ok = QInputDialog.getItem(
            self, 'Create Environment', 'Strategy:',
            ['venv (virtualenv)', 'conda (Anaconda)'], 0, False
        )
        if not ok:
            return
        base_dir = QFileDialog.getExistingDirectory(self, 'Choose Location', os.getcwd())
        if not base_dir:
            return
        name, ok = QInputDialog.getText(self, 'Environment Name', 'Name:')
        if not ok or not name:
            return
        target_path = os.path.join(base_dir, name)
        self.console.appendPlainText(f'[Env] Creating at: {target_path}')
        env_proc = QProcess(self)
        env_proc.setProcessChannelMode(QProcess.MergedChannels)
        env_proc.readyReadStandardOutput.connect(
            lambda: self.console.insertPlainText(env_proc.readAllStandardOutput().data().decode(errors='replace'))
        )
        if choice.startswith('venv'):
            env_proc.start(sys.executable, ['-m', 'venv', target_path])
        else:
            env_proc.start('conda', ['create', '-y', '-p', target_path, 'python'])
        env_proc.finished.connect(
            lambda code, status: self.console.appendPlainText(f'\n[Env] Done — exit {code}')
        )


# ─────────────────────────── Entry Point ───────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Trinity IDE")
    app.setStyle("Fusion")

    # Dark palette base so native widgets also look dark
    palette = QPalette()
    palette.setColor(QPalette.Window,          QColor(BG_VOID))
    palette.setColor(QPalette.WindowText,      QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Base,            QColor(BG_DARK))
    palette.setColor(QPalette.AlternateBase,   QColor(BG_PANEL))
    palette.setColor(QPalette.ToolTipBase,     QColor(BG_SURFACE))
    palette.setColor(QPalette.ToolTipText,     QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Text,            QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Button,          QColor(BG_ELEVATED))
    palette.setColor(QPalette.ButtonText,      QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Highlight,       QColor(BLUE_MID))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)

    window = TrinityMainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()