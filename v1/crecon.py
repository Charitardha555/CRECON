import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from ui import main_ui
from core import scanner
from ui.scan_worker import ScanWorker
from PyQt5.QtCore import Qt
from ai.ai_assistant import AIAssistant

class CRECONController:
    def __init__(self):
        self.ai_assistant = AIAssistant()
        self.window = main_ui.CRECONUI()
        self.window.scan_button.clicked.connect(self.run_scan)
        self.window.assistant = self.ai_assistant
        # Preload API key in settings tab
        self.window.api_key_input.setText(self.ai_assistant.api_key or "")
        self.window.toggle_ai.setText("Disable Online AI" if self.ai_assistant.use_openai else "Enable Online AI")

    def run_scan(self):
        # Stop any previous scan worker before starting a new one
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        target = self.window.command_line.text().strip()
        scan_type_ui = self.window.scan_type_combo.currentText().lower()

        if not target:
            self.window.show_error("Please enter a target.")
            return

        scan_map = {
            "intense scan": "tcp connect",
            "all tcp ports": "tcp connect",
            "ping scan": "ping scan",
            "quick scan": "tcp ping",
            "detect os": "os detect",
            "syn scan": "syn scan",
            "vuln scan": "tcp connect",  # fallback for now
        }
        scan_type = scan_map.get(scan_type_ui, "tcp connect")
        port_range = "1-65535" if scan_type_ui == "all tcp ports" else "1-1024"

        self.window.start_scan_progress()
        self.window.page_stack.widget(0).setText("")
        self._last_scanned_port = None

        def scanner_func(target, scan_type, port_range, callback=None, progress_callback=None):
            return scanner.scan_target(target, scan_type, port_range=port_range, callback=callback, progress_callback=progress_callback)

        self.worker = ScanWorker(scanner_func, target, scan_type, port_range)
        self.worker.progress.connect(self.append_live_output)
        self.worker.progress_port.connect(self.update_scanning_port)
        self.worker.finished.connect(self.scan_finished)
        self.worker.start()

    def update_scanning_port(self, port):
        # Show scanning port as a single changing line at the end
        current = self.window.page_stack.widget(0).toPlainText().splitlines()
        if self._last_scanned_port is not None and current and current[-1].startswith("scanning port:"):
            current = current[:-1]
        current.append(f"scanning port: {port}")
        self.window.page_stack.widget(0).setText("\n".join(current))
        self._last_scanned_port = port

    def append_live_output(self, line):
        current = self.window.page_stack.widget(0).toPlainText().splitlines()
        # Remove the last scanning port line if present
        if self._last_scanned_port is not None and current and current[-1].startswith("scanning port:"):
            current = current[:-1]
        current.append(line)
        # Add back the scanning port line if still scanning
        if self._last_scanned_port is not None:
            current.append(f"scanning port: {self._last_scanned_port}")
        self.window.page_stack.widget(0).setText("\n".join(current))

    def scan_finished(self, results):
        self.window.stop_scan_progress()
        self._last_scanned_port = None
        # Save report with new format: [date][time][nameofscan][target].txt
        timestamp = datetime.now().strftime("[%Y-%m-%d][%H-%M-%S]")
        scan_type_ui = self.window.scan_type_combo.currentText().lower().replace(' ', '_')
        target = self.window.command_line.text().strip().replace(':', '_').replace('/', '_')
        filename = f"scan_history/{timestamp}[{scan_type_ui}][{target}].txt"
        os.makedirs("scan_history", exist_ok=True)
        # Always save something, even if results is empty
        if not results:
            results = ["[No scan output generated]"]
        report = "\n".join(results)
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report)
        except Exception as e:
            print(f"[ERROR] Could not save scan: {e}")
        self.window.page_stack.widget(0).setText(report)
        self.window.refresh_history()
        # --- AI suggestions after scan ---
        self.window.append_ai_message(
            f"Suggest known exploits, CVEs, and vulnerabilities for the following scan results:", is_user=True)
        self.window.ask_button.setEnabled(False)
        self.window.stop_ai_button.setEnabled(True)
        scan_results = report
        prompt = "Suggest known exploits, CVEs, and vulnerabilities for the above scan results. List only actionable, relevant items."
        self.window.append_ai_message("Thinking...", is_user=False)
        # Only show AI suggestions in chat, not scan results
        def stream_ai():
            for chunk in self.ai_assistant.get_ai_response_stream(prompt, scan_results):
                self.window.append_ai_message(chunk, is_user=False)
            self.window.ask_button.setEnabled(True)
            self.window.stop_ai_button.setEnabled(False)
        import threading
        threading.Thread(target=stream_ai, daemon=True).start()

    def handle_ai_scan_request(self, prompt):
        """Detects scan requests in the AI/user prompt and triggers a scan if found."""
        import re
        # Example patterns: scan 192.168.1.1, scan 10.0.0.1 for open ports, scan example.com
        scan_pattern = re.compile(r"scan\s+([\w\.-]+)(?:\s+for\s+([\w\s]+))?", re.IGNORECASE)
        match = scan_pattern.search(prompt)
        if match:
            target = match.group(1)
            scan_type = match.group(2) or "intense scan"
            # Map keywords to scan types
            scan_type_map = {
                "open ports": "intense scan",
                "tcp": "intense scan",
                "udp": "udp scan",
                "os": "detect os",
                "vuln": "vuln scan",
                "syn": "syn scan",
            }
            for key, val in scan_type_map.items():
                if key in scan_type.lower():
                    scan_type = val
                    break
            # Set UI fields and trigger scan
            self.window.command_line.setText(target)
            idx = self.window.scan_type_combo.findText(scan_type, Qt.MatchContains)
            if idx != -1:
                self.window.scan_type_combo.setCurrentIndex(idx)
            self.run_scan()
            # Do NOT show any scan output or message in the AI chat
            return True
        return False

    def get_ai_response(self, prompt):
        # If the prompt is a scan request, trigger scan and return a message
        if self.handle_ai_scan_request(prompt):
            return ""  # Suppress all AI chat output for scan triggers
        return self.ai_assistant.get_ai_response(prompt)

    def set_api_key(self, key, use_openai):
        self.ai_assistant.set_api_key(key, use_openai)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = CRECONController()
    controller.window.show()
    sys.exit(app.exec_())
