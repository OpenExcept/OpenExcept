# OpenExcept API Documentation

## OpenExcept Class

The main class for interacting with the OpenExcept library.

### Methods

#### `__init__(self, url: str = "http://localhost:8000", cloud_api_key: Optional[str] = None, qdrant_url: Optional[str] = None)`

Initializes the OpenExcept instance.

- `url`: The URL of the OpenExcept API server (default: "http://localhost:8000")
- `cloud_api_key`: API key for cloud version (optional)
- `qdrant_url`: URL for Qdrant vector database (optional)

#### `group_exception(self, message: str, type_name: str = None, **context) -> str`

Groups an exception and returns the group ID.

- `message`: The exception message
- `type_name`: The exception type name (optional)
- `**context`: Additional context as keyword arguments

Returns: The assigned group ID (str)

#### `get_top_exceptions(self, limit: int = 10, days: int = 1) -> List[Dict]`

Retrieves the top exceptions within a specified time range.

- `limit`: Number of top exceptions to return (default: 10)
- `days`: Number of days to look back (default: 1)

Returns: A list of dictionaries containing group_id, count, and metadata for each top exception group.

## Example Usage

```python
from openexcept import OpenExcept

grouper = OpenExcept()

# Group an exception
group_id = grouper.group_exception("Connection refused to database xyz123", "ConnectionError")

# Get top exceptions
top_exceptions = grouper.get_top_exceptions(limit=5, days=7)
```

For more detailed examples, refer to the `examples/` directory in the project repository.