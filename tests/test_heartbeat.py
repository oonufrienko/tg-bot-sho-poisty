"""heartbeat_loop: свіжий unix-час у файлі — сигнал, що event loop живий."""

import asyncio
import time

from bot.main import heartbeat_loop


async def test_heartbeat_writes_fresh_timestamp(tmp_path):
    path = tmp_path / "heartbeat"
    task = asyncio.create_task(heartbeat_loop(path, interval=3600))
    await asyncio.sleep(0.05)
    task.cancel()
    assert abs(int(path.read_text()) - time.time()) < 5


async def test_heartbeat_rewrites_on_each_tick(tmp_path):
    path = tmp_path / "heartbeat"
    task = asyncio.create_task(heartbeat_loop(path, interval=0.01))
    await asyncio.sleep(0.03)
    first_mtime = path.stat().st_mtime_ns
    await asyncio.sleep(0.05)
    task.cancel()
    assert path.stat().st_mtime_ns > first_mtime
