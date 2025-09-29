
# my imports 
from src.dtos import TaskTypes, Dictor
from src.models import Task

# fire tasks 
async def fire_task(
    task_type: TaskTypes,
    payload: Dictor,
) -> Task:
  """ 
  store a task in mongodb
  args: task_type and payload data 
  """

  task = Task(
    task_type= task_type,
    payload=payload
  )

  await task.insert()

  return task