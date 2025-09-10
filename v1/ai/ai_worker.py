from PyQt5.QtCore import QThread, pyqtSignal

class AIStreamWorker(QThread):
    chunk = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, assistant, prompt, scan_results=None):
        super().__init__()
        self.assistant = assistant
        self.prompt = prompt
        self.scan_results = scan_results
        self._running = True  # ✅ ADD this line

    def run(self):
        try:
            for part in self.assistant.get_ai_response_stream(self.prompt, scan_results=self.scan_results):
                if not self._running:        # ✅ ADD this check
                    break
                self.chunk.emit(part)
            self.finished.emit()
        except Exception as e:
            self.chunk.emit(f"[AI Error] {e}")
            self.finished.emit()

    def stop(self):             # ✅ ADD this method
        self._running = False


class AIWorker(QThread):
    result = pyqtSignal(str)

    def __init__(self, assistant, prompt, scan_results=None):
        super().__init__()
        self.assistant = assistant
        self.prompt = prompt
        self.scan_results = scan_results

    def run(self):
        try:
            response = self.assistant.get_ai_response(self.prompt, scan_results=self.scan_results)
        except Exception as e:
            response = f"[AI Error] {e}"
        self.result.emit(response)
