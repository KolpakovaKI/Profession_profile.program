import requests
import json
import re
from datetime import datetime, timedelta
from collections import Counter

# --------- НАСТРОЙКИ ---------

SEARCH_QUERY = "IT"
PER_PAGE = 100
DAYS_STEP = 7          # шаг разбивки по датам
TOTAL_DAYS = 365        # за сколько дней назад собираем


# --------- НОРМАЛИЗАЦИЯ ---------

NORMALIZATION_MAP = {
    "front-end": "frontend",
    "front end": "frontend",
    "back-end": "backend",
    "back end": "backend",
    "full-stack": "fullstack",
    "full stack": "fullstack",
    "разработчик": "developer",
}

LEVEL_WORDS = [
    "junior", "middle", "senior", "lead",
    "младший", "старший", "ведущий"
]


def normalize_title(title):
    title = title.lower().strip()

    for level in LEVEL_WORDS:
        title = title.replace(level, "")

    for key, value in NORMALIZATION_MAP.items():
        title = title.replace(key, value)

    title = re.sub(r"[^\w\s]", "", title)
    title = re.sub(r"\s+", " ", title)

    return title.strip()


# --------- ПАРСИНГ С РАЗБИВКОЙ ПО ДАТАМ ---------

def get_vacancies_by_date_range(date_from, date_to):
    titles = []
    page = 0
    MAX_PAGES = 20  # лимит HH

    while page < MAX_PAGES:
        try:
            response = requests.get(
                "https://api.hh.ru/vacancies",
                params={
                    "text": SEARCH_QUERY,
                    "professional_role": 96,
                    "per_page": PER_PAGE,
                    "page": page,
                    "date_from": date_from.isoformat(),
                    "date_to": date_to.isoformat()
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            break

        items = data.get("items", [])
        if not items:
            break

        for vac in items:
            raw_title = vac.get("name")
            titles.append(normalize_title(raw_title))

        page += 1

    return titles


def collect_all_titles():
    all_titles = []

    today = datetime.now()
    start_date = today - timedelta(days=TOTAL_DAYS)

    current_date = start_date

    while current_date < today:
        next_date = current_date + timedelta(days=DAYS_STEP)

        print(f"Сбор вакансий с {current_date.date()} по {next_date.date()}")

        titles = get_vacancies_by_date_range(current_date, next_date)
        all_titles.extend(titles)

        current_date = next_date

    return all_titles


# --------- АНАЛИЗ ---------

def calculate_top_percent(data_list, top_n=10):
    counter = Counter(data_list)
    total = len(data_list)

    top = counter.most_common(top_n)

    return {
        title: {
            "count": count,
            "percent": round(count / total * 100, 2)
        }
        for title, count in top
    }


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# --------- ЗАПУСК ---------

if __name__ == "__main__":
    print("Начинаем сбор данных...\n")

    titles = collect_all_titles()

    # убираем дубликаты
    titles = list(set(titles))

    print(f"\nВсего уникальных вакансий собрано: {len(titles)}")

    save_json("it_all_titles_list.json", titles)

    top_professions = calculate_top_percent(titles, top_n=10)

    result = {
        "total_vacancies_analyzed": len(titles),
        "top_10_it_professions": top_professions
    }

    save_json("it_top_10_professions.json", result)

    print("\nФайлы созданы:")
    print("✔ it_all_titles_list.json")
    print("✔ it_top_10_professions.json")