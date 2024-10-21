import pytest
from openexcept import OpenExcept
from openexcept.core import ExceptionEvent
from datetime import datetime, timedelta

@pytest.fixture(scope="function")
def grouper():
    return OpenExcept()

def test_group_exception(grouper):
    group_id1 = grouper.group_exception("Connection refused to database xyz123", "ConnectionError")
    group_id2 = grouper.group_exception("Connection refused to database abc987", "ConnectionError")
    
    assert group_id1 == group_id2
    
    group_id3 = grouper.group_exception("Division by zero", "ZeroDivisionError")
    
    assert group_id3 != group_id1

def test_get_top_exceptions(grouper):
    # Generate some exceptions
    for _ in range(5):
        grouper.group_exception("Connection refused to database xyz123", "ConnectionError")
    
    for _ in range(3):
        grouper.group_exception("Division by zero", "ZeroDivisionError")
    
    grouper.group_exception("Index out of range", "IndexError")
    
    top_exceptions = grouper.get_top_exceptions(limit=3, days=1)
    
    assert len(top_exceptions) == 3
    assert top_exceptions[0]['count'] == 5
    assert top_exceptions[1]['count'] == 3
    assert top_exceptions[2]['count'] == 1

def test_exception_hook(grouper):
    OpenExcept.setup_exception_hook()
    
    try:
        1 / 0
    except ZeroDivisionError:
        pass  # The exception hook should have processed this

    top_exceptions = grouper.get_top_exceptions(limit=1, days=1)

def test_singleton_behavior():
    # Create two instances of OpenExcept
    instance1 = OpenExcept()
    instance2 = OpenExcept()

    # Check that both instances are the same object
    assert instance1 is instance2

    # Modify an attribute in one instance
    instance1.test_attribute = "test_value"

    # Check that the attribute is present in the other instance
    assert hasattr(instance2, "test_attribute")
    assert instance2.test_attribute == "test_value"

    # Create another instance with a different config path
    instance3 = OpenExcept(config_path="different_config.yaml")

    # Check that it's still the same instance
    assert instance1 is instance3
    assert instance2 is instance3

    # Verify that the config hasn't changed (it should use the first initialized config)
    assert instance3.config == instance1.config
