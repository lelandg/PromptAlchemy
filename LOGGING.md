# PromptAlchemy Logging System

## Overview

PromptAlchemy implements comprehensive logging with automatic rotation to track application behavior, debug issues, and audit API usage.

## Log Location

Logs are stored in the platform-specific AppData folder:

- **Windows**: `%APPDATA%\PromptAlchemy\logs\`
- **Linux/WSL**: `~/.config/PromptAlchemy/logs/`
- **macOS**: `~/Library/Application Support/PromptAlchemy/logs/`

## Log Files

- **Main log**: `promptalchemy.log` - Current log file
- **Rotated logs**: `promptalchemy.log.1`, `promptalchemy.log.2`, etc.

### Rotation Settings

- **Max file size**: 10 MB per file
- **Backup count**: 5 files (50 MB total)
- **Encoding**: UTF-8

When a log file reaches 10MB, it's automatically rotated:
- `promptalchemy.log` → `promptalchemy.log.1`
- `promptalchemy.log.1` → `promptalchemy.log.2`
- ... and so on

The oldest backup is deleted when the count exceeds 5.

## Log Levels

The application uses standard Python logging levels:

- **DEBUG**: Detailed diagnostic information (auth modes, token counts, file operations)
- **INFO**: General informational messages (startup, API calls, config changes)
- **WARNING**: Warning messages (missing files, deprecated features)
- **ERROR**: Error messages (API failures, exceptions)
- **CRITICAL**: Critical errors (startup failures)

### Default Log Level

- **File logs**: INFO (captures INFO, WARNING, ERROR, CRITICAL)
- **Console output**: INFO (same as file, for development)

## What Gets Logged

### Application Lifecycle
```
2025-10-12 10:15:12 - core.logging_config - INFO - PromptAlchemy Logging Initialized
2025-10-12 10:15:12 - __main__ - INFO - Starting PromptAlchemy...
2025-10-12 10:15:12 - __main__ - INFO - Configuration directory: /home/leland/.config/PromptAlchemy
```

### Configuration Changes
```
2025-10-12 10:15:12 - core.config - INFO - Found ImageAI config with data at: C:\Users\...\ImageAI\config.json
2025-10-12 10:20:45 - core.config - INFO - Setting API key for provider: openai
2025-10-12 10:20:45 - core.config - DEBUG - API key stored in keyring for openai
```

Note: API keys and passwords are masked in logs as `***` for security.

### API Calls
```
2025-10-12 10:30:15 - core.enhancer - INFO - Calling gemini/gemini-2.0-flash-exp to enhance prompt
2025-10-12 10:30:15 - core.enhancer - DEBUG - Auth mode: gcloud, Temperature: 0.7, Max tokens: 4096
2025-10-12 10:30:18 - core.enhancer - INFO - API Call Success - Provider: gemini, Model: gemini-2.0-flash-exp, Tokens: 1547
2025-10-12 10:30:18 - core.enhancer - INFO - Enhancement completed in 2.83s, tokens: 1547
```

### Errors and Exceptions
```
2025-10-12 10:35:22 - core.enhancer - ERROR - API Call Failed - Provider: openai, Model: gpt-4, Error: API key not found
2025-10-12 10:35:22 - core.enhancer - ERROR - Exception in enhance_prompt: API key for openai not configured
Traceback (most recent call last):
  File "/path/to/enhancer.py", line 140, in enhance_prompt
    raise ValueError(f"API key for {provider} not configured")
ValueError: API key for openai not configured
```

## Programmatic Access

### Setup Logging

```python
from core.logging_config import setup_logging
from core.config import ConfigManager

config = ConfigManager()
log_file = setup_logging(
    config.config_dir,
    log_level="INFO",
    console_output=True
)
```

### Log Exception

```python
from core.logging_config import log_exception
import logging

logger = logging.getLogger(__name__)

try:
    # Your code here
    pass
except Exception as e:
    log_exception(logger, e, "function_name")
```

### Log API Call

```python
from core.logging_config import log_api_call

