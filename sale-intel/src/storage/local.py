from pathlib import Path

from src.storage.base import ObjectStorage


class LocalObjectStorage(ObjectStorage):
    """Filesystem-backed store for dev/MVP. Paths are ``local://<relative>``."""

    SCHEME = "local://"

    def __init__(self, root: Path) -> None:
        self._root = root
        self._root.mkdir(parents=True, exist_ok=True)

    def put(self, key: str, content: bytes, content_type: str) -> str:
        target = self._root / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return f"{self.SCHEME}{key}"

    def get(self, path: str) -> bytes:
        if not path.startswith(self.SCHEME):
            raise ValueError(f"Not a local storage path: {path!r}")
        return (self._root / path.removeprefix(self.SCHEME)).read_bytes()
