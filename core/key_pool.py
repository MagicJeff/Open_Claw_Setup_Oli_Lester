"""
OpenClaw — Gemini Key Pool
Rotates through multiple API keys. When a key hits 429/503, it's marked
exhausted and the next key is tried. Keys reset after 24 hours (free tier
daily quota window). All consumers (Flash, Comms, carousel arbiter) share
the same pool so quota is distributed across all available keys.

Each key must be from a SEPARATE Google AI Studio project to get independent
quotas. Create at: aistudio.google.com/apikey → "Create API key in new project"
"""
import logging
import os
import time
from threading import Lock

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_RESET_AFTER_SECS = 86400  # 24 hours — free tier daily reset window
_TRANSIENT_BACKOFF_SECS = 60  # 503s reset after 1 minute (transient outage)


def _load_keys() -> list[str]:
    """Load keys from GEMINI_KEY_POOL (comma-separated) or fall back to GEMINI_API_KEY."""
    pool_str = os.environ.get("GEMINI_KEY_POOL", "")
    if pool_str:
        keys = [k.strip() for k in pool_str.split(",") if k.strip()]
        if keys:
            return keys
    # Fallback: single key
    single = os.environ.get("GEMINI_API_KEY", "")
    return [single] if single else []


class GeminiKeyPool:
    """Thread-safe rotating Gemini API key pool."""

    def __init__(self, keys: list[str] | None = None):
        self._keys = keys or _load_keys()
        if not self._keys:
            raise RuntimeError("No Gemini API keys configured. Set GEMINI_KEY_POOL in .env")
        # key → (exhausted_at_timestamp, is_quota_exhausted)
        # is_quota_exhausted=True means 24h reset needed; False means transient (1 min)
        self._exhausted: dict[str, tuple[float, bool]] = {}
        self._lock = Lock()
        self._index = 0
        logger.info("Key pool initialised with %d key(s)", len(self._keys))

    def get_key(self) -> str:
        """Return the next available key, skipping exhausted ones."""
        with self._lock:
            now = time.time()
            # Try each key starting from current index
            for i in range(len(self._keys)):
                key = self._keys[(self._index + i) % len(self._keys)]
                if key in self._exhausted:
                    exhausted_at, is_quota = self._exhausted[key]
                    reset_after = _RESET_AFTER_SECS if is_quota else _TRANSIENT_BACKOFF_SECS
                    if now - exhausted_at < reset_after:
                        continue  # Still exhausted
                    else:
                        del self._exhausted[key]  # Reset — try again
                # Advance index for next call (round-robin)
                self._index = (self._index + i + 1) % len(self._keys)
                return key

            # All keys exhausted — return least recently exhausted and log warning
            logger.warning("All %d Gemini keys exhausted — using least recently exhausted", len(self._keys))
            key = min(self._exhausted.items(), key=lambda x: x[1][0])[0]
            return key

    def mark_exhausted(self, key: str, is_quota: bool = True) -> None:
        """Mark a key as exhausted. is_quota=True for 429; False for 503."""
        with self._lock:
            self._exhausted[key] = (time.time(), is_quota)
            available = len(self._keys) - len(self._exhausted)
            logger.warning(
                "Key ...%s marked %s. %d/%d keys still available.",
                key[-6:],
                "quota-exhausted (24h)" if is_quota else "unavailable (1min)",
                max(0, available),
                len(self._keys),
            )

    @property
    def available_count(self) -> int:
        now = time.time()
        with self._lock:
            exhausted = sum(
                1 for exhausted_at, is_quota in self._exhausted.values()
                if now - exhausted_at < (_RESET_AFTER_SECS if is_quota else _TRANSIENT_BACKOFF_SECS)
            )
            return len(self._keys) - exhausted


# Singleton — shared across Flash, Comms, and carousel arbiter
_pool: GeminiKeyPool | None = None


def get_pool() -> GeminiKeyPool:
    global _pool
    if _pool is None:
        _pool = GeminiKeyPool()
    return _pool
