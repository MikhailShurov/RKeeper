import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User, user_table


class DBManager:
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
