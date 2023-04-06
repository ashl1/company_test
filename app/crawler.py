import asyncio
import re
import sys
from enum import Enum
from typing import Optional, Type
from urllib.parse import urljoin

import httpx
from httpx import AsyncClient, Response, AsyncHTTPTransport, Limits
from mimeparse import parse_mime_type

from urls_containers import BaseUrlsContainerServices


ALLOWED_MIME_TYPES_TO_PARSE = frozenset(('text/html',))
MAX_CONTENT_LENGTH_BYTES = 10 * 1024 * 1024
MAX_CONNECTIONS = 100


class NotParsingMimeType(Exception):
    ...


NOT_ACTIVE_ANYMORE = object()


class StatusEnum(Enum):
    FREE = 'free'
    ACTIVE = 'active'
    CLOSING = 'closing'


def check_active(func):
    def wrapper(crawler: 'Crawler', *args, **kwargs):
        if crawler._status != StatusEnum.ACTIVE:
            return NOT_ACTIVE_ANYMORE
        return func(crawler, *args, **kwargs)
    return wrapper


class Crawler:
    def __init__(self, urls_container_service: BaseUrlsContainerServices):
        self._urls_container = urls_container_service
        self._status = StatusEnum.FREE
        # t = AsyncHTTPTransport()
        self._client = AsyncClient(
            limits=Limits(
                max_connections=MAX_CONNECTIONS,
                max_keepalive_connections=MAX_CONNECTIONS,
            ),
        )
        self._active_tasks = set()

    def is_available(self) -> bool:
        return self._status == StatusEnum.FREE

    async def stop(self):
        self._status = StatusEnum.CLOSING
        if self._active_tasks:
            await asyncio.wait(self._active_tasks)
        self._status = StatusEnum.FREE

    @check_active
    async def _download_page(self, url: str) -> str | Exception | type(NOT_ACTIVE_ANYMORE):
        async with self._client.stream('GET', url) as resp:
            resp: Response
            main_mime, second_mime, _ = parse_mime_type(resp.headers['Content-Type'])
            mime_type = f'{main_mime}/{second_mime}'
            if mime_type not in ALLOWED_MIME_TYPES_TO_PARSE:
                return NotParsingMimeType(mime_type)
            res_arr = []
            async for piece in resp.aiter_text():
                res_arr.append(piece)
            return ''.join(res_arr)

    @check_active
    async def _get_urls_from_page(self, url: str, page_data: str) -> tuple[str] | type(NOT_ACTIVE_ANYMORE):
        # <a href=""
        # <a href=''
        # a_href_url_pattern = '<a\s+href\s*=\s*(\'.*?\')|("(.*?)")'
        a_href_url_pattern = '<a\s+href\s*=\s*(".*?")|(\'.*?\')'
        matches = re.findall(a_href_url_pattern, page_data, re.IGNORECASE)
        urls = [
            urljoin(
                url,
                found_url[0][1:-1]
                or found_url[1][1:-1],
            )
            for found_url in matches
        ]
        return urls

    @check_active
    async def _crawl_page(self, url: str) -> type(NOT_ACTIVE_ANYMORE) | None:
        page_text = await self._download_page(url)
        if page_text is NOT_ACTIVE_ANYMORE:
            return NOT_ACTIVE_ANYMORE
        if type(page_text) is not str:
            await self._urls_container.mark_url_as_not_parsing(url)

        urls_found = await self._get_urls_from_page(url, page_text)
        if urls_found is NOT_ACTIVE_ANYMORE:
            return NOT_ACTIVE_ANYMORE

        # TODO: data race possible
        not_existed_urls = [
            url
            for url, existance in (await self._urls_container.is_urls_exist(urls_found)).items()
            if not existance
        ]
        await self._urls_container.add_urls(not_existed_urls)
        await self._urls_container.add_crawl_tasks(not_existed_urls)

    async def start_crawling_from(self, url: str) -> None:
        if self._status != StatusEnum.FREE:
            return
        self._status = StatusEnum.ACTIVE
        await self._urls_container.add_urls([url])
        await self._urls_container.add_crawl_tasks([url])

        try:
            while self._status == StatusEnum.ACTIVE:
                # TODO: Should optimize to always load all tcp connections
                #       by using self._active_tasks
                tasks_url = await self._urls_container.pop_free_tasks_url(MAX_CONNECTIONS)
                if len(tasks_url) == 0:
                    print('There are no tasks left')
                    await self.stop()
                    return
                results = await asyncio.gather(
                    *(
                        self._crawl_page(task_url)
                        for task_url in tasks_url
                    ),
                    return_exceptions=True,
                )

                await self._urls_container.add_crawl_tasks((
                    task_url
                    for task_url, result in zip(tasks_url, results)
                    if (
                        result is NOT_ACTIVE_ANYMORE
                        or isinstance(result, BaseException)
                    )
                ))
        except Exception:
            # error boundary
            await self.stop()

    async def get_status(self):
        return {
            'urls': tuple(self._urls_container.storage.keys()),
            'tasks': tuple(self._urls_container.tasks),
        }