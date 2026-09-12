import os
from pathlib import Path
from typing import List

import config
import requests
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


PUBLIC_URL = "https://disk.yandex.ru/d/bCSmO_HY5AwQDA"

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SOURCE_PATH = DATA_DIR / "lifting_facilities_rules.txt"
INDEX_DIR = BASE_DIR / "faiss_index"

EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 3000
CHUNK_OVERLAP = 300


def get_openai_api_key() -> str:
  api_key = os.getenv("OPEN_API_KEY") or os.getenv("OPENAI_API_KEY")
  if not api_key:
    raise ValueError("Не найден OPEN_API_KEY или OPENAI_API_KEY в .env")

  return api_key


def get_download_url(public_url: str) -> str:
  api_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
  response = requests.get(api_url, params={"public_key": public_url}, timeout=30)
  response.raise_for_status()
  return response.json()["href"]


def load_document() -> str:
  DATA_DIR.mkdir(exist_ok=True)

  if SOURCE_PATH.exists():
    return SOURCE_PATH.read_text(encoding="utf-8")

  download_url = get_download_url(PUBLIC_URL)
  response = requests.get(download_url, timeout=60)
  response.raise_for_status()

  text = response.content.decode("utf-8-sig")
  SOURCE_PATH.write_text(text, encoding="utf-8")

  return text


def split_text(text: str) -> List[Document]:
  splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""]
  )

  chunks = splitter.split_text(text)

  return [
    Document(
      page_content=chunk,
      metadata={
        "source": SOURCE_PATH.name,
        "chunk": index
      }
    )
    for index, chunk in enumerate(chunks)
  ]


def get_embeddings() -> OpenAIEmbeddings:
  return OpenAIEmbeddings(
    model=EMBEDDING_MODEL,
    api_key=get_openai_api_key()
  )


def build_faiss_index() -> None:
  print("Загружаю документ...")
  text = load_document()

  print("Нарезаю документ на фрагменты...")
  documents = split_text(text)

  print(f"Создаю embeddings для {len(documents)} фрагментов...")
  vector_store = FAISS.from_documents(documents, get_embeddings())

  vector_store.save_local(str(INDEX_DIR))

  print(f"Готово. FAISS-база сохранена в: {INDEX_DIR}")
  print(f"Исходный текст сохранен в: {SOURCE_PATH}")


def test_search(question: str, top_k: int = 4) -> None:
  vector_store = FAISS.load_local(
    str(INDEX_DIR),
    get_embeddings(),
    allow_dangerous_deserialization=True
  )

  results = vector_store.similarity_search(question, k=top_k)

  for index, document in enumerate(results, start=1):
    print(f"\n--- Фрагмент {index}, chunk {document.metadata['chunk']} ---")
    print(document.page_content[:1000])


def load_faiss_index() -> FAISS:
  if not INDEX_DIR.exists():
    build_faiss_index()

  return FAISS.load_local(
    str(INDEX_DIR),
    get_embeddings(),
    allow_dangerous_deserialization=True
  )


def search_context(question: str, top_k: int = 4) -> str:
  vector_store = load_faiss_index()
  documents = vector_store.similarity_search(question, k=top_k)

  return "\n\n".join(
    f"[Фрагмент {index}; chunk {document.metadata['chunk']}]\n{document.page_content}"
    for index, document in enumerate(documents, start=1)
  )


if __name__ == "__main__":
  build_faiss_index()
  test_search("Какие требования предъявляются к эксплуатации подъемных сооружений?")
