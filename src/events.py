import asyncio
import json
from typing import Callable, Any , Coroutine, Dict

class EventManager:
  """
  basic in-memory pub/sub for sse connections.
  """

  def __init__(self) -> None:
    # subscribers
    self._subs: Dict[str, list[asyncio.Queue[Any]]] = {}
    # a lock -> stop race condition between coroutines -> as they try to access _subs
    self._lock = asyncio.Lock()

  async def subscribe(self, user_id: str) -> asyncio.Queue[Any]:
    """ create and register a queue for this user_id, return the queue """

    q: asyncio.Queue[Any] = asyncio.Queue()

    async with self._lock:
      if user_id not in self._subs:
        self._subs[user_id] = []
      
      # push queue into user_id.list
      self._subs[user_id].append(q)

    # return the queue
    return q

  # dict -> user_id -> [queue, queue]
  async def unsubscribe(self, user_id: str, q: asyncio.Queue[Any]) -> None:
    """ for this user, remove it's queue from the list """
    async with self._lock:
      subs: list[asyncio.Queue[Any]] | None = self._subs.get(user_id) 

      if not subs: # no such subscriber -> user_id
        return # no Queue

      if q in subs:
        subs.remove(q) # remove Queue from list
      
      # empty the list
      if not subs:
        self._subs.pop(user_id, None)

  async def publish(self, user_id: str, event: str, data: Any) -> None:
    """
    publish an event to all subscribers (Queues), under a user_id
    """

    # get subscribers
    async with self._lock: # we don't want to make other coroutines wait for too longs ->hence: copying
      subs = list(self._subs.get(user_id, [])) # copy the list of subs
    
    if not subs:
      return
    
    # create a payload
    payload = dict(event=event, data=data)
    text = json.dumps(payload)

    # loop through all subscribers/queues -> under current user_id
    for q in subs:
      try:
        # put_nowait -> if queue is full -> drop this event -> do not block publisher
        q.put_nowait(text)
      except asyncio.QueueFull: # queue can be full
        pass

  async def publish_all(self, event: str, data: Any) -> None:
    """ publish to all connected users/subscribers """
    async with self._lock:
      # grab all queues 
      all_queues = [q for subs in self._subs.values() for q in subs]
    
    payload = dict(event=event, data=data)
    text = json.dumps(payload)

    for q in all_queues:
      try:
        q.put_nowait(text)
      except asyncio.QueueFull:
        pass

# singleton 
event_manager = EventManager()