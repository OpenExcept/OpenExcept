# OpenExcept

OpenExcept is an AI based exception clustering engine. 

Your application is throwing tons of exceptions, each exception trace is slightly different and many of them do not have pre-defined exception classes. How do you know which exceptions are most common? How do you know there are suddenly increases of certain exception types?

OpenExcept intelligently cluster exceptions based on their semantic meaning, making it easier to identify patterns and address issues more efficiently.

## Features

- 🤖 Automatic Exception Clustering: Uses AI to cluster exceptions without manual intervention. Once they are clustered, you can do analysis much more easily!
- 🔌 Easy Integration: Seamlessly fits into your existing logging systems.
- 🚀 Simple API: Get started quickly with a straightforward and intuitive API.
- 🐳 Docker Support: Easily deployable with Docker for hassle-free setup.

## Installation

```bash
pip install openexcept
```

## Quick Start

### Docker Setup

To use OpenExcept with Docker:

1. Clone the repository:
   ```
   git clone https://github.com/OpenExcept/openexcept.git
   cd openexcept
   ```

2. Build and start the Docker containers:
   ```
   docker-compose up -d
   ```

   This will start two containers:
   - OpenExcept API server on port 8000
   - Qdrant vector database on port 6333

3. Install local dependencies

```bash
pip install -e .
```

4. You can now use the OpenExcept API at `http://localhost:8000`
You can now use it with an example as `python examples/basic_usage.py`

### Basic Usage

```python
from openexcept import OpenExcept

grouper = OpenExcept()

exceptions = [
    "Connection refused to database xyz123",
    "Connection refused to database abc987",
    "Divide by zero error in calculate_average()",
    "Index out of range in process_list()",
    "Connection timeout to service endpoint",
]

for exception in exceptions:
    group_id = grouper.group_exception(exception)

# When we get the top 1 exception group, it should return the group
# that contains "Connection refused to database xyz123" since it occurs the most
top_exception_groups = grouper.get_top_exception_groups(1)
```

### Integrating with Existing Logger

You can easily integrate OpenExcept with your existing logging setup using the provided `OpenExceptHandler`:

```python
import logging
from openexcept.handlers import OpenExceptHandler

# Set up logging
logger = logging.getLogger(__name__)
logger.addHandler(OpenExceptHandler())

# Now, when you log an error, it will be automatically grouped
try:
    1 / 0
except ZeroDivisionError as e:
    logger.error("An error occurred", exc_info=True)
```

This will automatically cluster exceptions and add the cluster ID to the log message.

For more detailed examples, check the `examples/logger_integration.py` in the project repository.

## Documentation

For more detailed information, check out our [API Documentation](docs/API.md).

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

## License

This project is licensed under the AGPLv3 License - see the [LICENSE](LICENSE) file for details.
