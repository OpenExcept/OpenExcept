import pytest
import tempfile
import shutil
import uuid
from datetime import datetime, timedelta
from openexcept.storage.qdrant import QdrantVectorStorage
from openexcept.core import ExceptionEvent
import time

@pytest.fixture(scope="function")
def temp_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")
def qdrant_storage(temp_dir):
    storage = QdrantVectorStorage(path=temp_dir)
    yield storage

def test_store_and_find_similar(qdrant_storage):
    # Store some vectors
    vector1 = [0.1, 0.2, 0.3] * 128  # 384-dimensional vector
    vector2 = [0.2, 0.3, 0.4] * 128
    vector3 = [0.3, 0.4, 0.5] * 128
    
    qdrant_storage.store_vector(vector1, {"error": "Error 1"})
    qdrant_storage.store_vector(vector2, {"error": "Error 2"})
    qdrant_storage.store_vector(vector3, {"error": "Error 3"})
    
    # Find similar vectors
    similar = qdrant_storage.find_similar(vector1, threshold=0.8)
    
    assert len(similar) >= 1
    assert similar[0][1] > 0.9  # The most similar vector should have a high similarity score

def test_store_exception_event_and_count(qdrant_storage):
    # Create a group_id by storing a vector
    vector = [0.5, 0.6, 0.7] * 128
    group_id = qdrant_storage.store_vector(vector, {"error": "Test Error"})
    
    # Create and store two exception events
    event1 = ExceptionEvent(
        id=str(uuid.uuid4()),
        message="Test Exception 1",
        type="ValueError",
        timestamp=datetime.now(),
        stack_trace="Traceback (most recent call last): ...",
        context={"sample_key": "sample_value"}
    )
    qdrant_storage.store_exception_event(group_id, event1, vector)

    event2 = ExceptionEvent(
        id=str(uuid.uuid4()),
        message="Test Exception 2",
        type="ValueError",
        timestamp=datetime.now(),
        stack_trace="Traceback (most recent call last): ...",
        context={"sample_key": "sample_value"}
    )
    qdrant_storage.store_exception_event(group_id, event2, vector)
    
    # Add a small delay to ensure updates are processed
    time.sleep(0.1)
    
    # Verify the count has increased
    results = qdrant_storage.get_top_exception_groups(1)
    print(f"Results from get_top_exception_groups: {results}")
    assert len(results) == 1
    assert results[0]["group_id"] == group_id
    assert results[0]["count"] == 2  # Should count the two events we stored

def test_get_top_exception_groups(qdrant_storage):
    # Store multiple vectors representing exception groups
    vector1 = [0.1, 0.2, 0.3] * 128
    vector2 = [0.2, 0.3, 0.4] * 128
    vector3 = [0.3, 0.4, 0.5] * 128

    id1 = qdrant_storage.store_vector(vector1, {"error": "Frequent Error"})
    id2 = qdrant_storage.store_vector(vector2, {"error": "Less Frequent Error"})
    id3 = qdrant_storage.store_vector(vector3, {"error": "Rare Error"})

    # Timestamp for all events
    timestamp = datetime.now()

    # Store exception events for each group with varying frequencies
    for _ in range(6):
        event = ExceptionEvent(
            id=str(uuid.uuid4()),
            message="Frequent Error Occurred",
            type="TypeError",
            timestamp=timestamp,
            stack_trace="Traceback (most recent call last): ...",
            context={}
        )
        qdrant_storage.store_exception_event(id1, event, vector1)

    for _ in range(4):
        event = ExceptionEvent(
            id=str(uuid.uuid4()),
            message="Less Frequent Error Occurred",
            type="ValueError",
            timestamp=timestamp,
            stack_trace="Traceback (most recent call last): ...",
            context={}
        )
        qdrant_storage.store_exception_event(id2, event, vector2)

    for _ in range(2):
        event = ExceptionEvent(
            id=str(uuid.uuid4()),
            message="Rare Error Occurred",
            type="IndexError",
            timestamp=timestamp,
            stack_trace="Traceback (most recent call last): ...",
            context={}
        )
        qdrant_storage.store_exception_event(id3, event, vector3)

    # Add a small delay to ensure updates are processed
    time.sleep(0.1)

    # Get top exception groups
    top_exceptions = qdrant_storage.get_top_exception_groups(3)

    assert len(top_exceptions) == 3
    assert top_exceptions[0]["group_id"] == id1
    assert top_exceptions[0]["count"] == 6
    assert top_exceptions[1]["group_id"] == id2
    assert top_exceptions[1]["count"] == 4
    assert top_exceptions[2]["group_id"] == id3
    assert top_exceptions[2]["count"] == 2

def test_get_exception_events(qdrant_storage):
    # Store a vector to create a group_id
    vector = [0.1, 0.2, 0.3] * 128
    group_id = qdrant_storage.store_vector(vector, {"error": "Test Error"})

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
        qdrant_storage.store_exception_event(group_id, event, vector)
        events.append(event)

    # Add a small delay to ensure updates are processed
    time.sleep(0.1)

    # Retrieve exception events
    retrieved_events = qdrant_storage.get_exception_events(group_id)

    assert len(retrieved_events) == 5
    # Check that the retrieved events match the stored events
    retrieved_event_ids = set(event.id for event in retrieved_events)
    stored_event_ids = set(event.id for event in events)
    assert retrieved_event_ids == stored_event_ids

