import os

import config
import anthropic


CLAUDE_MODEL = "claude-sonnet-4-5"
STOP_WORDS = {"стоп", "stop", "exit", "quit"}


def get_claude_api_key() -> str:
  api_key = os.getenv("CLAUDE_KEY")
  if not api_key:
    raise ValueError("Не найден CLAUDE_KEY в .env")

  return api_key


def get_client() -> anthropic.Anthropic:
  return anthropic.Anthropic(api_key=get_claude_api_key())


def get_text(message) -> str:
  return "".join(
    block.text
    for block in message.content
    if getattr(block, "type", None) == "text"
  )


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


def ask_claude(question: str, context: str, temperature: float = 0.0) -> str:
  message = get_client().messages.create(
    model=CLAUDE_MODEL,
    max_tokens=1200,
    extra_body={
      "temperature": temperature
    },
    messages=[
      {
        "role": "user",
        "content": build_rag_prompt(question, context)
      }
    ]
  )

  return get_text(message)


def main() -> None:
  print("Claude готов. Пиши сообщение, для выхода: стоп")

  while True:
    user_text = input("Вы: ").strip()

    if not user_text:
      continue

    if user_text.lower() in STOP_WORDS:
      print("Диалог завершен.")
      break

    message = get_client().messages.create(
      model=CLAUDE_MODEL,
      max_tokens=1000,
      messages=[
        {
          "role": "user",
          "content": user_text
        }
      ]
    )

    print(f"Claude: {get_text(message)}")


if __name__ == "__main__":
  main()
