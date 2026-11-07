"""Fan-out of server events to every connected browser (Server-Sent Events)."""
import queue
import threading
from typing import Dict, List


class EventHub:
    def __init__(self, backlog: int = 400):
        self._clients: List[queue.Queue] = []
        self._lock = threading.Lock()
        self._backlog: List[Dict] = []          # recent play-by-play so a page opened mid-game can catch up
        self._backlog_size = backlog

    def subscribe(self) -> queue.Queue:
        client = queue.Queue(maxsize=5000)
        with self._lock:
            self._clients.append(client)
            backlog = list(self._backlog)
        for event in backlog:
            client.put_nowait(event)
        return client

    def unsubscribe(self, client: queue.Queue):
        with self._lock:
            if client in self._clients:
                self._clients.remove(client)

    def publish(self, event: Dict, keep: bool = False):
        with self._lock:
            clients = list(self._clients)
            if keep:
                self._backlog.append(event)
                del self._backlog[:-self._backlog_size]
        for client in clients:
            try:
                client.put_nowait(event)
            except queue.Full:
                pass

    def clear_backlog(self):
        with self._lock:
            self._backlog.clear()
