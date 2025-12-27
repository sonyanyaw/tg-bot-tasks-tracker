from datetime import date
from sqlalchemy import select
from app.db.session import get_session
from app.db.models.task_status import TaskStatus
from app.utils.enums import TaskStatusEnum


class TaskStatusService:

    @staticmethod
    async def get_or_create(task_id: int, task_date: date) -> TaskStatus:
        async with get_session() as session:
            status = await session.scalar(
                select(TaskStatus)
                .where(TaskStatus.task_id == task_id)
                .where(TaskStatus.task_date == task_date)
            )

            if status:
                return status

            status = TaskStatus(
                task_id=task_id,
                task_date=task_date,
                status=TaskStatusEnum.pending
            )
            session.add(status)
            await session.commit()
            return status
        

    @staticmethod
    async def mark_done(task_id: int, task_date: date):
        async with get_session() as session:
            status = await session.scalar(
                select(TaskStatus)
                .where(TaskStatus.task_id == task_id)
                .where(TaskStatus.task_date == task_date)
            )

            if status:
                status.status = TaskStatusEnum.done
            else:
                session.add(TaskStatus(
                    task_id=task_id,
                    task_date=task_date,
                    status=TaskStatusEnum.done
                ))

            await session.commit()


    @staticmethod
    async def cancel(task_id: int, task_date: date):
        async with get_session() as session:
            status = await session.scalar(
                select(TaskStatus)
                .where(TaskStatus.task_id == task_id)
                .where(TaskStatus.task_date == task_date)
            )

            if status:
                status.status = TaskStatusEnum.canceled
            else:
                session.add(TaskStatus(
                    task_id=task_id,
                    task_date=task_date,
                    status=TaskStatusEnum.canceled
                ))

            await session.commit()

