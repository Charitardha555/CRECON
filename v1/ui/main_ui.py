from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QLineEdit, QFrame, QSizePolicy, QSplitter, QStackedWidget,
    QComboBox, QProgressBar, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QEvent, QMetaObject, Q_ARG
from ai.ai_worker import AIWorker, AIStreamWorker

class CRECONUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("\U0001f4a5 CRECON: AI-Powered Cyber Scanner")
        self.setMinimumSize(800, 600)
        self.resize(1400, 800)
        self.setStyleSheet("background-color: #0d1117; color: white;")
        self.menu_expanded = False
        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar Menu
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(60)
        self.sidebar.setStyleSheet("background-color: #161b22; border-right: 1px solid #30363d;")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(10, 10, 10, 10)
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.menu_button = QPushButton("☰")
        self.menu_button.setFixedSize(40, 40)
        self.menu_button.setStyleSheet("font-size: 20px; background: none; color: white; border: none;")
        self.menu_button.clicked.connect(self.toggle_menu)
        self.sidebar_layout.addWidget(self.menu_button)

        self.menu_buttons = []
        menu_names = ["Scan Target", "Saved Scans", "Settings"]
        for index, name in enumerate(menu_names):
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 10px;
                    text-align: left;
                    font-size: 15px;
                    color: #ddd;
                }
                QPushButton:hover {
                    background-color: #21262d;
                }
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setVisible(False)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            self.sidebar_layout.addWidget(btn)
            self.menu_buttons.append(btn)

        self.sidebar_layout.addStretch()
        self.sidebar.installEventFilter(self)

        # Top Bar
        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(40)
        self.top_bar.setStyleSheet("background-color: #161b22;")
        self.top_bar_layout = QHBoxLayout(self.top_bar)
        self.top_bar_layout.setContentsMargins(10, 0, 10, 0)

        self.title = QLabel("\U0001f4a5 CRECON: AI-Powered Cyber Scanner")
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.top_bar_layout.addWidget(self.title)
        self.top_bar_layout.addStretch()

        # Command & Output Area
        self.command_bar = QHBoxLayout()
        self.command_line = QLineEdit()
        self.command_line.setPlaceholderText("Enter target (IP or domain)")
        self.command_line.setStyleSheet("""
            QLineEdit {
                background-color: #0d1117;
                border: 1px solid #30363d;
                padding: 8px;
                font-family: Consolas;
                font-size: 14px;
                color: #0ff;
            }
        """)
        self.command_bar.addWidget(self.command_line)

        self.scan_type_combo = QComboBox()
        self.scan_type_combo.addItems(["intense scan", "all tcp ports", "ping scan", "quick scan", "detect os", "vuln scan", "syn scan"])
        self.scan_type_combo.setStyleSheet("""
            QComboBox {
                background-color: #0d1117;
                border: 1px solid #30363d;
                padding: 8px;
                font-family: Consolas;
                font-size: 14px;
                color: #0ff;
            }
        """)
        self.command_bar.addWidget(self.scan_type_combo)

        self.scan_button = QPushButton("Scan")
        self.scan_button.setStyleSheet("""
            QPushButton {
                background-color: #238636;
                color: white;
                padding: 8px 16px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
        """)
        self.command_bar.addWidget(self.scan_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #303d3d; background-color: #0d1117; color: #0ff; }")
        self.progress_bar.setMaximum(0)
        self.progress_bar.setVisible(False)
        self.command_bar.addWidget(self.progress_bar)

        # Pages
        self.page_stack = QStackedWidget()
        self.page_stack.setStyleSheet("background-color: #0d1117; border: 1px solid #30363d;")

        scan_page = QTextEdit("Scan results will appear here...")
        scan_page.setStyleSheet("color: #0f0; font-size: 13px; font-family: Consolas;")
        scan_page.setReadOnly(True)
        self.page_stack.addWidget(scan_page)

        self.saved_scans = QListWidget()
        self.saved_scans.setStyleSheet("color: #0af; font-size: 13px; font-family: Consolas;")
        self.saved_scans.itemClicked.connect(self.load_scan)
        self.page_stack.addWidget(self.saved_scans)

        self.settings_page = QWidget()
        self.settings_layout = QVBoxLayout(self.settings_page)
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter OpenAI API Key")
        self.api_key_input.setStyleSheet("""
            QLineEdit {
                background-color: #0d1117;
                border: 1px solid #30363d;
                padding: 8px;
                font-family: Consolas;
                font-size: 13px;
                color: #fff;
            }
        """)
        self.settings_layout.addWidget(self.api_key_input)
        self.toggle_ai = QPushButton("Enable Online AI")
        self.toggle_ai.setStyleSheet("""
            QPushButton {
                background-color: #1f6feb;
                color: white;
                padding: 8px 16px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #388bfd;
            }
        """)
        self.toggle_ai.clicked.connect(self.toggle_ai_mode)
        self.settings_layout.addWidget(self.toggle_ai)
        self.settings_layout.addStretch()
        self.page_stack.addWidget(self.settings_page)

        self.center_frame = QFrame()
        self.center_layout = QVBoxLayout(self.center_frame)
        self.center_layout.setContentsMargins(15, 15, 15, 15)
        self.center_layout.addLayout(self.command_bar)
        self.center_layout.addWidget(self.page_stack)

        # AI Assistant Panel
        self.ai_panel = QFrame()
        self.ai_panel.setMinimumWidth(280)
        self.ai_panel.setStyleSheet("background-color: #161b22; border-left: 1px solid #30363d;")
        self.ai_layout = QVBoxLayout(self.ai_panel)
        self.ai_layout.setContentsMargins(10, 10, 10, 10)

        self.ai_label = QLabel("\U0001f916 AI Assistant")
        self.ai_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.ai_layout.addWidget(self.ai_label)

        self.ai_output = QTextEdit()
        self.ai_output.setReadOnly(True)
        self.ai_output.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                border: 1px solid #30363d;
                font-family: Consolas;
                font-size: 13px;
                color: #aaa;
            }
        """)
        self.ai_layout.addWidget(self.ai_output)

        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("Ask AI: e.g., What ports are vulnerable?")
        self.ai_input.setStyleSheet("""
            QLineEdit {
                background-color: #0d1117;
                border: 1px solid #30363d;
                padding: 8px;
                font-family: Consolas;
                font-size: 13px;
                color: #fff;
            }
        """)
        self.ai_layout.addWidget(self.ai_input)

        self.ask_button = QPushButton("Ask AI")
        self.ask_button.setStyleSheet("""
            QPushButton {
                background-color: #1f6feb;
                color: white;
                padding: 8px 16px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #388bfd;
            }
        """)
        self.ask_button.clicked.connect(self.query_ai)

        self.stop_ai_button = QPushButton("Stop Thinking")
        self.stop_ai_button.setStyleSheet("""
            QPushButton {
                background-color: #d73a49;
                color: white;
                padding: 8px 16px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #cb2431;
            }
        """)
        self.stop_ai_button.clicked.connect(self.stop_ai_stream)
        self.stop_ai_button.setEnabled(False)

        # Place Ask AI and Stop Thinking side by side
        ai_button_row = QHBoxLayout()
        ai_button_row.addWidget(self.ask_button)
        ai_button_row.addWidget(self.stop_ai_button)
        self.ai_layout.addLayout(ai_button_row)

        self.clear_ai_button = QPushButton("Clear Chat")
        self.clear_ai_button.setStyleSheet("""
            QPushButton {
                background-color: #6e7681;
                color: white;
                padding: 8px 16px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #484f58;
            }
        """)
        self.clear_ai_button.clicked.connect(self.ai_output.clear)
        self.ai_layout.addWidget(self.clear_ai_button)

        # Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.center_frame)
        self.splitter.addWidget(self.ai_panel)
        self.splitter.setSizes([1000, 300])

        self.middle_frame = QFrame()
        self.middle_layout = QVBoxLayout(self.middle_frame)
        self.middle_layout.setContentsMargins(0, 0, 0, 0)
        self.middle_layout.addWidget(self.top_bar)
        self.middle_layout.addWidget(self.splitter)

        self.layout.addWidget(self.sidebar)
        self.layout.addWidget(self.middle_frame)

        self.anim = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.anim.setDuration(400)
        self.anim.setEasingCurve(QEasingCurve.InOutQuart)

        self.page_stack.setCurrentIndex(0)
        self.refresh_history()

    def switch_page(self, index):
        self.page_stack.setCurrentIndex(index)

    def toggle_menu(self):
        target_width = 180 if not self.menu_expanded else 60
        self.anim.setStartValue(self.sidebar.width())
        self.anim.setEndValue(target_width)
        self.anim.start()
        for btn in self.menu_buttons:
            btn.setVisible(not self.menu_expanded)
        self.menu_expanded = not self.menu_expanded

    def eventFilter(self, source, event):
        if source == self.sidebar:
            if event.type() == QEvent.Enter and not self.menu_expanded:
                self.toggle_menu()
            elif event.type() == QEvent.Leave and self.menu_expanded:
                self.toggle_menu()
        return super().eventFilter(source, event)

    def append_ai_message(self, message, is_user=False):
        # Show user input in cyan, AI output in white, using HTML formatting
        if not message.strip():
            return
        if is_user:
            html = f'<div style="color:#00ffff;"><b>&gt;&gt; {message}</b></div>'  # Cyan for user
        else:
            html = f'<div style="color:#fff;">{message}</div>'  # White for AI
        # Ensure UI update is in main thread
        QMetaObject.invokeMethod(self.ai_output, "append", Qt.QueuedConnection, Q_ARG(str, html))

    def query_ai(self):
        prompt = self.ai_input.text().strip()
        scan_results = self.page_stack.widget(0).toPlainText().strip()

        if prompt:
            self._ai_buffer = []  # 🔄 Reset buffer
            self.append_ai_message(prompt, is_user=True)

            self.ask_button.setEnabled(False)
            self.stop_ai_button.setEnabled(True)

            QMetaObject.invokeMethod(self.ai_output, "setPlainText", Qt.QueuedConnection, Q_ARG(str, "Thinking..."))

            # Always use streaming worker for all queries (scan or not)
            self.stream_worker = AIStreamWorker(self.assistant, prompt, scan_results)
            self.stream_worker.chunk.connect(self.append_ai_chunk)
            self.stream_worker.finished.connect(self.finish_ai_stream)
            self.stream_worker.start()


    from PyQt5.QtCore import QMetaObject, Qt, Q_ARG

    def append_ai_chunk(self, chunk):
        if not hasattr(self, '_ai_buffer'):
            self._ai_buffer = []

        if chunk.strip():
            # Smart merging: if chunk is a single character, add to previous
            if self._ai_buffer and len(chunk.strip()) == 1:
                self._ai_buffer[-1] += chunk
            else:
                self._ai_buffer.append(chunk)

            # Join everything and update live
            full_text = ''.join(self._ai_buffer).strip()
            QMetaObject.invokeMethod(self.ai_output, "setPlainText", Qt.QueuedConnection, Q_ARG(str, full_text))


    def finish_ai_stream(self):
        # Join all output into a single string and display it as one message
        full_text = ''
        if hasattr(self, '_ai_buffer') and self._ai_buffer:
            full_text = ''.join(self._ai_buffer).strip()
            self._ai_buffer = []
        # Remove duplicate output if present (e.g., repeated blocks)
        if full_text:
            # If output is repeated twice, keep only one
            mid = len(full_text) // 2
            if full_text[:mid] == full_text[mid:]:
                full_text = full_text[:mid]
            last = self.ai_output.toPlainText().strip()
            if last != full_text:
                self.append_ai_message(full_text, is_user=False)
        self.ai_input.clear()
        self.ask_button.setEnabled(True)
        self.stop_ai_button.setEnabled(False)


    def stop_ai_stream(self):
        self.stop_ai_button.setEnabled(False)

        if hasattr(self, 'stream_worker'):
            try:
                self.stream_worker.stop()
            except Exception:
                pass

            if self.stream_worker.isRunning():
                self.stream_worker.wait(1000)

        self.finish_ai_stream()


    def refresh_history(self):
        self.saved_scans.clear()
        import os
        os.makedirs("scan_history", exist_ok=True)
        for file in sorted(os.listdir("scan_history"), reverse=True):
            # Accept any .txt file in scan_history, not just _scan.txt
            if file.endswith(".txt"):
                item = QListWidgetItem(file)
                self.saved_scans.addItem(item)

    def load_scan(self, item):
        import os
        path = os.path.join("scan_history", item.text())
        try:
            with open(path, "r", encoding="utf-8") as f:
                scan_text = f.read()
                self.page_stack.widget(0).setText(scan_text)
                self.page_stack.setCurrentIndex(0)

                # ✅ Start AI analysis (proper streaming)
                self.ask_button.setEnabled(False)
                self.stop_ai_button.setEnabled(True)
                self._ai_buffer = []

                self.stream_worker = AIStreamWorker(self.assistant, "Analyze the following scan results for vulnerabilities:", scan_results=scan_text)
                self.stream_worker.chunk.connect(self.append_ai_chunk)
                self.stream_worker.finished.connect(self.finish_ai_stream)
                self.stream_worker.start()

        except Exception as e:
            self.show_error(f"Failed to load scan: {str(e)}")


    def start_scan_progress(self):
        self.progress_bar.setVisible(True)

    def stop_scan_progress(self):
        self.progress_bar.setVisible(False)

    def show_error(self, message):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error", message)

    def toggle_ai_mode(self):
        use_openai = not self.assistant.use_openai
        self.assistant.set_api_key(self.api_key_input.text(), use_openai)
        self.toggle_ai.setText("Disable Online AI" if use_openai else "Enable Online AI")
        # Save API key immediately
        # (already handled in set_api_key)

    def showEvent(self, event):
        super().showEvent(event)
        # Preload API key when window is shown
        if hasattr(self, 'api_key_input') and hasattr(self, 'assistant'):
            self.api_key_input.setText(self.assistant.api_key or "")

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = CRECONUI()
    window.show()
    sys.exit(app.exec_())

