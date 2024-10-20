import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from openexcept.storage.qdrant import QdrantVectorStorage
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
    similar = qdrant_storage.find_similar(vector1, 0.8)
    
    assert len(similar) >= 1
    assert similar[0][1] > 0.9  # The most similar vector should have a high similarity score

def test_increment_occurrence(qdrant_storage):
    vector = [0.5, 0.6, 0.7] * 128
    group_id = qdrant_storage.store_vector(vector, {"error": "Test Error"})
    
    # Increment occurrence
    qdrant_storage.increment_occurrence(group_id, datetime.now())
    qdrant_storage.increment_occurrence(group_id, datetime.now())
    
    # Add a small delay to ensure updates are processed
    time.sleep(0.1)

    # Verify the count has increased
    results = qdrant_storage.get_top_exceptions(1, timedelta(days=1))
    print(f"Results from get_top_exceptions: {results}")  # Add this debug print
    assert len(results) == 1
    assert results[0]["group_id"] == group_id
    assert results[0]["count"] == 3  # Initial count (1) + 2 increments

def test_get_top_exceptions(qdrant_storage):
    # Store multiple vectors with different counts
    vector1 = [0.1, 0.2, 0.3] * 128
    vector2 = [0.2, 0.3, 0.4] * 128
    vector3 = [0.3, 0.4, 0.5] * 128
    
    id1 = qdrant_storage.store_vector(vector1, {"error": "Frequent Error"})
    id2 = qdrant_storage.store_vector(vector2, {"error": "Less Frequent Error"})
    id3 = qdrant_storage.store_vector(vector3, {"error": "Rare Error"})
    
    # Increment occurrences
    for _ in range(5):
        qdrant_storage.increment_occurrence(id1, datetime.now())
    for _ in range(3):
        qdrant_storage.increment_occurrence(id2, datetime.now())
    qdrant_storage.increment_occurrence(id3, datetime.now())
    
    # Get top exceptions
    top_exceptions = qdrant_storage.get_top_exceptions(3, timedelta(days=1))
    
    assert len(top_exceptions) == 3
    assert top_exceptions[0]["group_id"] == id1
    assert top_exceptions[0]["count"] == 6  # Initial count (1) + 5 increments
    assert top_exceptions[1]["group_id"] == id2
    assert top_exceptions[1]["count"] == 4  # Initial count (1) + 3 increments
    assert top_exceptions[2]["group_id"] == id3
    assert top_exceptions[2]["count"] == 2  # Initial count (1) + 1 increment

def test_find_similar_with_threshold(qdrant_storage):
    # Store some vectors
    vector1 = [0.1, 0.2, 0.3] * 128
    vector2 = [0.2, 0.3, 0.4, 0.2, 0.3, 0.7] * 64
    vector3 = [0.1] * 384
    # Similarity between vector1 and vector2 is 0.9707253433941512
    # Similarity between vector1 and vector3 is 0.9258200997725515
    # Similarity between vector2 and vector3 is 0.898717034272917

    qdrant_storage.store_vector(vector1, {"error": "Error 1"})
    qdrant_storage.store_vector(vector2, {"error": "Error 2"})
    qdrant_storage.store_vector(vector3, {"error": "Error 3"})
    
    # Find similar vectors with a high threshold
    similar = qdrant_storage.find_similar(vector1, 0.98)
    
    assert len(similar) == 1  # Only the exact match should be returned
    assert similar[0][1] > 0.99  # The similarity should be very high

    # Find similar vectors with a lower threshold
    similar = qdrant_storage.find_similar(vector1, 0.95)
    
    assert len(similar) == 2  # The first two vectors should be returned
    assert similar[0][1] > 0.99  # The first match should be very similar
    assert 0.95 < similar[1][1] < 0.98  # The second match should be somewhat similar
