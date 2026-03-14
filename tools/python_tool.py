from google.adk.tools import FunctionTool
import sys
import io
import contextlib

async def python_interpreter_func(code: str) -> str:
    """
    Executes Python code and returns the printed output.
    Useful for complex math, data processing, and physics simulations.
    """
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        try:
            # Note: In a production environment, this should be sandboxed.
            # For the hackathon, we execute locally.
            exec(code)
        except Exception as e:
            return f"ERROR: {str(e)}"
    return f.getvalue()
