import requests
import json
from collections import Counter

# --------- НАСТРОЙКИ ---------

SOFT_SKILLS_LIST = [
    "Коммуникабельность",
    "Работа в команде",
    "Критическое мышление",
    "Тайм-менеджмент",
    "Лидерство",
    "Адаптивность",
    "Ответственность",
    "Эмоциональный интеллект",
    "Навыки презентации",
    "Стрессоустойчивость"
]

PROFESSION = "Frontend разработчик"
NUM_VACANCIES = 200
PER_PAGE = 50


# --------- ДОБАВЛЕНО: СЛОВАРЬ ОБЪЕДИНЕНИЙ ---------

NORMALIZATION_MAP = {
    # JavaScript
    "js": "javascript",
    "java script": "javascript",

    # React
    "react.js": "react",
    "reactjs": "react",
    "react 18": "react",
    "react18": "react",
    "react 19": "react",

    # Vue
    "vue.js": "vue",
    "vuejs": "vue",
    "vue js": "vue",
    "vue3": "vue",

    # REST API
    "rest": "rest api",
    "api": "rest api",
    "http": "rest api",
    "fetch api": "rest api",

    # HTML
    "html5": "html",
    "html/css": "html",

    # CSS
    "css3": "css",
    "scss": "css",
    "sass": "css",

    # Git
    "github": "git",
    "gitlab": "git",
    "bitbucket": "git",

    # PostgreSQL
    "postgres": "postgresql",

    # C#
    "с#": "c#"
}


# --------- ФУНКЦИИ ---------

def normalize(skill):
    skill = skill.strip().lower()
    return NORMALIZATION_MAP.get(skill, skill)


def get_vacancy_skills_from_hh(profession_name, num_vacancies):
    skills = []

    try:
        response = requests.get(
            "https://api.hh.ru/vacancies",
            params={"text": profession_name, "per_page": PER_PAGE, "page": 0},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        total_vacancies = data.get("found", 0)
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса вакансий: {e}")
        return skills

    pages = min((num_vacancies // PER_PAGE) + 1,
                (total_vacancies // PER_PAGE) + 1)

    for page in range(pages):
        params = {
            "text": profession_name,
            "per_page": PER_PAGE,
            "page": page
        }

        try:
            response = requests.get(
                "https://api.hh.ru/vacancies",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка страницы {page}: {e}")
            continue

        items = data.get("items", [])
        if not items:
            break

        for vac in items:
            vac_id = vac["id"]

            try:
                detail = requests.get(
                    f"https://api.hh.ru/vacancies/{vac_id}",
                    timeout=10
                ).json()
            except requests.exceptions.RequestException:
                continue

            for skill in detail.get("key_skills", []):
                skills.append(normalize(skill.get("name")))

    return skills


def separate_skills(skills):
    hard = []
    soft = []

    soft_normalized = [normalize(s) for s in SOFT_SKILLS_LIST]

    for skill in skills:
        if skill in soft_normalized:
            soft.append(skill)
        else:
            hard.append(skill)

    return hard, soft

def calculate_top_percent(skills, top_n=20, min_percent=1):
    counter = Counter(skills)
    total = len(skills)

    if total == 0:
        return {}

    # Считаем процент каждого навыка
    percent_data = {
        skill: (count / total) * 100
        for skill, count in counter.items()
    }

    # Оставляем только навыки выше порога
    filtered = {
        skill: percent
        for skill, percent in percent_data.items()
        if percent >= min_percent
    }

    # Сортируем по убыванию
    sorted_skills = sorted(
        filtered.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_n]

    # Пересчитываем проценты уже внутри отфильтрованной группы
    new_total = sum(percent for _, percent in sorted_skills)

    return {
        skill: round((percent / new_total) * 100, 2)
        for skill, percent in sorted_skills
    }


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# --------- ЗАПУСК ---------

if __name__ == "__main__":
    print(f"Собираем навыки по профессии: {PROFESSION}\n")

    skills_list = get_vacancy_skills_from_hh(PROFESSION, NUM_VACANCIES)

    print(f"Всего навыков собрано: {len(skills_list)}")

    # 1 Сохраняем ВСЕ найденные навыки!
    save_json("frontend_all_skills.json", skills_list)

    # 2 Разделяем на hard / soft
    hard_skills, soft_skills = separate_skills(skills_list)

    # 3 Считаем проценты
    top_data = {
        "profession": PROFESSION,
        "total_skills_found": len(skills_list),
        "hard_skills_top_percent": calculate_top_percent(hard_skills),
        "soft_skills_top_percent": calculate_top_percent(soft_skills)
    }

    # 4 Сохраняем топы!
    save_json("frontend_top_skills.json", top_data)

    print("\nФайлы созданы:")
    print("✔ frontend_all_skills.json")
    print("✔ frontend_top_skills.json")