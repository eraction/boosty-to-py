from .utils import make_sync
from .objects import BlogPost


class Iterator:
    default_batch_size = 50

    def __init__(self, client, path: str, params=None, offset=None, limit=50, meta=None) -> None:
        '''_summary_

        Args:
            client (BoostyAPI): _description_
            path (str): _description_
            params (_type_, optional): _description_. Defaults to None.
            offset (str, optional): offset from saved iteration. Defaults to None.
            limit (int, optional): Maximum items to fetch from collection. Defaults to 50.
        '''

        self._client = client
        self._path = path
        self._params = params or {}
        self._cursor = offset
        self._limit = limit
        self._meta = meta or {}

        self._count = 0
        self._items = []
        self._items_cursor = 0

    @property
    def offset(self):
        return self._cursor

    def __next__(self):
        return make_sync(self.__anext__())

    def _parse_response(self, json_response):
        if not isinstance(json_response.get('data'), list):
            raise ValueError(f'{self._path} is not a collection')

        self._items = json_response.get('data', [])
        self._cursor = None

        extra = json_response.get('extra', {})

        if not extra.get('isLast'):
            self._cursor = extra.get('offset')

    async def __anext__(self) -> BlogPost:
        if self._limit and self._count == self._limit:
            # we raised user-defined limit
            raise StopAsyncIteration()

        if not self._items and (self._count == 0 or self._cursor):
            self._parse_response(await self._client._get_async_json(
                self._path,
                params=self._build_params()
            ))

        if not self._items:
            raise StopAsyncIteration()

        item = self._items.pop(0)
        self._count += 1
        self._items_cursor += 1

        return BlogPost.from_dict(item, meta=self._meta)

    def _build_params(self):
        params = self._params.copy()

        params['limit'] = self.default_batch_size

        if self._cursor:
            params['offset'] = self._cursor

        if self._limit:
            params['limit'] = min(self.default_batch_size, self._limit - self._count)

        return params

    def __iter__(self):
        return self

    def __aiter__(self):
        return self
