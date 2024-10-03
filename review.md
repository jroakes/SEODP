# File Path: ./src/seodp/lib/logging.py
Changes:
- Imported the `loguru` library
- Configured logging to write to both console and a local file

Code:
```python
import logging
from loguru import logger

# Configure logging to write to both console and a local file
logger.add("seo-dp.log", enqueue=True, rotation="1 week", level="INFO")
logger.add(sys.stderr, level="INFO")
```

This will log messages to both the console and a local file called `seo-dp.log`. The log file will rotate weekly, keeping only the latest week's worth of logs. The default logging level is set to `INFO`, but you can change it as needed for different parts of your application. The `enqueue=True` parameter ensures that log messages are written to the file without blocking the main thread.

You can use `logger` instead of the built-in `logging` module throughout your application. For example:

```python
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
```

Note that if you want to use the built-in `logging` module in other parts of your application, you'll need to configure it separately. Alternatively, you can use `loguru` as a drop-in replacement for the `logging` module by using `logger.bind()`; see the [loguru documentation](https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-logging) for more details.