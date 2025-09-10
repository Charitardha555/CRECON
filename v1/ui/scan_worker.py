from PyQt5.QtCore import QThread, pyqtSignal

class ScanWorker(QThread):
    progress = pyqtSignal(str)
    progress_port = pyqtSignal(int)
    finished = pyqtSignal(list)

    def __init__(self, scanner_func, *args, **kwargs):
        super().__init__()
        self.scanner_func = scanner_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        results = []
        def live_callback(line):
            self.progress.emit(line)
            results.append(line)
        def port_progress_callback(port):
            self.progress_port.emit(port)
        # Pass live_callback and port_progress_callback if supported
        self.kwargs['callback'] = live_callback
        self.kwargs['progress_callback'] = port_progress_callback
        try:
            scan_results = self.scanner_func(*self.args, **self.kwargs)
            if isinstance(scan_results, list):
                results.extend(scan_results)
        except Exception as e:
            results.append(f"Scan error: {str(e)}")
        self.finished.emit(results)
