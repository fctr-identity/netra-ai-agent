"""Run one Netra directory sync; suitable for cron or Task Scheduler."""
import asyncio
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.core.entra.sync.engine import SyncOrchestrator
from src.core.storage.operations import DatabaseOperations


async def main():
    db = DatabaseOperations()
    try:
        result = await SyncOrchestrator(db=db).run_sync()
        print(json.dumps(result, indent=2))
        return 0 if result['status'] == 'completed' else 2
    except Exception as exc:
        print(f'Sync failed: {exc}', file=sys.stderr)
        return 1
    finally:
        await db.close()


if __name__ == '__main__':
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        sys.exit(130)
