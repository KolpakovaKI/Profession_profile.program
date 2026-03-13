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
        "c++", "c++ developer", "c developer", "embedded c", "c++ программист", "программист c++",
        "c++ разработчик", "инженер-программист c/c++", "программист c/c++", "разработчик c/c++",
        "разработчик c", "c разработчик", "разработчик c++",

        "с++ программист", "программист с++",
        "с++ разработчик", "инженер-программист с/с++", "программист с/с++", "разработчик с/с++",
        "разработчик с", "с разработчик", "разработчик с++",

    ],

    "C# Developer": [
        "c#", "с#", ".net", "c# разработчик", "c# developer",
        "программист c#", "программист с#", "с# developer"
    ],

    "Frontend": [
        "frontend", "react", "vue", "angular",
        "javascript", "typescript", "html", "css",
        "фронтенд", "frontend developer", "ui developer", "web programmer",
        "web developer", "веб программист", "web программист",
        "wordpress", "битрикс", "bitrix", "drupal", "cms",
        "front developer", "фронтэнд", "верстальщик",
        "веб разработчик", "web разработчик", "front end developer"

    ],

    "Backend": [
        "backend", "node", "nestjs", "go", "api", "spring backend",
        "backend developer", "back end developer",
        "back end разработчик", "бекэнд разработчик", "бекэнд",
    ],

    "Fullstack": [
        "fullstack", "full stack", "фуллстек",
        "fullstack developer"
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
        "arduino", "встроенный",
        "fpga", "плис", "rtl", "verilog", "vhdl",
        "встраиваем",
        "firmware",
        "embedded"
    ],

    "Data / ML / AI": [
        "ml", "machine learning", "ai",
        "нейрон", "llm", "data engineer",
        "big data", "rag", "искусственный интеллект", "машинное обучение"
    ],

    "BI / Data": [
        "bi", "power bi", "etl",
        "dwh", "sql developer", "postgres",
        "oracle", "бд", "sql", "pl/sql", "database developer",
        "разработчик баз данных", "бд", "dba",
    ],

    "Data Analyst": [
        "data analyst",
        "аналитик данных",
        "data analytics",
        "data analysis",
        "bi analyst",
        "аналитик bi",
        "продуктовый аналитик",
        "product analyst",
        "marketing analyst",
        "маркетинговый аналитик",
        "system analyst",
        "analytics engineer",
        "системный аналитик",
        "аналитик 1c", "аналитик 1c"
    ],

    "1C": [
        "1с", "1c developer", "1 с"
    ],

    "QA/QI/Tester": [
        "qi", "qa", "tester", "тестировщик", "специалист по тестированию"
    ],

    "Engineer": [
        "software engineer", "программный инженер"
    ],

    "DB Admin": [
       "администратор баз данных", "системный администратор", "сетевой инженер", "сетевой администратор"
    ],

    "Project Manager": [
        "project manager", "product manager", "менеджер проектов",
        "проектный менеджер", "менеджер продуктов", "продуктовый менеджер",
        "менеджер продукта", "менеджер проекта", "менеджер по продукту"
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
        "automation engineer", "промышленный",
        "плк",
        "plc",
        "scada",
        "asu",
        "асу",
        "hmi"
    ],

    "Team Leader": [
        "team leader", "тимлид", "руководитель проектов"
    ],

    "Design": [
        "graphic designer", "product designer", "visual designer", "web designer",
        "графический дизайнер", "веб дизайнер",
        "ux ui дизайнер", "ui ux дизайнер", "ux designer",
        "ui designer", "ux/ui дизайнер", "ui/ux дизайнер"
        "ux дизайнер", "ui дизайнер",
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
    text = text.replace("ё", "е")
    return text

def classify_category(title):

    t = normalize(title)

    # 1C
    if "1с" in t or "1c" in t:
        return "1C"

    # сначала категории
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in t:
                return cat

    # технологии
    tech_map = {
        "python": "Python Developer",
        "java": "Java Developer",
        "php": "PHP Developer",
        "c#": "C# Developer",
        "c++": "C/C++ Developer",
        "rust": "C/C++ Developer",
        "scala": "Java Developer",
        "ruby": "Ruby Developer"
    }

    for tech, cat in tech_map.items():
        if tech in t:
            return cat

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

    # словарь вакансий по категориям
    category_files = {cat: [] for cat in categories}
    category_files["General Programmer"] = []
    category_files["Other IT"] = []

    for name in vacancies:

        # ---- категории ----
        cat = classify_category(name)
        categories_assigned.append(cat)

        # добавляем в общий словарь
        category_files.setdefault(cat, []).append(name)

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

    # убираем ненужные категории
    excluded = {"General Programmer", "Other IT"}

    filtered_counter = {
        cat: count
        for cat, count in cat_counter.items()
        if cat not in excluded
    }

    total_cat = sum(filtered_counter.values())

    with open("top_categories.txt", "w", encoding="utf-8") as f:
        f.write(f"Всего вакансий: {len(vacancies)}\n\n")
        f.write("Топ категорий:\n\n")

        for cat, count in sorted(filtered_counter.items(), key=lambda x: x[1], reverse=True):
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
    # ---------- ФАЙЛЫ ПО КАТЕГОРИЯМ ----------

    os.makedirs("categories", exist_ok=True)

    for cat, vacs in category_files.items():

        safe_name = cat.replace("/", "_").replace(" ", "_")
        filename = f"categories/{safe_name}.txt"

        with open(filename, "w", encoding="utf-8") as f:

            f.write(f"{cat}: {len(vacs)} вакансий\n\n")

            for v in vacs:
                f.write(v + "\n")

    print("Файлы категорий сохранены в папке categories")

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