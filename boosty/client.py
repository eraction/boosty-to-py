import httpx

from urllib.parse import urljoin

from typing import Iterator as Iter

from .iterator import Iterator
from .objects import BlogPost
from .utils import make_sync


class BoostyClient:
    def __init__(self) -> None:
        self._base = 'https://api.boosty.to/v1/'
        self._headers = {
            'User-Agent': 'python Boosty API / v0.1'
        }

    def iter_posts(self, blog: str, limit: int = None) -> Iter[BlogPost]:
        '''Iterate over blog posts

        Args:
            blog (str): blog id/name from https://boosty.to/<name>
            limit (int, optional): limit iteration. Defaults to None.

        Returns:
            Iter[BlogPost]: _description_
        '''
        URL = f'blog/{blog}/post/'

        return Iterator(self, URL, limit=limit, meta=dict(blog=blog))

    async def obtain_posts_since(self, blog: str, date):
        posts = []

        async for post in self.iter_posts(blog):
            post: BlogPost

            if post.created_at > date:
                posts.append(post)
            else:
                break

        return posts[::-1]

    async def _request_async(self, method, path, content=None, params=None, data=None, files=None, headers=None):
        _headers = self._headers.copy()

        if headers:
            if not isinstance(headers, dict):
                raise ValueError(f'Expecting dictionary, got: {type(headers).__name__}')

            _headers.update(headers)

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=urljoin(self._base, path),
                content=content,
                params=params,
                files=files,
                data=data,
                headers=_headers
            )

        response.raise_for_status()

        return response

    def _get(self, path, params=None) -> httpx.Response:
        return make_sync(self._get_async(path, params=params))

    async def _get_async(self, path, params=None) -> httpx.Response:
        return await self._request_async('get', path, params=params)

    def _get_json(self, path, params=None):
        return make_sync(self._get_async_json(path, params=params))

    async def _get_async_json(self, path, params=None):
        result = await self._get_async(path, params=params)

        return result.json()
