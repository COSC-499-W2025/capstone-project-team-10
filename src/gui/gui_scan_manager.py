import PyQt5.QtCore as QtCore
from src.fss.fss import FSS_Search, search
import src.log.log as log
import sys

class _EmitStream(QtCore.QObject):
    text_written = QtCore.pyqtSignal(str)

    def write(self, text):
        if text and text.strip():
            self.text_written.emit(text)

    def flush(self):
        pass

class ScanWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal(int)
    failed = QtCore.pyqtSignal(str)
    output = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.directory_path = None
        self.filters = None
        self._stream = _EmitStream()
        self._stream.text_written.connect(self.output.emit)

    @QtCore.pyqtSlot(str, dict)
    def run_scan(self, directory_path: str, filters: dict):
        self.directory_path = directory_path
        self.filters = filters

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = self._stream
        sys.stderr = self._stream

        try:
            if filters.get('clean', False):
                log.open_log_file()

            search_params = FSS_Search(
                input_path=directory_path,
                excluded_path=filters.get('excluded_paths', set()),
                file_types=filters.get('file_types', set()),
                time_lower_bound=filters.get('time_lower_bound', None),
                time_upper_bound=filters.get('time_upper_bound', None),
            )
            result = search(search_params)
            self.finished.emit(result)
        except Exception as ex:
            self.failed.emit(str(ex))
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

class ScanManager(QtCore.QObject):
    scan_started = QtCore.pyqtSignal()
    scan_finished = QtCore.pyqtSignal(int)
    scan_failed = QtCore.pyqtSignal(str)
    scan_output = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.last_result = None
        self._is_scanning = False

        # Create persistent thread and worker
        self._thread = QtCore.QThread()
        self._worker = ScanWorker()
        self._worker.moveToThread(self._thread)

        # Connect worker signals
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._worker.output.connect(self.scan_output)

        # Start thread (runs forever until explicitly quit)
        self._thread.start()

    def scan_async(self, directory_path: str, filters: dict):
        if self._is_scanning:
            return False

        self._is_scanning = True
        self.scan_started.emit()
        
        # Emit signal to worker to run scan
        QtCore.QMetaObject.invokeMethod(
            self._worker,
            "run_scan",
            QtCore.Qt.QueuedConnection,
            QtCore.Q_ARG(str, directory_path),
            QtCore.Q_ARG(dict, filters)
        )
        return True

    @QtCore.pyqtSlot(int)
    def _on_finished(self, result: int):
        self.last_result = result
        self._is_scanning = False
        self.scan_finished.emit(result)

    @QtCore.pyqtSlot(str)
    def _on_failed(self, message: str):
        self._is_scanning = False
        self.scan_failed.emit(message)

    def get_scan_results(self):
        return self