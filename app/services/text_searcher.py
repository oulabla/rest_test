
from app.services.test_service import TestService

class TextSearcher:
    def __init__(self, test_service: TestService) -> None:
        self.test_service = test_service

    async def search(self) -> str:
        return await self.test_service.some_action() + " and search"