from abc import ABC, abstractmethod
import typing as t
from datetime import datetime, timedelta

class VectorStorage(ABC):
    @abstractmethod
    def store_vector(self, vector: t.List[float], metadata: dict) -> str:
        """
        Store a vector with associated metadata.

        Parameters
        ----------
        vector : t.List[float]
            The vector to be stored.
        metadata : dict
            Additional metadata associated with the vector.

        Returns
        -------
        str
            A unique identifier for the stored vector.
        """
        pass

    @abstractmethod
    def find_similar(self, vector: t.List[float], threshold: float) -> t.List[tuple[str, float]]:
        """
        Find similar vectors to the given vector.

        Parameters
        ----------
        vector : t.List[float]
            The query vector.
        threshold : float
            The similarity threshold.

        Returns
        -------
        t.List[tuple[str, float]]
            A list of tuples containing the identifier and similarity score of similar vectors.
        """
        pass

    @abstractmethod
    def store_exception_event(self, group_id: str, event: 'ExceptionEvent', vector: t.List[float]):
        """
        Store an exception event.

        Parameters
        ----------
        group_id : str
            The identifier of the group to which the exception belongs.
        event : ExceptionEvent
            The exception event to be stored.
        vector : t.List[float]
            The vector representation of the exception event.
        """
        pass

    @abstractmethod
    def get_exception_events(self, group_id: str, start_time: datetime = None, end_time: datetime = None) -> t.List['ExceptionEvent']:
        """
        Get exception events for a specific group within a time range.

        Parameters
        ----------
        group_id : str
            The identifier of the group.
        start_time : datetime, optional
            The start of the time range.
        end_time : datetime, optional
            The end of the time range.

        Returns
        -------
        t.List[ExceptionEvent]
            A list of exception events matching the criteria.
        """
        pass

    @abstractmethod
    def get_top_exception_groups(self, limit: int, start_time: datetime = None, end_time: datetime = None) -> t.List[dict]:
        """
        Get the top exception groups, sorted by number of exceptions for that groupduring the time range in descending order.

        Parameters
        ----------
        limit : int
            The maximum number of exception groups to return.
        start_time : datetime, optional
            The start of the time range to consider for grouping exceptions.
        end_time : datetime, optional
            The end of the time range to consider for grouping exceptions.

        Returns
        -------
        t.List[dict]
            A list of dictionaries containing information about the top exception groups.
            Each dictionary includes:
            - 'group_id': str, the unique identifier for the exception group
            - 'count': int, the number of occurrences of this exception group
            - 'metadata': dict, additional information about the exception group
        """
        pass