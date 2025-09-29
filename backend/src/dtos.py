from enum import Enum
from typing import TypeAlias, Any

# tasks types
class TaskTypes(Enum):
  """ different types of tasks """
  TEST = 'test'

class TaskStatus(Enum):
  INCOMPLETE = 'incomplete'
  PROCESSING = 'processing'# worker is processing task
  DONE = 'done'
  FAILED = 'failed'

Dictor: TypeAlias = dict[str, Any]