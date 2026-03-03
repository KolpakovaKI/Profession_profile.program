import requests
from skill_utils import get_top_skills

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

def get_vacancy_skills_from_hh(profession_name, num_vacancies=800):
    skills = []
    per_page = 50
    try:
        response = requests.get(
            "https://api.hh.ru/vacancies",
            params={"text": profession_name, "per_page": per_page, "page": 0},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        total_vacancies = data.get("found", 0)
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса вакансий: {e}")
        return skills

    pages = min((num_vacancies // per_page) + 1, (total_vacancies // per_page) + 1)

    for page in range(pages):
        params = {"text": profession_name, "per_page": per_page, "page": page}
        try:
            response = requests.get("https://api.hh.ru/vacancies", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса вакансий на странице {page}: {e}")
            continue

        items = data.get("items", [])
        if not items:
            break

        for vac in items:
            vac_id = vac["id"]
            try:
                vac_detail = requests.get(f"https://api.hh.ru/vacancies/{vac_id}", timeout=10).json()
            except requests.exceptions.RequestException as e:
                print(f"Ошибка запроса вакансии {vac_id}: {e}")
                continue

            for skill in vac_detail.get("key_skills", []):
                skills.append(skill.get("name"))

    return skills

def separate_skills(skills_list):
    hard_skills = []
    soft_skills = []
    for skill in skills_list:
        if skill in SOFT_SKILLS_LIST:
            soft_skills.append(skill)
        else:
            hard_skills.append(skill)
    return hard_skills, soft_skills

def convert_to_percentage(top_skills, total_count):
    """
    Преобразует список навыков с количеством в проценты
    """
    return [(skill, round(count / total_count * 100, 2)) for skill, count in top_skills]

if __name__ == "__main__":
    profession = "Frontend разработчик"
    num_vacancies = 200
    print(f"Собираем навыки по профессии: {profession}...\n")
    skills_list = get_vacancy_skills_from_hh(profession, num_vacancies=num_vacancies)

    print(f"Всего навыков собрано: {len(skills_list)}\n")

    hard_skills, soft_skills = separate_skills(skills_list)

    top_hard = get_top_skills(hard_skills, top_n=20)
    top_soft = get_top_skills(soft_skills, top_n=20)

    # Переводим в проценты
    top_hard_percent = convert_to_percentage(top_hard, len(hard_skills))
    top_soft_percent = convert_to_percentage(top_soft, len(soft_skills) if soft_skills else 1)  # чтобы не делить на 0

    print("ТОП-20 Hard skills (в %):")
    for i, (skill, percent) in enumerate(top_hard_percent, start=1):
        print(f"{i}. {skill} — {percent}%")

    print("\nТОП-20 Soft skills (в %):")
    for i, (skill, percent) in enumerate(top_soft_percent, start=1):
        print(f"{i}. {skill} — {percent}%")