from datetime import datetime, timedelta
from typing import NamedTuple


class TimeRange(NamedTuple):
    start: datetime
    end: datetime

    def __post_init__(self):
        if self.start >= self.end:
            raise ValueError("Start time must be before end time")

    @classmethod
    def last_n_days(cls, n: int) -> "TimeRange":
        end = datetime.utcnow()
        start = end - timedelta(days=n)
        return cls(start=start, end=end)

    def duration(self) -> timedelta:
        return self.end - self.start

    def contains(self, timestamp: datetime) -> bool:
        return self.start <= timestamp <= self.end