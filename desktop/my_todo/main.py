#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
My Todo - 桌面待办事项清单
一个仿小黄条风格的Windows桌面待办软件
功能：桌面小组件模式、背景透明度调节、黑灰渐变背景、历史待办功能
"""

import sys
import os
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QLabel, QSlider, QMenu, QAction, QSystemTrayIcon,
    QCheckBox, QFrame, QSizePolicy, QStackedWidget,
    QGraphicsOpacityEffect
)
from PyQt5.QtCore import Qt, QPoint, QTimer, QSettings, QSize
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QCursor, QKeyEvent, QLinearGradient, QBrush

# 数据库路径 - 支持exe和普通python运行
def get_db_path():
    """获取数据库文件路径
    
    当打包为exe时，数据库文件放在exe所在目录
    当作为python脚本运行时，数据库文件放在脚本所在目录
    """
    if getattr(sys, 'frozen', False):
        # 打包为exe的情况 - 使用exe所在目录
        # sys.executable 是exe文件的完整路径
        base_dir = os.path.dirname(sys.executable)
    else:
        # 普通python脚本运行
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_dir, 'todo_data.db')

# 数据库路径
DB_PATH = get_db_path()


class Database:
    """SQLite数据库管理类"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 待办事项表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 历史待办表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                completed_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_todo(self, content):
        """添加待办事项"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO todos (content) VALUES (?)',
            (content,)
        )
        todo_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return todo_id
    
    def get_all_todos(self):
        """获取所有待办事项"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, content, created_at FROM todos ORDER BY created_at DESC'
        )
        todos = cursor.fetchall()
        conn.close()
        return todos
    
    def delete_todo(self, todo_id):
        """删除待办事项"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        conn.commit()
        conn.close()
    
    def update_todo_content(self, todo_id, content):
        """更新待办事项内容"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE todos SET content = ? WHERE id = ?',
            (content, todo_id)
        )
        conn.commit()
        conn.close()
    
    def move_to_history(self, todo_id, content):
        """将待办事项移到历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 添加到历史表
        cursor.execute(
            'INSERT INTO history (content, completed_at) VALUES (?, ?)',
            (content, datetime.now().isoformat())
        )
        
        # 从待办表删除
        cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_history(self):
        """获取所有历史待办"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, content, completed_at FROM history ORDER BY completed_at DESC'
        )
        history = cursor.fetchall()
        conn.close()
        return history
    
    def delete_history(self, history_id):
        """删除历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM history WHERE id = ?', (history_id,))
        conn.commit()
        conn.close()
    
    def clear_all_history(self):
        """清空所有历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM history')
        conn.commit()
        conn.close()
    
    def restore_from_history(self, history_id, content):
        """从历史记录恢复到待办"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 添加回待办表
        cursor.execute(
            'INSERT INTO todos (content, created_at) VALUES (?, ?)',
            (content, datetime.now().isoformat())
        )
        
        # 从历史表删除
        cursor.execute('DELETE FROM history WHERE id = ?', (history_id,))
        
        conn.commit()
        conn.close()
    
    def search_todos(self, keyword):
        """模糊搜索待办事项"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, content, created_at FROM todos WHERE content LIKE ? ORDER BY created_at DESC',
            (f'%{keyword}%',)
        )
        todos = cursor.fetchall()
        conn.close()
        return todos
    
    def search_history(self, keyword):
        """模糊搜索历史待办"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, content, completed_at FROM history WHERE content LIKE ? ORDER BY completed_at DESC',
            (f'%{keyword}%',)
        )
        history = cursor.fetchall()
        conn.close()
        return history


class TodoItemWidget(QFrame):
    """自定义待办事项项组件"""
    
    def __init__(self, todo_id, content, created_at, parent=None, main_window=None, is_history=False):
        super().__init__(parent)
        self.todo_id = todo_id
        self.content = content
        self.created_at = created_at
        self.is_history = is_history
        self.parent_list = parent
        self.main_window = main_window  # 直接保存主窗口引用
        self.setup_ui()
    
    def setup_ui(self):
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("""
            TodoItemWidget {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(8)
        
        if not self.is_history:
            # 复选框（仅待办事项显示）
            self.checkbox = QCheckBox()
            self.checkbox.setStyleSheet("""
                QCheckBox {
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border-radius: 3px;
                    border: 2px solid #AAAAAA;
                    background-color: rgba(255, 255, 255, 50);
                }
                QCheckBox::indicator:hover {
                    border: 2px solid #FFFFFF;
                }
                QCheckBox::indicator:checked {
                    background-color: #4CAF50;
                    border: 2px solid #4CAF50;
                }
            """)
            self.checkbox.stateChanged.connect(self.on_completed)
            layout.addWidget(self.checkbox)
        else:
            # 历史记录显示完成图标
            self.check_icon = QLabel("✓")
            self.check_icon.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 14px;
                    font-weight: bold;
                    background-color: transparent;
                }
            """)
            layout.addWidget(self.check_icon)
        
        # 内容区域 - 使用 stacked widget 实现标签和输入框切换
        self.content_stack = QStackedWidget()
        self.content_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # 内容标签（显示模式）
        self.content_label = QLabel(self.content)
        self.content_label.setWordWrap(True)
        
        # 字体设置：加大一号(11)，待办加粗
        if self.is_history:
            # 历史记录：白色、11号、不加粗，不打横杠
            font = QFont("Microsoft YaHei", 11)
            self.content_label.setFont(font)
            self.content_label.setStyleSheet("""
                QLabel {
                    color: #FFFFFF;
                    background-color: transparent;
                }
            """)
        else:
            # 待办事项：白色、11号、加粗
            font = QFont("Microsoft YaHei", 11, QFont.Bold)
            self.content_label.setFont(font)
            self.content_label.setStyleSheet("""
                QLabel {
                    color: #FFFFFF;
                    background-color: transparent;
                }
            """)
        
        # 双击编辑（仅待办事项）
        if not self.is_history:
            self.content_label.mouseDoubleClickEvent = self.start_edit
        
        self.content_stack.addWidget(self.content_label)
        
        # 内容输入框（编辑模式）- 仅待办事项
        if not self.is_history:
            self.content_input = QLineEdit(self.content)
            self.content_input.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
            self.content_input.setFixedHeight(26)
            self.content_input.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255, 255, 255, 20);
                    border: 1px solid rgba(255, 255, 255, 80);
                    border-radius: 3px;
                    padding: 2px 6px;
                    color: #FFFFFF;
                }
                QLineEdit:focus {
                    background-color: rgba(255, 255, 255, 30);
                    border: 2px solid rgba(255, 255, 255, 120);
                }
            """)
            self.content_input.returnPressed.connect(self.finish_edit)
            self.content_input.editingFinished.connect(self.finish_edit)
            self.content_stack.addWidget(self.content_input)
        
        layout.addWidget(self.content_stack, 1)
        
        # 操作按钮
        if self.is_history:
            # 恢复按钮
            self.restore_btn = QPushButton("↩")
            self.restore_btn.setFixedSize(24, 24)
            self.restore_btn.setToolTip("恢复到待办")
            self.restore_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #4CAF50;
                    border: none;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: rgba(76, 175, 80, 0.2);
                    border-radius: 3px;
                }
            """)
            self.restore_btn.clicked.connect(self.restore_item)
            layout.addWidget(self.restore_btn)
        
        # 删除按钮
        self.delete_btn = QPushButton("×")
        self.delete_btn.setFixedSize(20, 20)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #AAAAAA;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #FF4444;
                background-color: rgba(255, 68, 68, 0.2);
                border-radius: 3px;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_item)
        layout.addWidget(self.delete_btn)
    
    def on_completed(self, state):
        """完成待办事项"""
        if state == Qt.Checked:
            # 先更新文本样式为已完成（打横杠）
            self.content_label.setStyleSheet("""
                QLabel {
                    color: #888888;
                    text-decoration: line-through;
                    background-color: transparent;
                }
            """)
            # 延迟一下让用户看到效果，然后移到历史
            QTimer.singleShot(500, self.complete_item)
    
    def complete_item(self):
        """将待办移到历史"""
        if self.main_window and hasattr(self.main_window, 'db'):
            self.main_window.db.move_to_history(self.todo_id, self.content)
            self.main_window.load_todos()
            self.main_window.load_history()
    
    def restore_item(self):
        """从历史恢复到待办"""
        if self.main_window and hasattr(self.main_window, 'db'):
            self.main_window.db.restore_from_history(self.todo_id, self.content)
            self.main_window.load_todos()
            self.main_window.load_history()
    
    def start_edit(self, event):
        """双击开始编辑 - 切换到输入框模式"""
        if not self.is_history:
            self.content_input.setText(self.content)
            self.content_stack.setCurrentIndex(1)  # 切换到输入框
            self.content_input.setFocus()
            self.content_input.selectAll()
    
    def finish_edit(self):
        """完成编辑 - 保存内容并切换回标签模式"""
        if not self.is_history:
            new_content = self.content_input.text().strip()
            if new_content and new_content != self.content:
                self.content = new_content
                self.content_label.setText(self.content)
                if self.main_window and hasattr(self.main_window, 'db'):
                    self.main_window.db.update_todo_content(self.todo_id, self.content)
            # 切换回标签模式
            self.content_stack.setCurrentIndex(0)
    
    def delete_item(self):
        """删除此项"""
        if self.main_window and hasattr(self.main_window, 'db'):
            if self.is_history:
                self.main_window.db.delete_history(self.todo_id)
                self.main_window.load_history()
            else:
                self.main_window.db.delete_todo(self.todo_id)
                self.main_window.load_todos()


class YellowStickyNotes(QWidget):
    """小黄条主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 数据库
        self.db = Database(DB_PATH)
        
        # 当前视图状态
        self.current_view = 'todos'  # 'todos' 或 'history'
        
        # 窗口设置 - 桌面小组件模式
        self.setWindowFlags(
            Qt.FramelessWindowHint |      # 无边框
            Qt.WindowStaysOnBottomHint |  # 始终保持在最底层（桌面小组件效果）
            Qt.Tool                       # 不在任务栏显示
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景
        
        # 拖动相关
        self.dragging = False
        self.drag_position = QPoint()
        
        # 吸附相关
        self.snap_margin = 20  # 吸附边距
        self.screen_geometry = QApplication.primaryScreen().geometry()
        
        # 设置窗口大小和位置
        self.setFixedSize(300, 450)
        self.load_position()
        
        # 初始化UI
        self.setup_ui()
        
        # 加载透明度设置
        self.load_opacity()
        
        # 加载数据
        self.load_todos()
        self.load_history()
        
        # 创建系统托盘图标
        self.create_tray_icon()
    
    def setup_ui(self):
        """设置用户界面"""
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 主容器（带背景色和圆角）- 黑灰渐变背景
        self.container = QFrame()
        self.container.setObjectName("container")
        # 透明度将在 load_opacity() 中设置
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(12, 12, 12, 12)
        container_layout.setSpacing(10)
        
        # 标题栏
        title_layout = QHBoxLayout()
        
        # 标题
        self.title_label = QLabel("📝 Todo")
        self.title_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.title_label.setStyleSheet("color: #FFFFFF; background-color: transparent;")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # 视图切换按钮
        self.view_toggle_btn = QPushButton("History")
        self.view_toggle_btn.setFixedSize(50, 24)
        self.view_toggle_btn.setFont(QFont("Microsoft YaHei", 9))
        self.view_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 30);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 50);
            }
        """)
        self.view_toggle_btn.clicked.connect(self.toggle_view)
        title_layout.addWidget(self.view_toggle_btn)
        
        # 设置按钮
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(24, 24)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #FFFFFF;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);
                border-radius: 4px;
            }
        """)
        self.settings_btn.clicked.connect(self.show_settings_menu)
        title_layout.addWidget(self.settings_btn)
        
        container_layout.addLayout(title_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: rgba(255, 255, 255, 30);")
        line.setFixedHeight(1)
        container_layout.addWidget(line)
        
        # 堆叠窗口（待办列表和历史列表）
        self.stacked_widget = QStackedWidget()
        
        # 待办视图
        self.todos_widget = QWidget()
        todos_layout = QVBoxLayout(self.todos_widget)
        todos_layout.setContentsMargins(0, 0, 0, 0)
        todos_layout.setSpacing(8)
        
        # 搜索区域（待办搜索）
        search_layout = QHBoxLayout()
        
        self.todo_search_field = QLineEdit()
        self.todo_search_field.setPlaceholderText("🔍 Search...")
        self.todo_search_field.setFont(QFont("Microsoft YaHei", 10))
        self.todo_search_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 20);
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 4px;
                padding: 6px;
                color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid rgba(255, 255, 255, 100);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 100);
            }
        """)
        self.todo_search_field.textChanged.connect(self.search_todos)
        search_layout.addWidget(self.todo_search_field, 1)
        
        self.search_btn = QPushButton("🔍")
        self.search_btn.setFixedSize(32, 32)
        self.search_btn.setFont(QFont("Microsoft YaHei", 12))
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 100, 100, 180);
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(120, 120, 120, 220);
            }
            QPushButton:pressed {
                background-color: rgba(140, 140, 140, 255);
            }
        """)
        self.search_btn.clicked.connect(self.search_todos)
        search_layout.addWidget(self.search_btn)
        
        todos_layout.addLayout(search_layout)
        
        # 待办列表
        self.todo_list = QListWidget()
        self.todo_list.setFrameShape(QFrame.NoFrame)
        self.todo_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                background-color: transparent;
                border: none;
                padding: 0px;
            }
            QListWidget::item:selected {
                background-color: transparent;
            }
            /* 美化滚动条 */
            QScrollBar:vertical {
                background-color: transparent;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 80);
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 255, 255, 120);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background-color: transparent;
            }
        """)
        self.todo_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.todo_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 设置滚动条自动隐藏
        self.todo_scrollbar = self.todo_list.verticalScrollBar()
        self.todo_scrollbar_timer = QTimer(self)
        self.todo_scrollbar_timer.setSingleShot(True)
        self.todo_scrollbar_timer.timeout.connect(self.hide_todo_scrollbar)
        self.todo_scrollbar.valueChanged.connect(self.on_todo_scroll)
        
        # 双击空白处添加待办
        self.todo_list.mouseDoubleClickEvent = self.on_todo_list_double_click
        
        todos_layout.addWidget(self.todo_list, 1)
        
        # 新增待办输入框（内联）
        self.add_todo_layout = QHBoxLayout()
        
        self.add_todo_input = QLineEdit()
        self.add_todo_input.setPlaceholderText("+ Add Todo...")
        self.add_todo_input.setFont(QFont("Microsoft YaHei", 10))
        self.add_todo_input.setFixedHeight(28)
        self.add_todo_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(76, 175, 80, 30);
                border: 1px solid rgba(76, 175, 80, 80);
                border-radius: 4px;
                padding: 4px 8px;
                color: #FFFFFF;
            }
            QLineEdit:focus {
                background-color: rgba(76, 175, 80, 50);
                border: 2px solid rgba(76, 175, 80, 120);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 120);
            }
        """)
        self.add_todo_input.returnPressed.connect(self.add_todo_from_input)
        self.add_todo_layout.addWidget(self.add_todo_input, 1)
        
        self.add_todo_btn = QPushButton("+")
        self.add_todo_btn.setFixedSize(28, 28)
        self.add_todo_btn.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        self.add_todo_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(76, 175, 80, 180);
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(76, 175, 80, 220);
            }
            QPushButton:pressed {
                background-color: rgba(76, 175, 80, 255);
            }
        """)
        self.add_todo_btn.clicked.connect(self.add_todo_from_input)
        self.add_todo_layout.addWidget(self.add_todo_btn)
        
        todos_layout.addLayout(self.add_todo_layout)
        
        # 待办统计
        self.todos_stats = QLabel("0 待办")
        self.todos_stats.setFont(QFont("Microsoft YaHei", 9))
        self.todos_stats.setStyleSheet("color: rgba(255, 255, 255, 150); background-color: transparent;")
        todos_layout.addWidget(self.todos_stats)
        
        self.stacked_widget.addWidget(self.todos_widget)
        
        # 历史视图
        self.history_widget = QWidget()
        history_layout = QVBoxLayout(self.history_widget)
        history_layout.setContentsMargins(0, 0, 0, 0)
        history_layout.setSpacing(8)
        
        # 历史搜索区域
        history_search_layout = QHBoxLayout()
        
        self.history_search_field = QLineEdit()
        self.history_search_field.setPlaceholderText("🔍 Search...")
        self.history_search_field.setFont(QFont("Microsoft YaHei", 10))
        self.history_search_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 20);
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 4px;
                padding: 6px;
                color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid rgba(255, 255, 255, 100);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 100);
            }
        """)
        self.history_search_field.textChanged.connect(self.search_history)
        history_search_layout.addWidget(self.history_search_field, 1)
        
        self.history_search_btn = QPushButton("🔍")
        self.history_search_btn.setFixedSize(32, 32)
        self.history_search_btn.setFont(QFont("Microsoft YaHei", 12))
        self.history_search_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 100, 100, 180);
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(120, 120, 120, 220);
            }
            QPushButton:pressed {
                background-color: rgba(140, 140, 140, 255);
            }
        """)
        self.history_search_btn.clicked.connect(self.search_history)
        history_search_layout.addWidget(self.history_search_btn)
        
        history_layout.addLayout(history_search_layout)
        
        # 历史列表
        self.history_list = QListWidget()
        self.history_list.setFrameShape(QFrame.NoFrame)
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                background-color: transparent;
                border: none;
                padding: 0px;
            }
            QListWidget::item:selected {
                background-color: transparent;
            }
            /* 美化滚动条 - 与待办列表保持一致 */
            QScrollBar:vertical {
                background-color: transparent;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 80);
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 255, 255, 120);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background-color: transparent;
            }
        """)
        self.history_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.history_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 设置滚动条自动隐藏
        self.history_scrollbar = self.history_list.verticalScrollBar()
        self.history_scrollbar_timer = QTimer(self)
        self.history_scrollbar_timer.setSingleShot(True)
        self.history_scrollbar_timer.timeout.connect(self.hide_history_scrollbar)
        self.history_scrollbar.valueChanged.connect(self.on_history_scroll)
        
        history_layout.addWidget(self.history_list, 1)
        
        # 历史统计和清空按钮
        history_bottom = QHBoxLayout()
        
        self.history_stats = QLabel("0 History")
        self.history_stats.setFont(QFont("Microsoft YaHei", 9))
        self.history_stats.setStyleSheet("color: rgba(255, 255, 255, 100); background-color: transparent;")
        history_bottom.addWidget(self.history_stats)
        
        history_bottom.addStretch()
        
        self.clear_history_btn = QPushButton("Clean History")
        self.clear_history_btn.setFont(QFont("Microsoft YaHei", 9))
        self.clear_history_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: rgba(255, 255, 255, 100);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 4px;
                padding: 3px 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 68, 68, 0.2);
                color: #FF4444;
                border: 1px solid rgba(255, 68, 68, 50);
            }
        """)
        self.clear_history_btn.clicked.connect(self.clear_all_history)
        history_bottom.addWidget(self.clear_history_btn)
        
        history_layout.addLayout(history_bottom)
        
        self.stacked_widget.addWidget(self.history_widget)
        
        container_layout.addWidget(self.stacked_widget, 1)
        
        # 透明度滑块（默认隐藏）
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_slider.setValue(90)
        self.opacity_slider.setStyleSheet("""
            QSlider {
                background-color: rgba(0, 0, 0, 100);
                border-radius: 4px;
                padding: 5px;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: rgba(255, 255, 255, 100);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                width: 14px;
                height: 14px;
                background: #FFFFFF;
                border-radius: 7px;
                margin: -4px 0;
            }
        """)
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        self.opacity_slider.sliderReleased.connect(self.on_slider_released)
        self.opacity_slider.setVisible(False)
        container_layout.addWidget(self.opacity_slider)
        
        self.main_layout.addWidget(self.container)
    
    def update_container_style(self, bg_opacity_percent):
        """更新容器背景样式 - 黑灰渐变"""
        bg_opacity = int(255 * bg_opacity_percent / 100)
        self.container.setStyleSheet(f"""
            #container {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(30, 30, 30, {bg_opacity}),
                    stop: 0.5 rgba(50, 50, 50, {bg_opacity}),
                    stop: 1 rgba(30, 30, 30, {int(bg_opacity * 0.8)})
                );
                border-radius: 10px;
                border: 1px solid rgba(100, 100, 100, 80);
            }}
        """)
    
    def toggle_view(self):
        """切换待办/历史视图"""
        if self.current_view == 'todos':
            self.current_view = 'history'
            self.stacked_widget.setCurrentIndex(1)
            self.view_toggle_btn.setText("Todo")
            self.title_label.setText("📜 History")
            self.load_history()
        else:
            self.current_view = 'todos'
            self.stacked_widget.setCurrentIndex(0)
            self.view_toggle_btn.setText("History")
            self.title_label.setText("📝 Todo")
            self.load_todos()
    
    def load_todos(self):
        """从数据库加载待办事项"""
        self.todo_list.clear()
        # 清空搜索框
        self.todo_search_field.clear()
        todos = self.db.get_all_todos()
        
        for todo in todos:
            todo_id, content, created_at = todo
            
            # 创建自定义待办项，传入主窗口引用
            item_widget = TodoItemWidget(todo_id, content, created_at, self.todo_list, main_window=self, is_history=False)
            
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            
            self.todo_list.addItem(list_item)
            self.todo_list.setItemWidget(list_item, item_widget)
        
        # 更新统计
        self.todos_stats.setText(f"{len(todos)} Todos")
    
    def load_history(self):
        """从数据库加载历史待办"""
        self.history_list.clear()
        # 清空搜索框
        self.history_search_field.clear()
        history = self.db.get_all_history()
        
        for item in history:
            history_id, content, completed_at = item
            
            # 创建历史项，传入主窗口引用
            item_widget = TodoItemWidget(history_id, content, completed_at, self.history_list, main_window=self, is_history=True)
            
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            
            self.history_list.addItem(list_item)
            self.history_list.setItemWidget(list_item, item_widget)
        
        # 更新统计
        self.history_stats.setText(f"{len(history)} Histories")
    
    def search_todos(self):
        """搜索待办事项"""
        keyword = self.todo_search_field.text().strip()
        self.todo_list.clear()
        
        if keyword:
            todos = self.db.search_todos(keyword)
        else:
            todos = self.db.get_all_todos()
        
        for todo in todos:
            todo_id, content, created_at = todo
            item_widget = TodoItemWidget(todo_id, content, created_at, self.todo_list, main_window=self, is_history=False)
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.todo_list.addItem(list_item)
            self.todo_list.setItemWidget(list_item, item_widget)
        
        self.todos_stats.setText(f"{len(todos)} Todos")
    
    def add_todo_from_input(self):
        """从内联输入框添加待办"""
        content = self.add_todo_input.text().strip()
        if content:
            self.db.add_todo(content)
            self.add_todo_input.clear()
            self.load_todos()  # 刷新列表
    
    def on_todo_list_double_click(self, event):
        """双击待办列表空白处聚焦到新增输入框"""
        # 获取点击位置对应的 item
        item = self.todo_list.itemAt(event.pos())
        
        # 如果点击的是空白处（没有 item），则聚焦到新增输入框
        if item is None:
            self.add_todo_input.setFocus()
        else:
            # 如果点击的是 item，不处理（让 item 自己的双击事件处理编辑）
            pass
    
    def search_history(self):
        """搜索历史待办"""
        keyword = self.history_search_field.text().strip()
        self.history_list.clear()
        
        if keyword:
            history = self.db.search_history(keyword)
        else:
            history = self.db.get_all_history()
        
        for item in history:
            history_id, content, completed_at = item
            item_widget = TodoItemWidget(history_id, content, completed_at, self.history_list, main_window=self, is_history=True)
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.history_list.addItem(list_item)
            self.history_list.setItemWidget(list_item, item_widget)
        
        self.history_stats.setText(f"{len(history)} Histories")
    
    # ========== 滚动条自动隐藏 ==========
    
    def on_todo_scroll(self):
        """待办列表滚动时显示滚动条"""
        self.todo_scrollbar.setStyleSheet("""
            QScrollBar:vertical {
                background-color: transparent;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 150);
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 255, 255, 200);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background-color: transparent;
            }
        """)
        # 重启定时器
        self.todo_scrollbar_timer.stop()
        self.todo_scrollbar_timer.start(1500)  # 1.5秒后隐藏
    
    def hide_todo_scrollbar(self):
        """隐藏待办列表滚动条"""
        self.todo_scrollbar.setStyleSheet("""
            QScrollBar:vertical {
                background-color: transparent;
                width: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: transparent;
            }
        """)
    
    def on_history_scroll(self):
        """历史列表滚动时显示滚动条"""
        self.history_scrollbar.setStyleSheet("""
            QScrollBar:vertical {
                background-color: transparent;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 150);
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 255, 255, 200);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background-color: transparent;
            }
        """)
        # 重启定时器
        self.history_scrollbar_timer.stop()
        self.history_scrollbar_timer.start(1500)  # 1.5秒后隐藏
    
    def hide_history_scrollbar(self):
        """隐藏历史列表滚动条"""
        self.history_scrollbar.setStyleSheet("""
            QScrollBar:vertical {
                background-color: transparent;
                width: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: transparent;
            }
        """)
    
    def clear_all_history(self):
        """清空所有历史记录"""
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, '确认', '确定要清空所有历史记录吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db.clear_all_history()
            self.load_history()
    
    def change_opacity(self, value):
        """改变窗口背景透明度 - 仅背景透明，文字不透明"""
        self.update_container_style(value)
    
    def on_slider_released(self):
        """滑块释放时保存透明度并隐藏"""
        # 保存透明度设置
        settings = QSettings('YellowStickyNotes', 'Opacity')
        settings.setValue('opacity', self.opacity_slider.value())
        # 隐藏滑块
        self.opacity_slider.setVisible(False)
    
    def load_opacity(self):
        """加载保存的透明度设置"""
        settings = QSettings('YellowStickyNotes', 'Opacity')
        opacity = settings.value('opacity', 90)  # 默认90%
        self.opacity_slider.setValue(int(opacity))
        self.update_container_style(int(opacity))
    
    def show_settings_menu(self):
        """显示设置菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(40, 40, 40, 240);
                border: 1px solid rgba(100, 100, 100, 100);
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
                color: #FFFFFF;
            }
            QMenu::item:selected {
                background-color: rgba(100, 100, 100, 100);
            }
        """)
        
        # 透明度选项
        opacity_action = QAction("透明度设置", self)
        opacity_action.triggered.connect(self.show_opacity_slider)
        menu.addAction(opacity_action)
        
        menu.addSeparator()
        
        # 退出选项
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.quit_app)
        menu.addAction(exit_action)
        
        menu.exec_(QCursor.pos())
    
    def show_opacity_slider(self):
        """显示透明度滑块"""
        self.opacity_slider.setVisible(True)
    
    def create_tray_icon(self):
        """创建系统托盘图标"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("MYTODO - 待办事项")
        
        # 托盘菜单
        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu {
                background-color: rgba(40, 40, 40, 240);
                border: 1px solid rgba(100, 100, 100, 100);
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
                color: #FFFFFF;
            }
            QMenu::item:selected {
                background-color: rgba(100, 100, 100, 100);
            }
        """)
        
        show_action = QAction("显示", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("隐藏", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
    
    def on_tray_activated(self, reason):
        """托盘图标被激活"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
    
    def quit_app(self):
        """退出应用程序"""
        self.save_position()
        self.tray_icon.hide()
        QApplication.quit()
    
    # ========== 窗口拖动功能 ==========
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 检查是否点击在标题栏区域
            if event.pos().y() < 50:
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            new_pos = event.globalPos() - self.drag_position
            self.move(new_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.snap_to_edge()
            event.accept()
    
    # ========== 桌面吸附功能 ==========
    
    def snap_to_edge(self):
        """吸附到屏幕边缘"""
        screen = QApplication.primaryScreen().geometry()
        pos = self.pos()
        size = self.size()
        
        new_x = pos.x()
        new_y = pos.y()
        
        # 检查左边缘
        if abs(pos.x()) < self.snap_margin:
            new_x = 0
        # 检查右边缘
        elif abs(pos.x() + size.width() - screen.width()) < self.snap_margin:
            new_x = screen.width() - size.width()
        
        # 检查上边缘
        if abs(pos.y()) < self.snap_margin:
            new_y = 0
        # 检查下边缘
        elif abs(pos.y() + size.height() - screen.height()) < self.snap_margin:
            new_y = screen.height() - size.height()
        
        # 如果位置改变，则移动窗口
        if new_x != pos.x() or new_y != pos.y():
            self.move(new_x, new_y)
            self.save_position()
    
    def save_position(self):
        """保存窗口位置"""
        settings = QSettings('YellowStickyNotes', 'Position')
        settings.setValue('x', self.x())
        settings.setValue('y', self.y())
    
    def load_position(self):
        """加载窗口位置"""
        settings = QSettings('YellowStickyNotes', 'Position')
        x = settings.value('x', None)
        y = settings.value('y', None)
        
        if x is not None and y is not None:
            self.move(int(x), int(y))
        else:
            # 默认位置：屏幕右上角
            screen = QApplication.primaryScreen().geometry()
            self.move(screen.width() - self.width() - 20, 50)
    
    def closeEvent(self, event):
        """关闭事件"""
        self.save_position()
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出程序
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建主窗口
    window = YellowStickyNotes()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