# Success
log_api_call(logger, "openai", "gpt-4", True, tokens=1500)

# Failure
log_api_call(logger, "openai", "gpt-4", False, error="API key not found")
```

### Log Configuration Change

```python
from core.logging_config import log_config_change

log_config_change(logger, "default_model", "gpt-3.5", "gpt-4")
# Output: Config Changed - default_model: gpt-3.5 -> gpt-4

log_config_change(logger, "api_key", "old_key", "new_key")
# Output: Config Changed - api_key: *** -> ***
```

### Get Recent Logs

```python
from core.logging_config import get_recent_logs

recent = get_recent_logs(config.config_dir, lines=100)
print(recent)
```

### Get All Log Files

```python
from core.logging_config import get_log_files

log_files = get_log_files(config.config_dir)
for log_file in log_files:
    print(f"{log_file.name}: {log_file.stat().st_size} bytes")
```

## Debugging

To enable DEBUG level logging, modify `main.py`:

```python
log_file = setup_logging(
    config.config_dir,
    log_level="DEBUG",  # Changed from "INFO"
    console_output=True
)
```

This will log much more detailed information including:
- Authentication modes for each API call
- Request/response sizes
- File operations
- Configuration lookups

## Privacy and Security

### Automatic Masking

The logging system automatically masks sensitive information:
- API keys: Logged as `***`
- Passwords: Logged as `***`
- Tokens: Logged as `***`

### What's NOT Logged

- Full API keys or passwords
- User prompts (unless DEBUG level is used)
- Enhanced prompt content (unless DEBUG level is used)
- Personal file paths (only filenames are logged)

### Safe Information

The following is safe to share from logs:
- Timestamps and durations
- Provider and model names
- Token counts
- Error messages
- Configuration keys (not values)

## Troubleshooting

### No logs appearing

1. Check if log directory exists:
   ```bash
   # Linux/WSL
   ls -la ~/.config/PromptAlchemy/logs/

   # Windows
   dir %APPDATA%\PromptAlchemy\logs\
   ```

2. Check file permissions (Linux/Mac):
   ```bash
   chmod 755 ~/.config/PromptAlchemy/logs/
   ```

3. Verify logging is initialized:
   ```python
   import logging
   logger = logging.getLogger()
   print(f"Log level: {logger.level}")
   print(f"Handlers: {logger.handlers}")
   ```

### Logs too large

Logs automatically rotate at 10MB, but if you need to clear them:

```bash
# Linux/WSL
rm ~/.config/PromptAlchemy/logs/*.log*

# Windows
del %APPDATA%\PromptAlchemy\logs\*.log*
```

The application will create new log files automatically.

### View logs in real-time

```bash
# Linux/WSL
tail -f ~/.config/PromptAlchemy/logs/promptalchemy.log

# Windows PowerShell
Get-Content "$env:APPDATA\PromptAlchemy\logs\promptalchemy.log" -Wait
```

## Log Format

Each log entry follows this format:
```
YYYY-MM-DD HH:MM:SS - module.name - LEVEL - Message
```

Example:
```
2025-10-12 10:15:12 - core.enhancer - INFO - Calling gemini/gemini-2.0-flash-exp to enhance prompt
```

## Best Practices

1. **Check logs first** when troubleshooting issues
2. **Include log excerpts** when reporting bugs (mask any sensitive data)
3. **Monitor log size** in production environments
4. **Use DEBUG level** only during development
5. **Archive important logs** before clearing

## Integration with Other Tools

The log files are standard UTF-8 text files and can be:
- Opened in any text editor
- Parsed with grep, awk, sed
- Imported into log analysis tools
- Monitored with tools like Logwatch or Splunk
- Searched with tools like `jq` (after converting to JSON)

## Future Enhancements

Planned logging improvements:
- [ ] JSON formatted logs (optional)
- [ ] Remote logging support (syslog, HTTP)
- [ ] Performance metrics tracking
- [ ] Log compression for archives
- [ ] Web-based log viewer
