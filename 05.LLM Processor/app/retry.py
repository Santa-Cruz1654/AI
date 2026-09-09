import asyncio
import random

import groq


def is_retryable_error(
    exc: Exception,
) -> bool:

    retryable_errors = (
        groq.APIConnectionError,
        groq.APITimeoutError,
        groq.RateLimitError,
        groq.InternalServerError,
    )

    return isinstance(
        exc,
        retryable_errors,
    )


async def retry_with_backoff(
    operation,
    max_attempts: int,
    base_delay: float,
):

    for attempt in range(
        1,
        max_attempts + 1,
    ):

        try:

            result = await operation()

            return result, attempt

        except Exception as exc:

            if not is_retryable_error(exc):

                raise

            if attempt == max_attempts:

                raise

            delay = (
                base_delay
                * (2 ** (attempt - 1))
                + random.uniform(0, 0.5)
            )

            await asyncio.sleep(delay)

    raise RuntimeError(
        "Unexpected retry state"
    )