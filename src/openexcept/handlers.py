import logging
from .easy import OpenExcept

class OpenExceptHandler(logging.Handler):
    def __init__(self, config_path=None):
        super().__init__()
        self.grouper = OpenExcept(config_path=config_path)

    def emit(self, record):
        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            group_id = self.grouper.group_exception(str(exc_value), type_name=exc_type.__name__)
            record.msg = f"[Group: {group_id}] {record.msg}"
        print(self.format(record))  # Print to console for demonstration
