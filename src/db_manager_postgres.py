import time
from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User, user_table, NonvalidUser, nonvalid_user_table


class DBManagerPostgres:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, email: str, hashed_password: str):
        user = User(email=email, hashed_password=hashed_password, account_created=str(time.time()))
        self.session.add(user)
        await self.session.commit()
        return user.id

    async def get_user_by_email(self, email: str):
        query = select(user_table).where(user_table.c.email == email)
        result = await self.session.execute(query)
        user = result.fetchone()
        await self.session.commit()

        if user:
            user_data = user._mapping  # NOQA
            return User(
                id=user_data['id'],
                email=user_data['email'],
                hashed_password=user_data['hashed_password'],
                account_created=user_data['account_created']
            )

        return None

    async def delete_nonvalid_user_by_uuid(self, user_uuid: str) -> bool:
        async with self.session.begin():
            result = await self.session.execute(
                delete(nonvalid_user_table).where(nonvalid_user_table.c.id == user_uuid)
            )
            await self.session.commit()
            return result.rowcount > 0  # NOQA

    async def get_tmp_user_data(self, uuid: str):
        query = select(nonvalid_user_table).where(nonvalid_user_table.c.id == uuid)
        result = await self.session.execute(query)
        user = result.fetchone()
        await self.session.commit()

        if user:
            user_data = user._mapping  # NOQA
            return user_data['email'], user_data['hashed_password']

        return None

    async def remove_expired_users(self):
        current_timestamp = int(datetime.now().timestamp())
        result = await self.session.execute(
            select(NonvalidUser).where(NonvalidUser.token_expires_at < current_timestamp)
        )
        expired_users = result.scalars().all()

        for user in expired_users:
            await self.session.delete(user)

        await self.session.commit()

    async def create_tmp_user(self, email: str, hashed_password: str, validation_start_timestamp: int, token: int):
        await self.remove_expired_users()
        user = NonvalidUser(email=email, hashed_password=hashed_password,
                            token_expires_at=validation_start_timestamp,
                            token_hashed_value=str(token))
        self.session.add(user)
        await self.session.commit()
        return user.id
