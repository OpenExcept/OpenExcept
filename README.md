# OpenExcept

OpenExcept is an intelligent exception grouping library that uses machine learning to automatically categorize and group similar exceptions without manual rules.

## Features

- 🤖 Automatic exception grouping using ML - no manual rules needed
- 🎯 Groups similar exceptions together based on semantic meaning
- 🔌 Easy integration with existing logging systems
- 🚀 Simple API for getting started quickly
- 🐳 Docker support for easy deployment

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

This will automatically group exceptions and add the group ID to the log message.

For more detailed examples, check the `examples/logger_integration.py` in the project repository.

## Documentation

For more detailed information, check out our [API Documentation](docs/API.md).

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

## License

This project is licensed under the AGPLv3 License - see the [LICENSE](LICENSE) file for details.
