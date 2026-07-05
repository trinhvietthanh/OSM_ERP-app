import abc


class ObjectStorage(abc.ABC):
    """Raw-content store. Postgres keeps only the returned storage path."""

    @abc.abstractmethod
    def put(self, key: str, content: bytes, content_type: str) -> str:
        """Store *content* under *key*; return the storage path/URI."""
        ...

    @abc.abstractmethod
    def get(self, path: str) -> bytes:
        """Fetch content previously stored at *path*."""
        ...
