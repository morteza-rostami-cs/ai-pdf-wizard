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
from langchain_core.documents import Document

# embedding
from langchain.text_splitter import CharacterTextSplitter
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
from src.services import prepare_page_for_embedding

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
embedding = OllamaEmbeddings(
  base_url=settings.LLM_URL,
  model=settings.EMBED_MODEL,
  temperature=0.6,
  # client_options={"proxies": None} 
)

# string parser
parser = StrOutputParser()
