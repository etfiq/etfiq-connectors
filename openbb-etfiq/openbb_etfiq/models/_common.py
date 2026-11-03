"""Pieces every ETFIQ model shares."""
import asyncio
from typing import Any

from openbb_etfiq.etfiq_client import EtfiqClient, EtfiqError

__version__ = "0.1.0"
_client: EtfiqClient | None = None


def client() -> EtfiqClient:
    global _client
    if _client is None:
        _client = EtfiqClient("openbb", __version__)
    return _client


async def call(fn, *args, **kwargs) -> Any:
    """Run a client read off the event loop; the client paces itself."""
    return await asyncio.to_thread(fn, *args, **kwargs)


def missing(what: str) -> EtfiqError:
    return EtfiqError(f"ETFIQ has no {what}")
