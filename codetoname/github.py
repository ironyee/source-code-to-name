from aiohttp import BasicAuth, ClientSession, Timeout
import asyncio


class Github:
    _BASE_URL = 'https://api.github.com'

    def __init__(self, username, password, timeout=10):
        self._loop = asyncio.get_event_loop()
        self._session = ClientSession(loop=self._loop, auth=BasicAuth(username, password))
        self._timeout = timeout

    def close(self):
        self._session.close()

    async def fetch(self, url, params):
        with Timeout(self._timeout):
            async with self._session.get('{}{}'.format(self._BASE_URL, url), params=params) as response:
                return await response.json()

    async def search_repositories(self, language, pushed, sort, order):
        q = 'language:{}'.format(language)
        if pushed:
            q = '{} pushed:>={}'.format(q, pushed)

        params = {'q': q, 'sort': sort, 'order': order}
        return await self.fetch('/search/repositories', params=params)
