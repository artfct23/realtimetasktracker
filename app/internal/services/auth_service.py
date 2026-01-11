from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.internal.repository.user import UserRepository
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from app.services.ses import send_email  

class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register_user(self, user_in: UserCreate):
        # 1. Проверяем, занят ли email
        if await self.repo.get_by_email(user_in.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        # 2. Хешируем пароль и готовим данные
        user_data = {
            "email": user_in.email,
            "hashed_password": get_password_hash(user_in.password),
            "full_name": user_in.full_name,
            "is_active": True
        }

        # 3. Сохраняем через репозиторий
        new_user = await self.repo.create(user_data)

        # 4. Отправляем письмо (бизнес-действие)
        await send_email(new_user.email, "Welcome", "Добро пожаловать в Task Tracker!")

        return new_user
