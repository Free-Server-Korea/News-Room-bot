from sqlalchemy import select
from ..cogs.models import NewsHistory
import logging

logger = logging.getLogger('news_bot')

class NewsRepository:
    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def is_url_sent(self, url: str) -> bool:
        """URL이 이미 전송되었는지 확인"""
        if not self.session_maker:
            return False
        
        async with self.session_maker() as session:
            result = await session.execute(
                select(NewsHistory).where(NewsHistory.url == url)
            )
            return result.scalar_one_or_none() is not None

    async def save_sent_url(self, url: str, message_id: str = None):
        """전송된 URL을 데이터베이스에 저장"""
        if not self.session_maker:
            return
        
        async with self.session_maker() as session:
            news_record = NewsHistory(url=url, message_id=message_id)
            session.add(news_record)
            await session.commit()

    async def get_total_count(self) -> int:
        """전체 뉴스 기록 수 반환"""
        if not self.session_maker:
            return 0
        async with self.session_maker() as session:
            result = await session.execute(select(NewsHistory))
            return len(result.scalars().all())
