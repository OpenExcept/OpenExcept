# OpenExcept API Documentation

## OpenExcept Class

The main class for interacting with the OpenExcept library.

### Methods

#### `__init__(self, config_path: str = None)`

Initializes the OpenExcept instance.

- `config_path`: Path to the configuration file (optional)

#### `group_exception(self, message: str, type_name: str = None, **context) -> str`

Groups an exception and returns the group ID.

- `message`: The exception message
- `type_name`: The exception type name (optional)
- `**context`: Additional context as keyword arguments

Returns: The assigned group ID (str)

#### `get_top_exception_groups(self, limit: int, start_time: datetime = None, end_time: datetime = None) -> List[Dict[str, Any]]`

Retrieves the top exceptions within a specified time range.

- `limit`: Number of top exceptions to return
- `start_time`: Start of the time range (optional)
- `end_time`: End of the time range (optional)

Returns: A list of dictionaries containing information about top exception groups.

#### `get_exception_events(self, group_id: str, start_time: datetime = None, end_time: datetime = None) -> List[ExceptionEvent]`

Retrieves exception events for a specific group within a time range.

- `group_id`: The group ID to retrieve events for
- `start_time`: Start of the time range (optional)
- `end_time`: End of the time range (optional)

Returns: A list of ExceptionEvent objects.

### Class Methods

#### `setup_exception_hook(cls, **kwargs)`

Sets up a global exception hook to automatically group exceptions.

- `**kwargs`: Additional keyword arguments to pass to the OpenExcept constructor

## Example Usage

```python
from openexcept import OpenExcept
from datetime import datetime, timedelta

# Initialize OpenExcept
grouper = OpenExcept()

# Group an exception
group_id = grouper.group_exception("Connection refused to database xyz123", "ConnectionError")

# Get top exceptions for the last 7 days
end_time = datetime.now()
start_time = end_time - timedelta(days=7)
top_exceptions = grouper.get_top_exception_groups(limit=5, start_time=start_time, end_time=end_time)

# Get exception events for a specific group
events = grouper.get_exception_events(group_id, start_time=start_time, end_time=end_time)
```

For more detailed examples, refer to the `examples/` directory in the project repository.
