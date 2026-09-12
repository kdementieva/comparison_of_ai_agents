import config
from claude import ask_claude
from db import search_context
from experiments import save_experiment
from gemini import ask_gemini


STOP_WORDS = {"стоп", "stop", "exit", "quit"}


def ask_int(prompt: str, default: int) -> int:
  value = input(f"{prompt} [{default}]: ").strip()
  if not value:
    return default

  return int(value)


def ask_float(prompt: str, default: float) -> float:
  value = input(f"{prompt} [{default}]: ").strip()
  if not value:
    return default

  return float(value)


def ask_yes_no(prompt: str) -> int:
  while True:
    value = input(f"{prompt} [да/нет]: ").strip().lower()

    if value in {"да", "д", "yes", "y", "1"}:
      return 1

    if value in {"нет", "н", "no", "n", "0"}:
      return 0

    print("Введите да или нет.")


def choose_model() -> str:
  print("Выбери модель:")
  print("1 - Claude")
  print("2 - Gemini")

  while True:
    choice = input("Модель [1]: ").strip() or "1"

    if choice == "1":
      return "claude"

    if choice == "2":
      return "gemini"

    print("Введите 1 или 2.")


def answer_question(model: str, question: str, top_k: int, temperature: float) -> str:
  context = search_context(question, top_k=top_k)

  if model == "claude":
    return ask_claude(question, context, temperature=temperature)

  return ask_gemini(question, context, temperature=temperature)


def main() -> None:
  print("Нейро-консультант по правилам безопасности подъемных сооружений")
  print("Если FAISS-базы еще нет, она будет создана автоматически.")

  model = choose_model()
  top_k = ask_int("Сколько фрагментов документа давать модели, top_k", 4)
  temperature = ask_float("Температура ответа", 0.0)

  print("\nПиши вопросы. Для выхода: стоп\n")

  while True:
    question = input("Вопрос: ").strip()

    if not question:
      continue

    if question.lower() in STOP_WORDS:
      print("Диалог завершен.")
      break

    try:
      answer = answer_question(model, question, top_k, temperature)
    except Exception as error:
      print(f"\nНе получилось получить ответ от {model}: {error}")
      print("Ответ не записан в базу. Попробуйте еще раз или выберите другую модель.\n")
      continue

    print(f"\nОтвет {model}:\n{answer}\n")

    print("Анкета для таблицы:")
    prompt_accuracy = input(
      "Точность промпта (например: общий / средний / строгий): "
    ).strip()
    matches_document = ask_yes_no("Ответ соответствует документу?")

    save_experiment(
      model_name=model,
      question=question,
      answer=answer,
      temperature=temperature,
      context_depth=top_k,
      prompt_accuracy=prompt_accuracy,
      matches_document=matches_document
    )

    print("Записала результат в базу.\n")


if __name__ == "__main__":
  main()
