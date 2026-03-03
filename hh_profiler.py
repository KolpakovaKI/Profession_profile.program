import requests
import time
from collections import Counter
import json

BASE_URL = "https://api.hh.ru/vacancies"

# =========================
# 1. Нормализация навыков
# =========================

NORMALIZATION_MAP = {
    # React
    "ReactJS": "React",
    "React.js": "React",
    "React 18": "React",
    "React19": "React",
    "React/Query": "React",

    # Vue
    "VueJS": "Vue.js",
    "Vue3": "Vue.js",
    "Vue2": "Vue.js",
    "VUE JS": "Vue.js",

    # JS
    "Java Script": "JavaScript",
    "JS": "JavaScript",
    "VanillaJS": "JavaScript",
    "vanilla.js": "JavaScript",

    # Next
    "NextJS": "Next.js",
    "Next js": "Next.js",
    "Next": "Next.js",

    # CSS
    "CSS3": "CSS",
    "CSS/SCSS": "CSS",
    "SCSS": "CSS",
    "Sass": "CSS",

    # HTML
    "HTML5": "HTML",
    "HTML/CSS": "HTML",
    "HTML5 / CSS3 / JavaScript": "HTML"
}

# soft skills и мусор
SOFT_SKILLS = [
    "Работа в команде",
    "Ответственность",
    "Ответственное отношение к работе",
    "Коммуникабельность",
    "Умение работать в коллективе",
    "Деловое общение",
    "Деловая переписка",
    "Организаторские навыки",
    "Аналитическое мышление",
    "Навыки коммуникации"
]


def normalize_skill(skill):
    skill = skill.strip()

    if skill in NORMALIZATION_MAP:
        return NORMALIZATION_MAP[skill]

    return skill


# =========================
# 2. Получение вакансий
# =========================

def get_vacancies(profession, pages=1):
    vacancies = []

    for page in range(pages):
        params = {
            "text": profession,
            "per_page": 100,
            "page": page
        }

        response = requests.get(BASE_URL, params=params, timeout=5)
        data = response.json()

        vacancies.extend(data["items"])
        time.sleep(0.3)

    return vacancies


def get_vacancy_skills(vacancy_id):
    try:
        response = requests.get(
            f"https://api.hh.ru/vacancies/{vacancy_id}",
            timeout=5
        )
        data = response.json()
        return [skill["name"] for skill in data.get("key_skills", [])]
    except:
        return []


# =========================
# 3. Формирование профиля
# =========================

def build_skill_profile(profession, pages=1):
    vacancies = get_vacancies(profession, pages)
    skill_counter = Counter()

    for vacancy in vacancies:
        skills = get_vacancy_skills(vacancy["id"])

        for skill in skills:
            if skill in SOFT_SKILLS:
                continue

            normalized = normalize_skill(skill)
            skill_counter[normalized] += 1

        time.sleep(0.2)

    # Берём только TOP-20
    top_20 = skill_counter.most_common(20)

    total = sum(count for _, count in top_20)

    profile = {
        skill: round(count / total, 4)
        for skill, count in top_20
    }

    return profile


# =========================
# 4. Запуск
# =========================

if __name__ == "__main__":
    profession_name = "Frontend разработчик"
    profile = build_skill_profile(profession_name, pages=1)

    with open("frontend_profile_top20.json", "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=4)

    print("TOP-20 профиль сформирован.")