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
    # Create timestamps for different time periods
    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)
    two_hours_ago = now - timedelta(hours=2)

    # Test data: (message, type, old_count, recent_count, current_count)
    exception_data = [
        ("Connection refused to database xyz123", "ConnectionError", 2, 3, 1),  # 11 total (combined with abc987)
        ("Division by zero", "ZeroDivisionError", 4, 1, 2),                    # 7 total
        ("Index out of range", "IndexError", 1, 2, 3),                         # 6 total
        ("Connection refused to database abc987", "ConnectionError", 1, 2, 2)  # (combined with xyz123)
    ]

    # Store exceptions with different timestamps
    for message, error_type, old_count, recent_count, current_count in exception_data:
        # Old exceptions (1-2 hours ago)
        for _ in range(old_count):
            grouper.group_exception(
                message, 
                error_type, 
                timestamp=two_hours_ago + timedelta(minutes=1)
            )
        
        # Recent exceptions (0-1 hours ago)
        for _ in range(recent_count):
            grouper.group_exception(
                message, 
                error_type, 
                timestamp=one_hour_ago + timedelta(minutes=1)
            )
        
        # Current exceptions
        for _ in range(current_count):
            grouper.group_exception(
                message, 
                error_type, 
                timestamp=now + timedelta(minutes=1)
            )

    # Test different time ranges
    # All time
    all_groups = grouper.get_top_exception_groups(limit=3)
    assert len(all_groups) == 3
    assert sum(group["count"] for group in all_groups) == 24
    assert sorted([group["count"] for group in all_groups]) == [6, 7, 11]

    # Last hour only
    recent_groups = grouper.get_top_exception_groups(
        limit=3, 
        start_time=one_hour_ago
    )
    assert len(recent_groups) == 3
    assert sum(group["count"] for group in recent_groups) == 16
    assert sorted([group["count"] for group in recent_groups]) == [3, 5, 8]

    # Between 2 hours ago and 1 hour ago
    mid_range_groups = grouper.get_top_exception_groups(
        limit=3,
        start_time=two_hours_ago,
        end_time=one_hour_ago
    )
    assert len(mid_range_groups) == 3
    assert sum(group["count"] for group in mid_range_groups) == 8
    assert sorted([group["count"] for group in mid_range_groups]) == [1, 3, 4]

    # Current time only
    current_groups = grouper.get_top_exception_groups(
        limit=3,
        start_time=now
    )
    assert len(current_groups) == 3
    assert sum(group["count"] for group in current_groups) == 8
    assert sorted([group["count"] for group in current_groups]) == [2, 3, 3]

    # Verify ordering for current time period
    assert current_groups[0]["count"] == 3  # ConnectionError or IndexError should be most frequent
    assert current_groups[1]["count"] == 3  # ConnectionError or IndexError should be second most frequent
    assert current_groups[2]["count"] == 2  # ZeroDivisionError least frequent
