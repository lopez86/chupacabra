import abc
from contextlib import AbstractContextManager, contextmanager
from typing import Any, Generator

class KeyValueStore(abc.ABC):
    @abc.abstractmethod
    def get(self, key: Any) -> Any:
        """Get a value given its key."""
        raise NotImplementedError()

    @abc.abstractmethod
    def set(
        self,
        key: Any,
        data: Any,
        lifetime: int = 3600
    ) -> bool:
        """Set the value for a key"""
        raise NotImplementedError()

    @abc.abstractmethod
    @contextmanager
    def lock(
        self,
        key: str,
        blocking_timeout: int
    ) -> Generator[AbstractContextManager, None, None]:
        """Lock a key for at most a specific number of seconds"""
        raise NotImplementedError()

    @abc.abstractmethod
    def delete(self, key: Any) -> bool:
        """Delete the value for a key."""
        raise NotImplementedError()
