from sqlalchemy import select
from app.db.models.user import User
from app.db.session import get_session

# async def get_or_create_user(message) -> User:
#     """
#     Получает пользователя из БД по telegram_id.
#     Если нет — создаёт нового.
#     """
#     telegram_id = message.from_user.id

#     async with get_session() as session:
#         result = await session.execute(select(User).where(User.telegram_id == telegram_id))
#         user = result.scalar_one_or_none()

#         if user:
#             return user

#         user = User(
#             telegram_id=telegram_id,
#             username=message.from_user.username,
#             first_name=message.from_user.first_name,
#             last_name=message.from_user.last_name,
#             language=message.from_user.language_code
#         )
#         session.add(user)
#         return user


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class UserService:

    @staticmethod
    async def get_or_create_user(message) -> User:
        """
        Получает пользователя из БД по telegram_id.
        Если нет — создаёт нового.
        """ 
        telegram_id = message.from_user.id

        async with get_session() as session:
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalar_one_or_none()

            if user:
                return user

            user = User(
                telegram_id=telegram_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language=message.from_user.language_code
            )
            session.add(user)
            return user


    @staticmethod
    async def get_user_by_telegram_id(
        session: AsyncSession,
        telegram_id: int
    ) -> User | None:
        return await session.scalar(
            select(User).where(User.telegram_id == telegram_id)
        )
    

    @staticmethod
    async def get_user_id_by_telegram_id(session: AsyncSession, telegram_id: int) -> int | None:
        user = await session.scalar(
            select(User).where(User.telegram_id == telegram_id)
        )
        return user.id if user else None  # Вернёт ID из БД или None, если пользователь не найден