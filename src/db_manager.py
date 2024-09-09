from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.models import User, user_table
import datetime
from sqlalchemy import select, insert, exists


class DBManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, email: str, hashed_password: str):
        try:
            user = User(email=email, hashed_password=hashed_password, account_created=str(datetime.datetime.utcnow()))
            self.session.add(user)
            await self.session.commit()
            return user.id
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def get_user_id(self, email: str):
        query = select(user_table.c.id).where(user_table.c.email == email)
        result = await self.session.execute(query)
        user = result.fetchone()
        await self.session.commit()
        return user