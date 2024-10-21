import os
import traceback

already_shown_errors = set()

def __printExceptionWarning(e: Exception):
    stack_trace = "".join(traceback.format_stack())
    exception = f"WARNING - ignoring {type(e).__name__} '{e}' in:\n\r{stack_trace}"
    if not exception in already_shown_errors:
        print(exception)
    else:
        already_shown_errors.add(exception)


def handleNotImplementedError(error: str):
    if os.getenv("AUTOSAR_IGNORE_NOT_IMPLEMENTED_ERROR") == "1":
        try: 
            raise NotImplementedError(error)
        except NotImplementedError as e:
            __printExceptionWarning(e)
    else:
        raise NotImplementedError(error)

def handleValueError(error: str):
    if os.getenv("AUTOSAR_IGNORE_NOT_IMPLEMENTED_ERROR") == "1":
        try: 
            raise ValueError(error)
        except ValueError as e:
            __printExceptionWarning(e)
    else:
        raise ValueError(error)