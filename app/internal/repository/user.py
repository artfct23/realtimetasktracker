from sqlalchemy import select
from app.internal.repository.base import BaseRepository
from app.models.domain import User

class UserRepository(BaseRepository[User]):
    def __init__(self, db):
        # Говорим Базовому: "Я работаю с моделью User"
        super().__init__(User, db)

    async def get_by_email(self, email: str):
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
