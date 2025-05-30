import asyncio
import time

class AsyncRetryCaller:
    def __init__(self, max_attempts=3, wait_seconds=1, single_try_timeout=2, log=None):
        self.max_attempts = max_attempts
        self.wait_seconds = wait_seconds
        self.single_try_timeout = single_try_timeout
        self.attempt_count = None
        self.success_time = None
        self.log = log

    async def _internal_call(self, func, *args, **kwargs):
        for attempt in range(self.max_attempts):
            try:
                if attempt > 0:  # Print retry message only after the first attempt
                    msg = f"Attempt {attempt + 1}: Retrying API call..."
                    if self.log:
                        self.log.warning(msg)
                    else:
                        print(msg)
                start_time = time.time()
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    self.single_try_timeout
                )
                return result, attempt + 1, time.time() - start_time
            except asyncio.exceptions.TimeoutError as e:
                if self.log:
                    self.log.warning(f"Attempt {attempt + 1} failed in {time.time() - start_time:.2f} seconds")
                if attempt + 1 < self.max_attempts:
                    await asyncio.sleep(self.wait_seconds)
                else:
                    raise Exception("Max attempts reached, giving up") from e
            except Exception as e:
                if self.log:
                    self.log.warning(f"Attempt {attempt + 1} failed in {time.time() - start_time:.2f} seconds")
                    self.log.warning("Unexpected error:")
                    self.log.exception(e)
                if attempt + 1 < self.max_attempts:
                    await asyncio.sleep(self.wait_seconds)
                else:
                    if self.log:
                        self.log.error("Max attempts reached, raising an exception")
                    raise e
        raise Exception("AsyncRetryCaller internal error")  # We should never end up here

    async def __call__(self, func, *args, **kwargs):
        result, self.attempt_count, self.success_time = await self._internal_call(
            func, *args, **kwargs
        )
        return result
