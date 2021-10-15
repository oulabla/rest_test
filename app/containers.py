from dependency_injector import containers, providers
from dependency_injector.ext import aiohttp
from aiohttp import web
from app.api.di_test import di_view

from app.services.test_service import TestService
from app.services.text_searcher import TextSearcher

class ApplicationContainer(containers.DeclarativeContainer):
    
    app = aiohttp.Application(web.Application)

    config = providers.Configuration()

    test_service = providers.Factory(
        TestService,
        api_key=config.test_service.api_key
    )

    text_searcher = providers.Factory(
        TextSearcher,
        test_service=test_service,
    )

    di_view = aiohttp.View(
        di_view, 
        text_searcher=text_searcher
    )