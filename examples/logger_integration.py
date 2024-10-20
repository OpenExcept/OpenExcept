import logging
from openexcept import OpenExcept

def setup_logger_with_grouping():
    # Set up OpenExcept
    grouper = OpenExcept()

    # Create a custom logging handler
    class GroupingHandler(logging.Handler):
        def emit(self, record):
            if record.exc_info:
                exc_type, exc_value, _ = record.exc_info
                group_id = grouper.group_exception(str(exc_value), type_name=exc_type.__name__)
                record.msg = f"[Group: {group_id}] {record.msg}"
            print(self.format(record))  # Print to console for demonstration

    # Set up logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    
    # Add the GroupingHandler
    grouping_handler = GroupingHandler()
    grouping_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(grouping_handler)

    return logger

def main():
    logger = setup_logger_with_grouping()

    # Example usage
    try:
        1 / 0
    except ZeroDivisionError as e:
        logger.error("Division by zero error", exc_info=True)

    try:
        int("not a number")
    except ValueError as e:
        logger.error("Value error occurred", exc_info=True)

    # Repeat the first error to show grouping
    try:
        1 / 0
    except ZeroDivisionError as e:
        logger.error("Another division by zero error", exc_info=True)

    # Print top exceptions
    grouper = OpenExcept()
    top_exceptions = grouper.get_top_exceptions(limit=2, days=1)
    print("\nTop 2 exception groups in the last day:")
    for exception in top_exceptions:
        print(f"Group: {exception['group_id']}, Count: {exception['count']}")

if __name__ == "__main__":
    main()