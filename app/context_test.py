import uuid
import asyncio
import aiotask_context as context

from aiohttp import web


async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, {}. Your request id is {}.\n".format(name, context.get("X-Request-ID"))
    return web.Response(text=text)


async def request_id_middleware(app, handler):
    async def middleware_handler(request):
        context.set("X-Request-ID", request.headers.get("X-Request-ID", str(uuid.uuid4())))
        response = await handler(request)
        response.headers["X-Request-ID"] = context.get("X-Request-ID")
        return response
    return middleware_handler

loop = asyncio.get_event_loop()
loop.set_task_factory(context.task_factory)
app = web.Application(middlewares=[request_id_middleware])
app.router.add_route('GET', '/{name}', handle)
web.run_app(app, port=6666)