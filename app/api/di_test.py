from aiohttp import web

from app.services.text_searcher import TextSearcher

async def di_view(request: web.Request, text_searcher: TextSearcher) -> web.Response:
    query = request.query.get('query', 'Dependency Injector')
    limit = int(request.query.get('limit', 10))

    gifs = await text_searcher.search()

    return web.json_response(
        {
            'query': query,
            'limit': limit,
            'gifs': gifs,
        },
    )