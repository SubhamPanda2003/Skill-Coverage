---
name: error-handling
description: Use when writing Python code that needs exception or error handling.
---

# Error Handling

Catch specific exception types instead of using a bare `except:` clause.

Always chain the original exception using `raise NewError(msg) from err` when re-raising inside an except block.

If the error is recoverable then log a warning and continue execution, and if the error is unrecoverable then raise immediately.

Never use exceptions to control normal program flow.
