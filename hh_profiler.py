import requests
import time
from collections import Counter
import json

BASE_URL = "https://api.hh.ru/vacancies"


def get_vacancies(profession, pages=3):
    vacancies = []

    for page in range(pages):
        params = {
            "text": profession,
            "per_page": 100,
            "page": page
        }

        response = requests.get(BASE_URL, params=params)
        data = response.json()

        vacancies.extend(data["items"])
        time.sleep(0.3)

    return vacancies


def get_vacancy_skills(vacancy_id):
    response = requests.get(f"https://api.hh.ru/vacancies/{vacancy_id}")
    data = response.json()

    return [skill["name"] for skill in data.get("key_skills", [])]


def build_skill_profile(profession):
    vacancies = get_vacancies(profession)
    skill_counter = Counter()

    for vacancy in vacancies:
        skills = get_vacancy_skills(vacancy["id"])
        skill_counter.update(skills)

    total = sum(skill_counter.values())

    profile = {
        skill: round(count / total, 4)
        for skill, count in skill_counter.items()
    }

    return profile


if __name__ == "__main__":
    profession_name = "Frontend-разработчик"
    profile = build_skill_profile(profession_name)

    with open("frontend_developer_profile.json", "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=4)

    print("Профиль сформирован и сохранён.")