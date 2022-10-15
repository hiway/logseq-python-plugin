import pytest
from logspyq.api.proxy import LogseqProxy


async def test_api_proxy():
    proxy = LogseqProxy(None)
    
    proxy.register_callback("test_method", "test_event")
    assert proxy._register_callbacks["test_method"] == "test_event"
