import os
import django
import sys
from datetime import date, timedelta
import random

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import Role, ProjectStatus, TaskStatus, User, Project, Task

def generate_demo_data():
    print("Starting demo data generation...")

    # 1. Ensure Roles
    roles_data = ["head", "pm", "employee", "customer"]
    roles = {}
    for rname in roles_data:
        role, _ = Role.objects.get_or_create(name=rname)
        roles[rname] = role

    # 2. Ensure Statuses
    p_statuses = ["Новый", "В работе", "Завершен", "Приостановлен"]
    project_statuses = {}
    for s in p_statuses:
        st, _ = ProjectStatus.objects.get_or_create(name=s)
        project_statuses[s] = st

    t_statuses = ["К выполнению", "В процессе", "Тестирование", "Выполнено"]
    task_statuses = {}
    for s in t_statuses:
        st, _ = TaskStatus.objects.get_or_create(name=s)
        task_statuses[s] = st

    # 3. Create Users
    def create_user(username, full_name, role_name, position=""):
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password("123")
            user.full_name = full_name
            user.role = roles[role_name]
            user.position = position
            user.email = f"{username}@test.ru"
            user.save()
            print(f"Created user: {username} ({role_name})")
        return user

    head = create_user("head", "Иванов Иван Иванович", "head", "Генеральный директор")
    pm_smirnov = create_user("pm_smirnov", "Смирнов Алексей Петрович", "pm", "Старший менеджер проектов")
    pm_belova = create_user("pm_belova", "Белова Ирина Сергеевна", "pm", "Менеджер проектов")
    
    # Employees
    devs = [
        create_user("dev_ivanov", "Иванов Дмитрий", "employee", "Backend разработчик"),
        create_user("dev_petrov", "Петров Сергей", "employee", "Frontend разработчик"),
        create_user("dev_sidorov", "Сидоров Максим", "employee", "Fullstack разработчик"),
        create_user("qa_elena", "Тихонова Елена", "employee", "QA инженер"),
        create_user("designer_anton", "Волков Антон", "employee", "UI/UX дизайнер"),
    ]

    # Customers
    customers = [
        create_user("techno_prom", "ООО ТехноПром", "customer", "Заказчик (Промышленность)"),
        create_user("mega_stroy", "ГК МегаСтрой", "customer", "Заказчик (Строительство)"),
        create_user("agro_holding", "АгроХолдинг Юг", "customer", "Заказчик (Сельское хозяйство)"),
    ]

    # 4. Create Projects
    print("Creating projects and tasks...")
    
    projects_content = [
        {
            "title": "Интеллектуальная система мониторинга цеха",
            "desc": "Разработка IoT-решения для отслеживания состояния станков в реальном времени.",
            "cust": customers[0],
            "pm": pm_smirnov,
            "budget": 2450000,
            "status": "В работе",
            "tasks": [
                ("Сбор технических требований", devs[1], "Выполнено", 5),
                ("Проектирование архитектуры БД", devs[0], "Выполнено", 10),
                ("Разработка модуля интеграции с датчиками", devs[0], "В процессе", 20),
                ("Создание дашборда мониторинга", devs[1], "К выполнению", 15),
                ("Тестирование отказоустойчивости", devs[3], "К выполнению", 30),
            ]
        },
        {
            "title": "Мобильный кабинет жителя «МегаДом»",
            "desc": "Приложение для оплаты ЖКХ, подачи заявок и управления умным домом.",
            "cust": customers[1],
            "pm": pm_belova,
            "budget": 1800000,
            "status": "Новый",
            "tasks": [
                ("Проектирование UX-прототипов", devs[4], "Выполнено", 7),
                ("Верстка экранов авторизации", devs[1], "В процессе", 12),
                ("Настройка API шлюза", devs[2], "К выполнению", 14),
            ]
        },
        {
            "title": "Автоматизация закупок ГК СтройТех",
            "desc": "Внедрение системы автоматического подбора поставщиков по критериям цены и сроков.",
            "cust": customers[1],
            "pm": pm_smirnov,
            "budget": 3200000,
            "status": "Завершен",
            "tasks": [
                ("Анализ рынка поставщиков", devs[3], "Выполнено", -10),
                ("Разработка алгоритма ранжирования", devs[0], "Выполнено", -5),
                ("Финальное внедрение", devs[2], "Выполнено", -1),
            ]
        },
        {
            "title": "Цифровая ферма: Контроль полива",
            "desc": "Система автоматизированного управления ирригацией на площади 500 Га.",
            "cust": customers[2],
            "pm": pm_belova,
            "budget": 950000,
            "status": "В работе",
            "tasks": [
                ("Картографирование участков", devs[3], "Выполнено", 0),
                ("Разработка мобильного клиента", devs[2], "В процессе", 15),
            ]
        }
    ]

    for p_data in projects_content:
        p = Project.objects.create(
            title=p_data["title"],
            description=p_data["desc"],
            customer=p_data["cust"],
            pm=p_data["pm"],
            planned_budget=p_data["budget"],
            status=project_statuses[p_data["status"]],
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=90)
        )
        print(f"Project created: {p.title}")
        
        for t_title, assignee, status_name, days_offset in p_data["tasks"]:
            Task.objects.create(
                project=p,
                title=t_title,
                assignee=assignee,
                status=task_statuses[status_name],
                deadline=date.today() + timedelta(days=days_offset),
                cost=random.randint(50000, 200000)
            )

    print("Demo data successfully created!")

if __name__ == "__main__":
    generate_demo_data()
