import os
import logging
from openexcept import OpenExcept, OpenExceptHandler

def setup_logger_with_grouping():
    # Set up logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    
    # Initialize OpenExceptHandler with config file
    # Replace with the name of the config file you want to use,
    # e.g. config_local_fs.yaml, config_local_url.yaml, config.yaml
    config_name = 'config_local_fs.yaml'
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'openexcept', 'configs', config_name)
    handler = OpenExceptHandler(config_path=config_path)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

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
