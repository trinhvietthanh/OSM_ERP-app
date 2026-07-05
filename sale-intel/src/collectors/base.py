"""Collector contracts.

Collectors ONLY fetch raw bytes from public pages. They never parse business
data, never write product/promotion rows, and never attempt to bypass
captchas, logins, or anti-bot mechanisms — a blocked response is recorded
as-is (status code and body) and the pipeline moves on.
"""

import abc
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class CollectorResult:
    source_id: str
    url: str
    content_type: str
    raw_content: bytes
    status_code: int
    headers: dict[str, str]
    collected_at: datetime
    metadata: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300


class BaseCollector(abc.ABC):
    """Fetch one URL and return the raw response."""

    @abc.abstractmethod
    async def collect(self, url: str) -> CollectorResult:
        ...
