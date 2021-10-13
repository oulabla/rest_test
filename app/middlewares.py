from aiohttp import web

@web.middleware
async def api_underscore_body(request: web.Request, handler):
    is_api = True if request.url.path.startswith('/api') else False
    # if is_api:
        # content = request.content()
        # request.clone()
    
    resp = await handler(request)
    return resp


@web.middleware
async def api_exception_json(request: web.Request, handler):
    is_api = True if request.url.path.startswith('/api') else False

    try:
        resp = await handler(request)
        return resp
    except web.HTTPException as e:
        if not is_api: 
            raise e
        return  web.json_response({
            "success": False,
            "error": str(e),
            "code": e.status
        }, status=e.status)
    except Exception as e:
        if not is_api: 
            raise e
        return  web.json_response({
            "success": False,
            "error": str(e),
            "code": web.HTTPInternalServerError
        }, status=web.HTTPInternalServerError)

    