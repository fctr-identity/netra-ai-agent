from tests import CHECKS
import asyncio
import unittest
import logging
from src.api.shutdown import stop_services

class ShutdownTests(unittest.IsolatedAsyncioTestCase):
    async def test_cancelled_service_finishes_cleanup(self):
            closed = asyncio.Event()

            async def service():
                try:
                    await asyncio.Event().wait()
                finally:
                    await asyncio.sleep(0)
                    closed.set()

            task = asyncio.create_task(service())
            await asyncio.sleep(0)
            await stop_services({'socket': task}, {})
            self.assertTrue(closed.is_set())
            self.assertTrue(task.cancelled())

    async def test_slow_cleanup_is_bounded_and_other_services_close(self):
            closed = asyncio.Event()

            async def slow():
                await asyncio.Event().wait()

            async def fast():
                closed.set()

            with self.assertLogs('src.api.shutdown', logging.WARNING) as logs:
                await stop_services({}, {'slow': slow, 'fast': fast}, timeout=0.01)
            self.assertTrue(closed.is_set())
            self.assertIn('slow exceeded', logs.output[0])
            await asyncio.sleep(0)

    async def test_cleanup_failure_does_not_skip_other_services(self):
            closed = asyncio.Event()

            async def fail():
                raise RuntimeError('private provider message')

            async def fast():
                closed.set()

            with self.assertLogs('src.api.shutdown', logging.WARNING) as logs:
                await stop_services({}, {'broken': fail, 'fast': fast})
            self.assertTrue(closed.is_set())
            self.assertIn('RuntimeError', logs.output[0])
            self.assertNotIn('private provider message', logs.output[0])
