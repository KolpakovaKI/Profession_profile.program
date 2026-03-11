import requests
from collections import Counter
import re
import time
from datetime import datetime, timedelta
import os

URL = "https://api.hh.ru/vacancies"

# IT роли HH
roles = [
156,160,10,12,150,25,165,34,36,73,155,96,
164,104,157,107,112,113,148,114,116,121,124,125,126
]

# ========= категории =========
categories = {
    "PHP Developer": [
        "php", "php программист", "php developer", "laravel", "symfony"
    ],

    "Java Developer": [
        "java", "java программист", "java developer", "spring", "hibernate"
    ],

    "Python Developer": [
        "python", "python программист", "python developer", "django", "flask"
    ],

    "C/C++ Developer": [
        "c++", "c", "с++", "c developer", "c++ developer", "qt", "linux developer"
    ],

    "C# Developer": [
        "c#", ".net", "c# разработчик", "c# developer"
    ],

    "Web Developer": [
            "web разработчик", "web programmer", "веб-разработчик", "web developer", "web-программист", "Веб-разработчик"
        ],

    "Tester": [
        "tester", "тестировщик", "специалист по тестированию"
    ],

    "Frontend": [
        "frontend", "react", "vue", "angular",
        "javascript", "typescript", "html", "css",
        "фронтенд", "web разработчик", "веб-разработчик",
        "frontend developer", "ui developer"
    ],

    "Backend": [
        "backend", "node", "nestjs", "go", "api", "бэкенд", "бекенд", "spring backend"
    ],

    "Fullstack": [
        "fullstack", "full-stack", "full stack", "фуллстек",
        "fullstack developer", "full-stack developer"
    ],

    "Mobile": [
        "android", "ios", "flutter", "react native",
        "kotlin", "swift", "мобильный", "android-разработчик",
        "ios-разработчик", "mobile developer"
    ],

    "GameDev": [
        "unity", "unreal", "gamedev", "game developer",
        "игровой", "game dev"
    ],

    "Embedded": [
        "embedded", "микроконтроллер", "stm32", "firmware",
        "arduino", "встроенный"
    ],

    "Data / ML / AI": [
        "ml", "machine learning", "ai",
        "нейрон", "llm", "data engineer",
        "big data", "rag", "искусственный интеллект", "машинное обучение"
    ],

    "BI / Data": [
        "bi", "power bi", "etl",
        "dwh", "sql developer", "postgres",
        "oracle", "аналитик", "бд", "data analyst"
    ],

    "1C": [
        "1с", "1c developer", "1 с"
    ],

    "QA/QI": [
            "qi", "qa"
        ],

    "Engineer": [
                "engineer", "инженер"
            ],

    "DB Admin": [
                "администратор", "администратор баз данных", "системный администратор"
                ],

    "Project Manager": [
        "Project Manager", "product manager", "менеджер", "менеджер проектов", "проектный менеджер"
    ],

    "DevOps": [
        "devops", "kubernetes", "docker",
        "ci/cd"
    ],

    "Low-code / No-code": [
        "low code", "no code",
        "power platform", "tilda"
    ],

    "Automation / RPA": [
        "rpa", "robotization",
        "zennoposter", "automation", "роботизация"
    ],

    "PLC / Industrial": [
        "асу", "чпу", "plc", "siemens",
        "automation engineer", "промышленный"
    ],

    "Team Leader": [
            "team leader", "тимлид", "руководитель проектов", "ИТ-лидер", "graphic"
    ],

    "Design": [
        "designer", "дизайнер", "ux", "ui", "graphic",
        "ux/ui designer", "product designer", "visual designer", "web designer"
    ]
}

# ---------- СЛОВАРЬ ТЕХНОЛОГИЙ ----------
technology_patterns = {
    "Python": r"\bpython\b",
    "Java": r"\bjava\b",
    "JavaScript": r"javascript|\bjs\b",
    "TypeScript": r"typescript",
    "PHP": r"\bphp\b",
    "C#": r"c#|\.net",
    "C++": r"c\+\+",
    "C": r"\bc\b",
    "Go": r"golang|\bgo\b",
    "Ruby": r"\bruby\b",
    "Rust": r"\brust\b",
    "Kotlin": r"kotlin",
    "Swift": r"swift",
    "React": r"react",
    "Vue": r"vue",
    "Angular": r"angular",
    "Flutter": r"flutter",
    "React Native": r"react native",
    "Android": r"android",
    "iOS": r"\bios\b",
    "Django": r"django",
    "Spring": r"spring",
    "Laravel": r"laravel",
    "Node.js": r"node\.?js",
    "PostgreSQL": r"postgres",
    "MySQL": r"mysql",
    "MongoDB": r"mongodb",
    "Redis": r"redis",
    "Docker": r"docker",
    "Kubernetes": r"kubernetes|k8s",
    "CI/CD": r"ci.?cd",
    "Power BI": r"power bi",
    "TensorFlow": r"tensorflow",
    "PyTorch": r"pytorch"
}

# ---------- ФУНКЦИИ КЛАССИФИКАЦИИ ----------
def normalize(text):
    text = text.lower()
    text = text.replace("-", " ")
    return text

