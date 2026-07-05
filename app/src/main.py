"""ASGI entrypoint.

``src.main:app`` is the default ``APP_MODULE`` used by the Dockerfile and
``docker/entrypoint.sh``. Run locally with::

    uv run uvicorn src.main:app --reload
"""

import uvicorn

from src.app.application import app  # noqa: F401  (re-exported for the ASGI server)


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
