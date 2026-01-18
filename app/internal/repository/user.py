from sqlalchemy import select
from app.internal.repository.base import BaseRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin

class UserRepository(BaseRepository[User, UserCreate, UserCreate]):
    def __init__(self, db):
        super().__init__(User, db)

    async def get_by_email(self, email: str):
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
