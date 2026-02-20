import logging
import threading

class LogBufferHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.buffer = []
        self._buffer_lock = threading.RLock()

    def emit(self, record):
        try:
            log_entry = {
                "level": record.levelname,
                "source": "ShigureCafeBot",
                "content": self.format(record),
                "timestamp": int(record.created * 1000)
            }
            with self._buffer_lock:
                self.buffer.append(log_entry)
        except Exception:
            self.handleError(record)

    def get_and_clear_buffer(self):
        with self._buffer_lock:
            logs = self.buffer
            self.buffer = []
            return logs

log_buffer_handler = LogBufferHandler()

def setup_logger():
    # Change the millisecond separator from ',' to '.'
    logging.Formatter.default_msec_format = '%s.%03d'
    
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        root_logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Console handler: includes time, name, level, and message
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # Buffer handler: only [name] and message (no time, source is handled in emit)
        buffer_formatter = logging.Formatter('[%(name)s] %(message)s')
        log_buffer_handler.setFormatter(buffer_formatter)
        root_logger.addHandler(log_buffer_handler)
    
    return logging.getLogger("ShigureCafeBot")

logger = setup_logger()
