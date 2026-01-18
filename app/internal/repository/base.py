from typing import TypeVar, Generic, Type, Optional, List, Union, Any

from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: UUID) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, obj_in: Union[CreateSchemaType, dict]) -> ModelType:
        if isinstance(obj_in, dict):
            obj_in_data = obj_in
        else:
            obj_in_data = obj_in.model_dump()

        db_obj = self.model(**obj_in_data)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(
            self,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, dict[str, Any]]
    ) -> ModelType:
        obj_data = db_obj.__dict__

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: UUID) -> Optional[ModelType]:
        obj = await self.get(id)
        if obj:
            await self.session.delete(obj)
            await self.session.commit()
        return obj

