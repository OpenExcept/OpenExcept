import pytest
from openexcept import OpenExcept
from openexcept.core import ExceptionEvent
from datetime import datetime, timedelta
import tempfile
import shutil
import os
import yaml

@pytest.fixture(scope="function")
def config_path():
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Create a temporary config file
    config = {
        'storage': {'local_path': temp_dir},
        'embedding': {
            'class': 'SentenceTransformerEmbedding',
            'similarity_threshold': 0.8,
            'kwargs': {'model_name': 'all-mpnet-base-v2'}
        }
    }
    
    config_path = os.path.join(temp_dir, 'config.yaml')
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    
    yield config_path
    
    # Cleanup after test
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")
def grouper(config_path):
    # Create OpenExcept instance with temporary config
    instance = OpenExcept(config_path=config_path)
    
    yield instance

def test_group_exception(grouper):
    group_id1 = grouper.group_exception("Connection refused to database xyz123", "ConnectionError")
    group_id2 = grouper.group_exception("Connection refused to database abc987", "ConnectionError")
    
    assert group_id1 == group_id2
    
    group_id3 = grouper.group_exception("Division by zero", "ZeroDivisionError")
    
    assert group_id3 != group_id1

def test_get_top_exception_groups(grouper):
    exception_data = [
        ("Connection refused to database xyz123", "ConnectionError", 5),
        ("Division by zero", "ZeroDivisionError", 3),
        ("Index out of range", "IndexError", 1)
    ]

    for message, error_type, count in exception_data:
        for _ in range(count):
            grouper.group_exception(message, error_type)

    top_exception_groups = grouper.get_top_exception_groups(limit=3)

    assert len(top_exception_groups) == 3
    for i, (_, _, expected_count) in enumerate(exception_data):
        assert top_exception_groups[i]['count'] == expected_count

def test_exception_hook(config_path):
    import multiprocessing
    import os
    import sys

    def process_function(config_path, exception_type):
        # Redirect stderr to /dev/null to suppress output
        sys.stderr = open(os.devnull, 'w')
        
        grouper = OpenExcept.setup_exception_hook(config_path=config_path)
        if exception_type == 'ZeroDivisionError':
            1 / 0  # This will raise ZeroDivisionError
        elif exception_type == 'ValueError':
            int('not a number')  # This will raise ValueError
        del grouper

    # Start two separate processes
    process1 = multiprocessing.Process(target=process_function, args=(config_path, 'ZeroDivisionError'))
    process2 = multiprocessing.Process(target=process_function, args=(config_path, 'ValueError'))

    process1.start()
    process2.start()

    # Wait for both processes to finish
    process1.join()
    process2.join()

    grouper = OpenExcept.setup_exception_hook(config_path=config_path)
    top_exceptions = grouper.get_top_exception_groups(limit=2)
    
    assert len(top_exceptions) == 2, "Expected 2 exception groups"
    
    # Check ZeroDivisionError
    assert any(group['metadata']['example_type'] == 'ZeroDivisionError' for group in top_exceptions), "ZeroDivisionError not found in top exceptions"
    
    # Check ValueError
    assert any(group['metadata']['example_type'] == 'ValueError' for group in top_exceptions), "ValueError not found in top exceptions"
    
    # Check exception messages
    assert any('division by zero' in group['metadata']['example_message'].lower() for group in top_exceptions), "Expected 'division by zero' message"
    assert any('invalid literal for int' in group['metadata']['example_message'].lower() for group in top_exceptions), "Expected 'invalid literal for int' message"
