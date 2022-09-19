import asyncio


def make_sync(future):
    return asyncio.get_event_loop().run_until_complete(future)
