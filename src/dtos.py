from enum import Enum
from typing import TypeAlias, Any

# tasks types
class TaskTypes(Enum):
  """ different types of tasks """
  PROCESSING = 'processing' # pdf text extraction
  EMBEDDING = 'embedding' # vectorize & store in chroma db


class TaskStatus(Enum):
  INCOMPLETE = 'incomplete'
  PROCESSING = 'processing'# worker is processing task
  DONE = 'done'
  FAILED = 'failed'

Dictor: TypeAlias = dict[str, Any]

class UploadStatus(Enum):
  UPLOADING = 'uploading'
  DONE = 'done'
  FAILED = 'failed'

class PDFStatus(str, Enum):
  UPLOADED = 'uploaded'
  PROCESSING = 'processing' # pdf text extraction
  NEED_OCR = 'need_ocr' # Optical Character Recognition
  EMBEDDING = 'embedding' # vector db
  READY = 'ready'
  FAILED = 'failed'

class UploadEvents(str, Enum):
  UPLOAD_PROGRESS = 'upload_progress'
  UPLOAD_DONE = 'upload_done'
  UPLOAD_FAILED = 'upload_failed'

class PdfEvents(str, Enum):
  PDF_STATUS_UPDATE = 'pdf_status_update'