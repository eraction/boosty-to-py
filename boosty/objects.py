import pendulum
from pendulum.datetime import DateTime


class BlogPost:
    BASE_URL = 'https://boosty.to'

    @classmethod
    def from_dict(cls, obj_dict: dict, meta: dict = None):
        if not isinstance(obj_dict, dict):
            raise ValueError(f'Expecting dictionary, got: {type(obj_dict).__name__}')

        for key in ('publishTime', 'updatedAt', 'createdAt'):
            if key in obj_dict:
                obj_dict[key] = pendulum.from_timestamp(obj_dict[key])

        instance = cls(obj_dict, meta=meta)

        return instance

    def __init__(self, obj: dict, meta: dict = None) -> None:
        self._obj = obj
        self._meta = meta or {}

    @property
    def background(self) -> bytes:
        for obj in self._obj.get('teaser', []):
            if obj.get('rendition') == 'teaser_auto_background':
                return obj.get('url')

        return None

    @property
    def is_public(self):
        return self._obj.get('hasAccess', False)

    @property
    def level(self):
        if self.is_public:
            return 'PUBLIC'

        return self._obj.get('subscriptionLevel', {}).get('name', 'PUBLIC?')

    @property
    def free(self):
        return self.price == 0

    @property
    def price(self):
        return self._obj.get('price', 0)

    @property
    def title(self):
        return self._obj.get('title', '')

    @property
    def id(self):
        return self._obj.get('id', '')

    @property
    def url(self):
        if not self._meta.get('blog') or not self.id:
            return None

        return '{base}/{blog}/posts/{id}'.format(base=self.BASE_URL, blog=self._meta.get('blog'), id=self.id)

    @property
    def created_at(self) -> DateTime:
        return self._obj.get('createdAt')

    @property
    def updated_at(self) -> DateTime:
        return self._obj.get('updatedAt')

    @property
    def published_at(self) -> DateTime:
        return self._obj.get('publishedAt')
