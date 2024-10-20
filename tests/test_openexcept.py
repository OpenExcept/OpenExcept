import pytest
from openexcept import OpenExcept
from openexcept.core import ExceptionEvent
from datetime import datetime, timedelta

@pytest.fixture
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