def test_find_similar_with_threshold(qdrant_storage):
    # Store some vectors
    vector1 = [0.1, 0.2, 0.3] * 128
    vector2 = [0.1, 0.2, 0.3] * 128  # Exactly the same as vector1
    vector3 = [0.1] * 384  # Different vector

    qdrant_storage.store_vector(vector1, {"error": "Error 1"})
    qdrant_storage.store_vector(vector2, {"error": "Error 2"})
    qdrant_storage.store_vector(vector3, {"error": "Error 3"})
    
    # Find similar vectors with a high threshold
    similar = qdrant_storage.find_similar(vector1, threshold=0.99)
    
    assert len(similar) >= 1  # Only exact or almost exact matches should be returned
    for s in similar:
        assert s[1] > 0.99  # Similarity should be very high (>0.99)
    
    # Find similar vectors with a lower threshold
    similar = qdrant_storage.find_similar(vector1, threshold=0.5)
    
    assert len(similar) == 3  # All vectors should be returned with a low threshold
    # Check that similar[0] is the most similar
    assert similar[0][1] >= similar[1][1] >= similar[2][1]

def test_get_top_exception_groups_with_time_range(qdrant_storage):
    # Store vectors to create group_ids
    vector_a = [0.1, 0.2, 0.3] * 128
    vector_b = [0.4, 0.5, 0.6] * 128
    vector_c = [0.7, 0.8, 0.9] * 128
    group_id_a = qdrant_storage.store_vector(vector_a, {"error": "Exception A"})
    group_id_b = qdrant_storage.store_vector(vector_b, {"error": "Exception B"})
    group_id_c = qdrant_storage.store_vector(vector_c, {"error": "Exception C"})

    # Create timestamps for different time periods
    now = datetime.now()
    one_hour_ago = now - timedelta(hours=1)
    two_hours_ago = now - timedelta(hours=2)

    # Function to create events
    def create_events(group_id, message, count, start_time):
        return [ExceptionEvent(
            id=str(uuid.uuid4()),
            message=message,
            type="ValueError",
            timestamp=start_time + timedelta(minutes=i),
            stack_trace="Traceback (most recent call last): ...",
            context={}
        ) for i in range(count)]

    # Store exception events at different times
    events = [
        # Exception A: 2 old, 3 recent, 1 current
        *create_events(group_id_a, "Exception A", 2, two_hours_ago + timedelta(minutes=1)),
        *create_events(group_id_a, "Exception A", 3, one_hour_ago + timedelta(minutes=1)),
        *create_events(group_id_a, "Exception A", 1, now + timedelta(minutes=1)),

        # Exception B: 4 old, 1 recent, 2 current
        *create_events(group_id_b, "Exception B", 4, two_hours_ago + timedelta(minutes=1)),
        *create_events(group_id_b, "Exception B", 1, one_hour_ago + timedelta(minutes=1)),
        *create_events(group_id_b, "Exception B", 2, now + timedelta(minutes=1)),

        # Exception C: 1 old, 2 recent, 3 current
        *create_events(group_id_c, "Exception C", 1, two_hours_ago + timedelta(minutes=1)),
        *create_events(group_id_c, "Exception C", 2, one_hour_ago + timedelta(minutes=1)),
        *create_events(group_id_c, "Exception C", 3, now + timedelta(minutes=1)),
    ]

    # Store all events
    for event in events:
        if event.message == "Exception A":
            vector = vector_a
        elif event.message == "Exception B":
            vector = vector_b
        else:
            vector = vector_c
        qdrant_storage.store_exception_event(event.message.split()[-1], event, vector)

    # Add a small delay to ensure updates are processed
    time.sleep(0.1)

    # Test different time ranges

    # All events
    all_events = qdrant_storage.get_top_exception_groups(3)
    assert len(all_events) == 3
    assert sum(group["count"] for group in all_events) == 19
    assert sorted([group["count"] for group in all_events]) == [6, 6, 7]

    # Events from the last hour
    last_hour_events = qdrant_storage.get_top_exception_groups(3, start_time=one_hour_ago)
    assert len(last_hour_events) == 3
    assert sum(group["count"] for group in last_hour_events) == 12
    assert sorted([group["count"] for group in last_hour_events]) == [3, 4, 5]

    # Events between 2 hours ago and 1 hour ago
    mid_range_events = qdrant_storage.get_top_exception_groups(3, start_time=two_hours_ago, end_time=one_hour_ago)
    assert len(mid_range_events) == 3
    assert sum(group["count"] for group in mid_range_events) == 7
    assert sorted([group["count"] for group in mid_range_events]) == [1, 2, 4]

    # Events from exactly now
    current_events = qdrant_storage.get_top_exception_groups(3, start_time=now)
    assert len(current_events) == 3
    assert sum(group["count"] for group in current_events) == 6
    assert sorted([group["count"] for group in current_events]) == [1, 2, 3]

    # Verify correct ordering and metadata
    all_time_order = [group["metadata"]["example_message"] for group in all_events]
    assert all_time_order == ["Exception B", "Exception A", "Exception C"] or \
           all_time_order == ["Exception B", "Exception C", "Exception A"]

    last_hour_order = [group["metadata"]["example_message"] for group in last_hour_events]
    assert last_hour_order[0] == "Exception C"
    assert set(last_hour_order[1:]) == {"Exception A", "Exception B"}

    current_order = [group["metadata"]["example_message"] for group in current_events]
    assert current_order == ["Exception C", "Exception B", "Exception A"]
