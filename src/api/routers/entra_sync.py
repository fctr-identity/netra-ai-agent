"""Manual sync and status for the shared Entra snapshot engine."""
import asyncio
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from src.config.settings import settings
from src.core.security.dependencies import get_current_user
from src.core.storage.models import SyncHistory, SyncStatus
from src.core.storage.operations import DatabaseOperations
from src.core.entra.sync.engine import SyncOrchestrator, now, sync_lock
from src.core.entra.sync.models import DirectorySnapshot

router = APIRouter(prefix='/sync', tags=['sync'])
_start_lock = asyncio.Lock()
active_syncs = {}


async def _run(sync_id, event):
    db = DatabaseOperations()
    try:
        return await SyncOrchestrator(db=db, sync_id=sync_id, cancellation_flag=event).run_sync()
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        async with db.get_session() as session:
            await db.update_sync_history(session, sync_id, settings.tenant_id,
                {'status': SyncStatus.FAILED, 'end_time': now(), 'success': False, 'error_details': str(exc)[:1000]})
    finally:
        active_syncs.pop(sync_id, None)


@router.post('/start')
async def start_sync(current_user: Any = Depends(get_current_user)):
    if not all((settings.ENTRA_TENANT_ID, settings.ENTRA_CLIENT_ID, settings.ENTRA_CLIENT_SECRET)):
        raise HTTPException(400, 'Configure Entra tenant, client ID and client secret before syncing.')
    async with _start_lock:
        db = DatabaseOperations()
        await db.init_db()
        async with db.get_session() as session:
            active = await db.get_active_sync(session, settings.tenant_id)
            if active_syncs:
                return {'status': 'already_running', 'sync_id': next(iter(active_syncs)), 'message': 'Sync already running'}
            try:
                with sync_lock():
                    # An abandoned history row must not block a new local run.
                    if active:
                        await db.update_sync_history(session, active.id, settings.tenant_id,
                            {'status': SyncStatus.FAILED, 'end_time': now(), 'success': False,
                             'error_details': 'Previous process stopped before sync completed'})
            except RuntimeError:
                return {'status': 'already_running', 'sync_id': active.id if active else None, 'message': 'A CLI or server sync is running'}
            row = await db.create_sync_history(session, settings.tenant_id)
            sync_id = row.id
        event = asyncio.Event()
        task = asyncio.create_task(_run(sync_id, event), name=f'netra-sync-{sync_id}')
        active_syncs[sync_id] = (task, event)
        return {'status': 'started', 'sync_id': sync_id, 'progress': 0, 'message': 'Directory sync started'}


@router.get('/status')
async def get_sync_status(current_user: Any = Depends(get_current_user)):
    db = DatabaseOperations()
    async with db.get_session() as session:
        latest = await db.get_latest_sync(session, settings.tenant_id)
        if latest and latest.status in {SyncStatus.IDLE, SyncStatus.RUNNING} and latest.id not in active_syncs:
            try:
                with sync_lock():
                    # No process owns the run: make the UI's start action available.
                    await db.update_sync_history(session, latest.id, settings.tenant_id,
                        {'status': SyncStatus.FAILED, 'end_time': now(), 'success': False,
                         'error_details': 'Previous process stopped before sync completed; prior snapshots retained'})
                    latest = await db.get_latest_sync(session, settings.tenant_id)
            except RuntimeError:
                pass  # A CLI or another local server process still owns the OS lock.
        completed = await db.get_last_completed_sync(session, settings.tenant_id)
        snapshots = (await session.execute(select(DirectorySnapshot).where(DirectorySnapshot.tenant_id == settings.tenant_id))).scalars().all()
        response = {'status': latest.status.value if latest else 'never_synced',
                    'message': 'No sync yet' if not latest else latest.error_details or 'Directory sync ' + latest.status.value,
                    'sync_id': latest.id if latest else None, 'progress': latest.progress_percentage if latest else 0,
                    'start_time': latest.start_time if latest else None, 'end_time': latest.end_time if latest else None,
                    'last_successful_sync_time': completed.end_time if completed else None,
                    'error_details': latest.error_details if latest else None,
                    'entity_counts': {snapshot.resource: snapshot.record_count for snapshot in snapshots},
                    'resources': [{'resource': item.resource, 'status': item.status, 'last_successful_at': item.last_successful_at,
                                   'last_attempt_at': item.last_attempt_at, 'error': item.error, 'notes': item.notes} for item in snapshots]}
        response['entity_counts']['applications'] = response['entity_counts'].get('service_principals')
        response['entity_counts']['policies'] = response['entity_counts'].get('conditional_access_policies')
        return response


@router.post('/cancel')
async def cancel_sync(current_user: Any = Depends(get_current_user)):
    pending = list(active_syncs.items())
    if not pending:
        return {'status': 'not_running', 'message': 'No UI sync is running. Stop a CLI sync in its terminal.'}
    for sync_id, (task, event) in pending:
        event.set()
        task.cancel()
    await asyncio.gather(*(task for _, (task, _) in pending), return_exceptions=True)
    db = DatabaseOperations()
    async with db.get_session() as session:
        for sync_id, _ in pending:
            await db.update_sync_history(session, sync_id, settings.tenant_id,
                {'status': SyncStatus.CANCELED, 'end_time': now(), 'success': False, 'error_details': 'Sync cancelled'})
            active_syncs.pop(sync_id, None)
    return {'status': 'canceled', 'message': 'Local sync stopped; unpublished snapshots retained'}


@router.get('/history')
async def sync_history(current_user: Any = Depends(get_current_user)):
    db = DatabaseOperations()
    async with db.get_session() as session:
        rows = await db.get_sync_history(session, settings.tenant_id)
        return [{'id': row.id, 'status': row.status.value, 'start_time': row.start_time,
                 'end_time': row.end_time, 'error_details': row.error_details} for row in rows]
