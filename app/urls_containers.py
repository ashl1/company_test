from abc import abstractmethod
from typing import NamedTuple, Iterable


class BaseUrlsContainerServices:
    @abstractmethod
    async def is_urls_exist(self, urls: Iterable[str]) -> dict[str, bool]:
        ...

    @abstractmethod
    async def add_urls(self, urls: Iterable[str]) -> None:
        ...

    @abstractmethod
    async def add_crawl_tasks(self, urls: Iterable[str]) -> None:
        ...

    @abstractmethod
    async def mark_url_as_not_parsing(self, url: str) -> None:
        ...

    @abstractmethod
    async def pop_free_tasks_url(self, limit=1) -> tuple[str]:
        ...


class HashInMemoryUrlsContainerServices(BaseUrlsContainerServices):
    class StorageValue(NamedTuple):
        processed: bool
        might_contains_urls: bool

    def __init__(self):
        self.storage: dict[str, HashInMemoryUrlsContainerServices.StorageValue] = dict()
        self.tasks: set[str] = set()

    async def add_urls(self, urls: Iterable[str]) -> None:
        self.storage.update({
            url: HashInMemoryUrlsContainerServices.StorageValue(False, True)
            for url in urls
        })

    async def is_urls_exist(self, urls: Iterable[str]) -> dict[str, bool]:
        return {
            url: (url in self.storage) or (url in self.tasks)
            for url in urls
        }

    async def add_crawl_tasks(self, urls: Iterable[str]) -> None:
        self.tasks.update(urls)

    async def mark_url_as_not_parsing(self, url: str) -> None:
        raise NotImplementedError('mark_url_as_not_parsing')

    async def pop_free_tasks_url(self, limit=1) -> tuple[str]:
        res = []
        try:
            for _ in range(limit):
                res.append(self.tasks.pop())
        except KeyError:
            ...
        return tuple(res)
