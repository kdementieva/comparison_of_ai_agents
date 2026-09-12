import os

import config
from google import genai
from google.genai import types


GEMINI_MODEL = "gemini-3.8-flash"
STOP_WORDS = {"стоп", "stop", "exit", "quit"}
_client = None


def get_gemini_api_key() -> str:
  api_key = os.getenv("GEMINI_KEY") or os.getenv("GEMINI_API_KEY")
  if not api_key:
    raise ValueError("Не найден GEMINI_KEY или GEMINI_API_KEY в .env")

  return api_key


def get_client() -> genai.Client:
  global _client

  if _client is None:
    _client = genai.Client(api_key=get_gemini_api_key())

  return _client


def build_rag_prompt(question: str, context: str) -> str:
  return f"""
Ты нейро-консультант по документу "Правила безопасности опасных производственных объектов, на которых используются подъемные сооружения".

Отвечай только по контексту ниже.
Если в контексте нет ответа, прямо скажи: "В найденном контексте нет точной информации".
Не придумывай требования, номера пунктов и формулировки.

Контекст:
{context}

Вопрос:
{question}
""".strip()


def ask_gemini(question: str, context: str, temperature: float = 0.0) -> str:
  client = get_client()
  response = client.models.generate_content(
    model=GEMINI_MODEL,
    contents=build_rag_prompt(question, context),
    config=types.GenerateContentConfig(
      temperature=temperature,
      max_output_tokens=1200
    )
  )

  return response.text


def main() -> None:
  print("Gemini готов. Пиши сообщение, для выхода: стоп")

  while True:
    user_text = input("Вы: ").strip()

    if not user_text:
      continue

    if user_text.lower() in STOP_WORDS:
      print("Диалог завершен.")
      break

    client = get_client()
    response = client.models.generate_content(
      model=GEMINI_MODEL,
      contents=user_text
    )

    print(f"Gemini: {response.text}")


if __name__ == "__main__":
  main()
