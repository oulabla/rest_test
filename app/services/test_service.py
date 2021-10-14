import aiohttp

class TestService:

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def some_action(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("http://127.0.0.1:8000/text") as response:
                html = await response.text()
        html += f" and api: {self.api_key} "
        return html