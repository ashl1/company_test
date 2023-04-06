import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from crawler import Crawler
from urls_containers import HashInMemoryUrlsContainerServices

app = FastAPI()


class StartCrawlingData(BaseModel):
    url: str


crawler = Crawler(HashInMemoryUrlsContainerServices())


@app.post(
    '/start_crawling',
    summary='Command to start crawling',
)
async def start_crawling(item: StartCrawlingData):
    if not crawler.is_available():
        raise HTTPException(status_code=400, detail='Crawler has been already started')
    asyncio.create_task(crawler.start_crawling_from(item.url))


@app.post(
    '/stop_crawling',
    summary='Command to stop crawling'
)
async def stop_crawling():
    await crawler.stop()
    return ''


@app.get(
    '/status',
    summary='Get current crawling status'
)
async def get_crawling_status():
    if crawler.is_available():
        raise HTTPException(status_code=400, detail='There is no active crawling process')
    return await crawler.get_status()
