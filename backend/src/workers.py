from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Any
import asyncio
from bson import ObjectId

# my imports 
from src.dtos import TaskStatus, TaskTypes, PDFStatus
from src.models import Task, PDF, User
from src.services import extract_text_service, fire_task

# process test task
async def process_text_task(task: Task, db: AsyncIOMotorDatabase[Any]) -> None:
  """ task handler: extract text + html from PDF stored in GridFS """

  # data
  pdf_id = task.payload['pdf_id']
  user_id = task.payload["user_id"]

  # find PDF 
  pdf_doc = await PDF.get(document_id=ObjectId(pdf_id))

  if not pdf_doc:
    raise ValueError("PDF not found")

  try:

    # find User
    user_doc = await User.get(document_id=ObjectId(user_id))

    if not user_doc:
      raise ValueError("User not found")

    # call service
    await extract_text_service(
      db=db,
      pdf_doc=pdf_doc,
      user_doc=user_doc,
    )

    # extraction success

    # update status
    await task.mark_done()

    # enqueue a embedding task
    await fire_task(
      task_type=TaskTypes.EMBEDDING,
      payload=dict(pdf_id= pdf_id, user_id=user_id),
    )
  
  except Exception as e:
    # text extraction process has failed
    print(f"text extraction failed: {str(e)}")

    # set task & PDF to status failed
    await task.mark_failed(error_msg=str(e))

    # PDF status
    await pdf_doc.set_status(new_status=PDFStatus.FAILED)


# process each task based on type

async def process_task(task: Task, db: AsyncIOMotorDatabase[Any]):
  """ process a tas, based on task_type """

  # check for task
  if not task:
    raise Exception("process_task: task object missing.")

  try:

    task_type = task.task_type

    if task_type == TaskTypes.PROCESSING:
      await process_text_task(task=task, db=db)
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