def classify_category(title):
    t = normalize(title)

    # сначала точные категории
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in t:
                return cat

    # Generic programmer только если нет технологий
    tech_keywords = [
        "python", "java", "c#", "c++", "c", "javascript", "typescript",
        "php", "go", "ruby", "rust", "kotlin", "swift"
    ]
    if any(k in t for k in tech_keywords):
        # если есть явная технология, пробуем присвоить конкретную категорию
        if "backend" in t or "api" in t or "django" in t or "flask" in t or "spring" in t or "php" in t:
            return "Backend"
        if "frontend" in t or "react" in t or "vue" in t or "angular" in t or "web" in t:
            return "Frontend"
        if "android" in t or "ios" in t or "kotlin" in t or "swift" in t:
            return "Mobile"

    if "разработчик" in t or "developer" in t or "программист" in t:
        return "General Programmer"

    return "Other IT"

# ---------- СБОР ВАКАНСИЙ ----------
def collect_vacancies():

    vacancies = []
    seen_ids = set()

    days = 60
    today = datetime.now()

    for i in range(days):

        date_from = (today - timedelta(days=i+1)).strftime("%Y-%m-%d")
        date_to = (today - timedelta(days=i)).strftime("%Y-%m-%d")

        print(f"\nСбор за {date_from}")

        for page in range(20):

            params = {
                "professional_role": roles,
                "per_page": 100,
                "page": page,
                "date_from": date_from,
                "date_to": date_to
            }

            response = requests.get(URL, params=params)

            if response.status_code != 200:
                break

            data = response.json()
            items = data.get("items", [])

            if not items:
                break

            for item in items:

                vacancy_id = item["id"]

                if vacancy_id in seen_ids:
                    continue

                seen_ids.add(vacancy_id)
                vacancies.append(item["name"])

            print(f"  страница {page} | вакансий: {len(vacancies)}")

            time.sleep(0.3)

    with open("vacancies.txt", "w", encoding="utf-8") as f:
        for v in vacancies:
            f.write(v + "\n")

    print("\nvacancies.txt обновлён")

# ---------- АНАЛИЗ ----------
def analyze_professions():

    if not os.path.exists("vacancies.txt"):
        print("Сначала нужно собрать вакансии")
        return

    with open("vacancies.txt", "r", encoding="utf-8") as f:
        vacancies = [line.strip() for line in f]

    compiled_tech = {
        tech: re.compile(pattern, re.IGNORECASE)
        for tech, pattern in technology_patterns.items()
    }

    categories_assigned = []
    other_it_list = []
    general_programmer_list = []
    technologies = []

    for name in vacancies:

        # ---- категории ----
        cat = classify_category(name)
        categories_assigned.append(cat)

        if cat == "Other IT":
            other_it_list.append(name)
        elif cat == "General Programmer":
            general_programmer_list.append(name)

        # ---- технологии ----
        t_lower = name.lower()
        for tech, pattern in compiled_tech.items():
            if pattern.search(t_lower):
                technologies.append(tech)

    # ---------- ТОП категорий ----------
    cat_counter = Counter(categories_assigned)
    total_cat = sum(cat_counter.values())

    with open("top_categories.txt", "w", encoding="utf-8") as f:
        f.write(f"Всего вакансий: {len(vacancies)}\n\n")
        f.write("Топ категорий:\n\n")
        for cat, count in cat_counter.most_common(15):
            percent = round(count / total_cat * 100, 2)
            f.write(f"{cat}: {percent}% ({count})\n")

    # ---------- ТОП ТЕХНОЛОГИЙ ----------
    tech_counter = Counter(technologies)
    total_tech = sum(tech_counter.values())

    with open("top_technologies.txt", "w", encoding="utf-8") as f:
        f.write(f"Всего технологий найдено: {total_tech}\n\n")
        f.write("Топ технологий:\n\n")
        for tech, count in tech_counter.most_common(20):
            percent = round(count / total_tech * 100, 2)
            f.write(f"{tech}: {percent}% ({count})\n")

    # ---------- OTHER IT ----------
    with open("other_it.txt", "w", encoding="utf-8") as f:
        f.write(f"Other IT вакансии: {len(other_it_list)}\n\n")
        for v in other_it_list:
            f.write(v + "\n")

    # ---------- GENERAL PROGRAMMER ----------
    with open("general_programmer.txt", "w", encoding="utf-8") as f:
        f.write(f"General Programmer вакансии: {len(general_programmer_list)}\n\n")
        for v in general_programmer_list:
            f.write(v + "\n")

    print("top_categories.txt сохранён")
    print("top_technologies.txt сохранён")
    print("other_it.txt сохранён")
    print("general_programmer.txt сохранён")

# ---------- МЕНЮ ----------
while True:

    print("\n--- МЕНЮ ---")
    print("1 - Собрать новые вакансии")
    print("2 - Посчитать аналитику")
    print("3 - Выход")

    choice = input("Выберите действие: ")

    if choice == "1":
        collect_vacancies()

    elif choice == "2":
        analyze_professions()

    elif choice == "3":
        print("Выход из программы")
        break

    else:
        print("Неверный ввод")