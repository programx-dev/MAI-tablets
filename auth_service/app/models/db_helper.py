from asyncio import current_task
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    async_sessionmaker, 
    async_scoped_session, 
    AsyncSession,
)
from app.core.config import settings

import warnings
warnings.warn('Deprecated')

class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False) -> None:
        self.engine = create_async_engine(url=url, echo=echo)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        
    def get_scope_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session
    
    async def session_dependency(self) -> AsyncSession:
        async with self.get_scope_session() as session: 
            yield session
            await session.remove() 
        

db_helper = DatabaseHelper(
    url=settings.db_url,
    echo=settings.db_echo,
)
