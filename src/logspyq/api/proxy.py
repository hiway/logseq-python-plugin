from typing import Callable
from logspyq.server.logger import log


class LogseqProxy(object):
    def __init__(self, logseq) -> None:
        self._register_callbacks = {}
        self.logseq = logseq

    def register_callback(self, method: str, **data):
        log.info(f"Registering callback: {method} => {data}")
        self._register_callbacks[method] = data
        return method

    async def register_callbacks_with_logseq(self):
        for method, data in self._register_callbacks.items():
            func = data["func"]
            event_name = data["event_name"]
            data_minus_func = {k: v for k, v in data.items() if k != "func"}
            if func and event_name:
                log.info(f"!!!Registering callback: {method} => {data_minus_func} ({func})")
                self.logseq.on(event_name)(func)
                await self.logseq.emit(method, **data_minus_func)
            else:
                raise Exception(f"Invalid callback: {method} => {data} (func={func}, event_name={event_name})")
