from contextlib import AbstractContextManager, contextmanager
from typing import Any, Callable, Generator, Tuple

from redis import StrictRedis


class RedisCacheHandler:
    def __init__(
        self,
        host: str,
        port: int,
        db: int,
        key_serializer: Callable[[Any], str] = None,
        key_deserializer: Callable[[str], Any] = None,
        data_serializer: Callable[[Any], str] = None,
        data_deserializer: Callable[[str], Any] = None
    ) -> None:
        """A handler for a basic redis connection.

        Args:
            host: str, the host url
            port: int, the port on the redis server
            db: int, the DB number
            key_serializer: function, converts keys into strings
            key_deserializer: function, converts key strings back into objects
            data_serializer: function, converts data into strings
            data_deserializer: function, converts data strings back into data
        """
        self._redis = StrictRedis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,
            encoding='utf-8'
        )
        self._key_serializer = key_serializer
        self._key_deserializer = key_deserializer
        self._data_serializer = data_serializer
        self._data_deserializer = data_deserializer

    def get(self, key: Any) -> Any:
        """Get the data for the given key."""
        if self._key_serializer is not None:
            serialized_key = self._key_serializer(key)
        else:
            serialized_key = key

        if not isinstance(serialized_key, str):
            raise AssertionError('Illegal key type {}'.format(type(serialized_key)))

        data = self._redis.get(serialized_key)
        if data is None:
            return data

        if self._data_deserializer is not None:
            deserialized_data = self._data_deserializer(data)
        else:
            deserialized_data = data

        return deserialized_data

    def set(self, key: Any, data: Any, lifetime: int = 3600) -> bool:
        """Set a key, value pair for a given lifetime.

        If the lifetime is non-positive, then it is not given an expiration time.

        Args:
            key: the key, will be serialized to string
            data: the data, must be serialized to a string
            lifetime: int, the expiration time in seconds.

        Returns:
            bool, should be True for a successful operation
        """
        serialized_key, serialized_data = self._get_validated_inputs(key, data)

        if lifetime is None:
            self._redis.set(serialized_key, serialized_data)
        else:
            self._redis.set(serialized_key, serialized_data, ex=lifetime)

        return True

    @contextmanager
    def lock(
        self,
        key: str,
        blocking_timeout: int
    ) -> Generator[AbstractContextManager, None, None]:
        """Get a lock on a resource."""
        with self._redis.lock(key, blocking_timeout=blocking_timeout) as lock:
            yield lock

    def delete(self, key: Any) -> bool:
        """Delete the data for a given key"""
        if self._key_serializer is not None:
            serialized_key = self._key_serializer(key)
        else:
            serialized_key = key

        if not isinstance(serialized_key, str):
            raise AssertionError('Illegal key of type {}'.format(serialized_key))

        self._redis.delete([serialized_key])
        return True

    def _get_validated_inputs(self, key: Any, data: Any) -> Tuple[str, str]:
        if self._key_serializer is not None:
            serialized_key = self._key_serializer(key)
        else:
            serialized_key = key

        if self._data_serializer is not None:
            serialized_data = self._data_serializer(data)
        else:
            serialized_data = data

        if not isinstance(serialized_key, str):
            raise AssertionError('Illegal key of type {}'.format(serialized_key))

        if not isinstance(serialized_key, str):
            raise AssertionError('Illegal data of type {}'.format(serialized_data))

        return serialized_key, serialized_data
