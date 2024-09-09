from sqlalchemy.ext.asyncio import AsyncSession


class DBManager:
    def __init__(self, session: AsyncSession):
        self.session = session