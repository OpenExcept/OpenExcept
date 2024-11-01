import pytest
import uuid
from datetime import datetime, timedelta
import os
from openexcept.storage.postgres import PostgresVectorStorage
from openexcept.core import ExceptionEvent
import time

# Test database connection string
TEST_DB_URL = os.getenv('TEST_POSTGRES_URL', 'postgresql://postgres:postgres@localhost:5432/test_openexcept')

@pytest.fixture(scope="function")
def postgres_storage():
    """Create a test database and return a PostgresVectorStorage instance."""
    storage = PostgresVectorStorage(TEST_DB_URL)
    
    # Clean up any existing test data
    with storage._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS exception_events")
            cur.execute("DROP TABLE IF EXISTS exception_groups")
    
    # Initialize fresh tables
    storage._ensure_tables()
    
    yield storage
    
    # Cleanup after tests
    with storage._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS exception_events")
            cur.execute("DROP TABLE IF EXISTS exception_groups")

def test_store_and_find_similar(postgres_storage):
    # Store some vectors
    vector1 = [0.1, 0.2, 0.3] * 128  # 384-dimensional vector
    vector2 = [0.2, 0.3, 0.4] * 128
    vector3 = [0.3, 0.4, 0.5] * 128
    
    group1_id = postgres_storage.store_vector(vector1, {"error": "Error 1"})
    group2_id = postgres_storage.store_vector(vector2, {"error": "Error 2"})
    group3_id = postgres_storage.store_vector(vector3, {"error": "Error 3"})
    
    # Find similar vectors
    similar = postgres_storage.find_similar(vector1, threshold=0.8)
    
    assert len(similar) >= 1
    assert similar[0][1] > 0.9  # The most similar vector should have a high similarity score
    assert similar[0][0] == group1_id

def test_store_exception_event_and_count(postgres_storage):
    # Create a group_id by storing a vector
    vector = [0.5, 0.6, 0.7] * 128
    group_id = postgres_storage.store_vector(vector, {"error": "Test Error"})
    
    # Create and store two exception events
    event1 = ExceptionEvent(
        id=str(uuid.uuid4()),
        message="Test Exception 1",
        type="ValueError",
        timestamp=datetime.now(),
        stack_trace="Traceback (most recent call last): ...",
        context={"sample_key": "sample_value"}
    )
    postgres_storage.store_exception_event(group_id, event1, vector)

    event2 = ExceptionEvent(
        id=str(uuid.uuid4()),
        message="Test Exception 2",
        type="ValueError",
        timestamp=datetime.now(),
        stack_trace="Traceback (most recent call last): ...",
        context={"sample_key": "sample_value"}
    )
    postgres_storage.store_exception_event(group_id, event2, vector)
    
    # Verify the count has increased
    results = postgres_storage.get_top_exception_groups(1)
    assert len(results) == 1
    assert results[0]["group_id"] == group_id
    assert results[0]["count"] == 2

def test_get_exception_events(postgres_storage):
    # Store a vector to create a group_id
    vector = [0.1, 0.2, 0.3] * 128
    group_id = postgres_storage.store_vector(vector, {"error": "Test Error"})

    # Store exception events for the group
    timestamps = [datetime.now() - timedelta(minutes=i) for i in range(5)]
    events = []
    for ts in timestamps:
        event = ExceptionEvent(
            id=str(uuid.uuid4()),
            message="Test Exception",
            type="ValueError",
            timestamp=ts,
            stack_trace="Traceback (most recent call last): ...",
            context={}
        )
        postgres_storage.store_exception_event(group_id, event, vector)
        events.append(event)

    # Retrieve exception events
    retrieved_events = postgres_storage.get_exception_events(group_id)

    assert len(retrieved_events) == 5
    # Check that the retrieved events match the stored events
    retrieved_event_ids = set(event.id for event in retrieved_events)
    stored_event_ids = set(event.id for event in events)
    assert retrieved_event_ids == stored_event_ids

def test_get_top_exception_groups_with_time_range(postgres_storage):
    # Store vectors to create group_ids
    vector_a = [0.1, 0.2, 0.3] * 128
    vector_b = [0.4, 0.5, 0.6] * 128
    group_id_a = postgres_storage.store_vector(vector_a, {"error": "Exception A"})
    group_id_b = postgres_storage.store_vector(vector_b, {"error": "Exception B"})

    # Create timestamps for different time periods
    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)
    two_hours_ago = now - timedelta(hours=2)

    # Store events in different time periods
    for i in range(3):
        event = ExceptionEvent(
            id=str(uuid.uuid4()),
            message="Exception A",
            type="ValueError",
            timestamp=now - timedelta(minutes=i),
            stack_trace="...",
            context={}
        )
        postgres_storage.store_exception_event(group_id_a, event, vector_a)

    for i in range(2):
        event = ExceptionEvent(
            id=str(uuid.uuid4()),
            message="Exception B",
            type="ValueError",
            timestamp=one_hour_ago - timedelta(minutes=i),
            stack_trace="...",
            context={}
        )
        postgres_storage.store_exception_event(group_id_b, event, vector_b)

    # Test different time ranges
    all_groups = postgres_storage.get_top_exception_groups(10)
    assert len(all_groups) == 2
    assert all_groups[0]["count"] == 3  # Group A has more recent events
    assert all_groups[1]["count"] == 2

    # Test with time range
    recent_groups = postgres_storage.get_top_exception_groups(
        10, 
        start_time=now - timedelta(minutes=30)
    )
    assert len(recent_groups) == 1
    assert recent_groups[0]["group_id"] == group_id_a

def test_find_similar_with_threshold(postgres_storage):
    # Store some vectors
    vector1 = [0.1, 0.2, 0.3] * 128
    vector2 = [0.1, 0.2, 0.3] * 128  # Exactly the same as vector1
    vector3 = [0.9, 0.8, 0.7] * 128  # Different vector
    
    postgres_storage.store_vector(vector1, {"error": "Error 1"})
    postgres_storage.store_vector(vector2, {"error": "Error 2"})
    postgres_storage.store_vector(vector3, {"error": "Error 3"})
    
    # Find similar vectors with a high threshold
    similar = postgres_storage.find_similar(vector1, threshold=0.99)
    assert len(similar) == 2  # Should find vector1 and vector2
    
    # Find similar vectors with a lower threshold
    similar = postgres_storage.find_similar(vector1, threshold=0.5)
    assert len(similar) == 3  # Should find all vectors 