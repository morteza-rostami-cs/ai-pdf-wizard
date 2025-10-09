from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel, SimpleChatModel
from langchain_core.language_models import LanguageModelInput
from langchain_ollama import OllamaLLM, ChatOllama
from langchain.globals import set_verbose, set_debug
from langchain_core.messages import BaseMessage
import os
import uuid
from langchain_core.runnables.base import RunnableSequence, RunnableParallel, RunnableLambda

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables.branch import RunnableBranch

from langchain_community.docstore.document import Document as DOC

# file messages storage
from langchain_community.chat_message_histories.file import FileChatMessageHistory

from langchain_core.prompt_values import ChatPromptValue
#from langchain_core.documents import Document
from langchain.schema import Document

# embedding
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import sys
from typing import Any
#hash doc content
import hashlib

# my imports
from src.config import settings
from src.schemas import PageMetadata

# set_debug(value=True)
set_verbose(value=True)

# Disable proxies
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("ALL_PROXY", None)

# (optional, lowercase too, since some systems use them)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
os.environ.pop("all_proxy", None)

# turns off the stupid proxy
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

# path to store chroma db data
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(path=os.path.join(current_dir, os.pardir))
chroma_path = os.path.join(root_dir, settings.CHROMA_PERSIST)

#print(chroma_path)
# D:\workspace\production\ai-pdf-wizard\chroma_db

llm = ChatOllama(
  model=settings.LLM_MODEL,
  base_url=settings.LLM_URL,
  # stream=True,
  temperature=0.8,
  # client_options={"proxies": None} 
)

# embed model
embedding_function = OllamaEmbeddings(
  base_url=settings.LLM_URL,
  model=settings.EMBED_MODEL,
  temperature=0.6,
  # client_options={"proxies": None} 
)

# string parser
parser = StrOutputParser()

def chunk_pdf_for_embed(
    pages_data: list[dict[str, Any]], # {text, metadata}
    chunk_size: int = 1000,
    chunk_overlap: int = 200, # to not lose context
) -> list[Document]:
  """
  convert PDF page data into chunked langchain Document objects -> ready for embedding
  args:
    page_data: list of dicts -> each: {text, metadata}
  
  """

  # convert dict -> Document
  documents = [
    Document(page_content=page['text'], metadata=page['metadata'] )
    for page in pages_data
    if page.get("text") # skip empty page
  ]

  # split chunk
  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
    #separators=["\n\n", "\n", ".", "!", "?", " ", ""]
  )

  chunks = text_splitter.split_documents(documents=documents)

  return chunks

#embedding_function.aembed_documents

def create_chunk_id(
  pdf_id: str, 
  page_number: int,
  chunk_index: int, 
  chunk_text: str,
) -> str:
  """ create deterministic unique ID for each chunk """
  text_hash = hashlib.md5(chunk_text.encode("utf-8")).hexdigest()[:8]
  return f"{pdf_id}_{page_number}_{chunk_index}_{text_hash}"

# embedding function
async def create_embedding(
  chunks: list[Document],
  embed_function: OllamaEmbeddings = embedding_function,
) -> dict[str, list[Any]]:
  """
  takes langchain Documents, embeds them using Ollama, -> ready to store stuff in Chroma db

  returns: ids, embeddings, metadata, documents
  """

  ids: list[Any] = []
  #metadatas: list[Any] = []
  documents: list[Any] = []

  # loop over chunks -> create vectors
  for i, chunk in enumerate(chunks):
    chunk: Any
    metadata = chunk.metadata
    pdf_id = metadata.get("pdf_id")
    page_number = metadata.get("page_number")

    chunk_id = create_chunk_id(
      pdf_id=pdf_id,
      page_number=page_number,
      chunk_index=i,
      chunk_text=chunk.page_content,
    )

    # push each id
    ids.append(chunk_id)
    # we only want the text
    documents.append(chunk.page_content)
    #metadatas.append(metadata)

  # 🧠 Compute embeddings (batch)
  print(f"🧩 Embedding {len(documents)} chunks...")
  embeddings = await embed_function.aembed_documents(documents)

  print("✅ embedding complete")

  return dict(
    ids=ids,
    embeddings=embeddings,
    #metadatas=metadatas,
    documents=chunks,
  )

# store in chroma db
def store_in_chroma(
    collection_name: str,
    embedding_data: dict[str, Any],
    embedding_function: Any = embedding_function,
    chroma_path: str = chroma_path,
) -> None:
  """
  connect to chroma, persist collection and stores embeddings
  """

  print(f"📂 connect to chroma collection: {collection_name} at {chroma_path}")

  chroma: Chroma = Chroma(
    collection_name=collection_name,
    persist_directory=chroma_path,
    embedding_function=embedding_function,
  )

  # check
  # existing = chroma._collection.count()
  # print(f"existing vectors in collection: {existing}")
  #print(embedding_data['documents'][0])
  print(f"💾 adding {len(embedding_data['documents'])} new vectors to chroma")

  chroma.add_documents(
    ids=embedding_data['ids'],
    documents=embedding_data['documents'],
    embeddings=embedding_data['embeddings'],
  )

  print(f"success store chroma db 📦: {chroma_path}")
  

#delete chunks
def delete_pdf_vectors(
    collection_name: str,
    pdf_id: str,
    chroma_path: str = chroma_path,
    embedding_function: OllamaEmbeddings = embedding_function,
) -> None:
  """ given pdf_id -> delete all vectors from chroma """

  print(f"🧹 deleting all vectors for: {pdf_id}")

  # connect to chroma collection
  chroma = Chroma(
    collection_name=collection_name,
    persist_directory=chroma_path,
    embedding_function=embedding_function,
  )

  # check if collection exists
  existing = chroma.get(where=dict(pdf_id=pdf_id))
  """
  {
  "ids": [...],
  "embeddings": None,   # not returned unless you request them
  "documents": None,    # not returned unless you request them
  "metadatas": None,    # not returned unless you request them
  }
  """

  if not existing or not existing.get("ids"):
    print(f"no embedding found for PDF {pdf_id}")
    return
  
  # ids to delete
  ids_to_delete = existing['ids']

  print(f"found {len(ids_to_delete)} vectors. deleting...")

  chroma.delete(ids=ids_to_delete)
  print(f"✅ Deleted {len(ids_to_delete)} vectors for PDF {pdf_id}")
