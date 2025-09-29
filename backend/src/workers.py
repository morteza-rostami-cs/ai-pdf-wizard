from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Any
import asyncio

# my imports 
from src.dtos import TaskStatus, TaskTypes
from src.models import Task

# process test task
async def process_test_task(task: Task, db: AsyncIOMotorDatabase[Any]) -> None:
  """ just fake processing a task """

  print(f"process task: {task.task_type}🍆")

  # get task.payload - and process task

  # mark task as done
  await task.mark_done()

# process each task based on type

async def process_task(task: Task, db: AsyncIOMotorDatabase[Any]):
  """ process a tas, based on task_type """

  # check for task
  if not task:
    raise Exception("process_task: task object missing.")

  try:

    task_type = task.task_type

    if task_type == TaskTypes.TEST:
      await process_test_task(task=task, db=db)
    else:
      raise ValueError(f"we don't process this type of task {task_type}")

  except Exception as e:
    print("process_task: has failed")
    # set the task to failed
    await task.mark_failed(error_msg=str(e))

# async worker loop

async def task_worker_loop(
    db: AsyncIOMotorDatabase[Any],# instance of mongodb
    interval: int = 5,
): 
  """ main worker loop to fetch and process incomplete tasks """
  print("🍎🍎 start worker loop.")

  while True:
    print("---async worker loop---")
    try:

      # process incomplete tasks
      async for task in Task.find({
        "status": TaskStatus.INCOMPLETE,
      }).sort('created_at'):
        
        # set task to processing -> start worker process
        await task.mark_processing()

        # dispatch task to handler
        asyncio.create_task(process_task(task=task, db=db))

    except Exception as e:
      print(f"task worker loop error: {str(e)}")
      
    
    await asyncio.sleep(delay=interval)