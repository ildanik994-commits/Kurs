import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk

# Импортируем нашу логику базы данных из уже готового бекенда!
from database import SessionLocal, engine, Base
import models
import hashlib

# Установка современного стиля
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success

        # Заголовок
        self.title_label = ctk.CTkLabel(self, text="Авторизация ИС", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(40, 20))

        # Логин
        self.username_entry = ctk.CTkEntry(self, placeholder_text="Имя пользователя", width=200)
        self.username_entry.pack(pady=10)

        # Пароль
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Пароль", show="*", width=200)
        self.password_entry.pack(pady=10)

        # Кнопка входа
        self.login_button = ctk.CTkButton(self, text="Войти", command=self.login, width=200)
        self.login_button.pack(pady=20)
        
        # Подсказка
        self.hint = ctk.CTkLabel(self, text="Демо: head / pm / emp\nПароль: 123", text_color="gray", font=ctk.CTkFont(size=11))
        self.hint.pack(side="bottom", pady=20)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()

        db = SessionLocal()
        user = db.query(models.User).filter(models.User.username == username).first()
        db.close()

        if user and user.password_hash == hashed_pw:
            self.on_login_success(user)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, user, on_logout):
        super().__init__(master)
        self.user = user
        self.on_logout = on_logout

        # Верхняя панель
        self.top_bar = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.top_bar.pack(fill="x", side="top")
        
        self.welcome_label = ctk.CTkLabel(self.top_bar, text=f"Добро пожаловать, {user.full_name} ({user.role})", font=ctk.CTkFont(weight="bold"))
        self.welcome_label.pack(side="left", padx=20, pady=10)
        
        self.logout_btn = ctk.CTkButton(self.top_bar, text="Выйти", fg_color="transparent", border_width=1, command=self.on_logout)
        self.logout_btn.pack(side="right", padx=20)

        # Навигация (вкладки)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.tab_projects = self.tabview.add("Проекты")
        self.tab_tasks = self.tabview.add("Мои задачи")
        
        self.build_projects_tab()
        self.build_tasks_tab()
        
    def build_projects_tab(self):
        project_label = ctk.CTkLabel(self.tab_projects, text="Список проектов автоматизации", font=ctk.CTkFont(size=18, weight="bold"))
        project_label.pack(pady=10)
        
        db = SessionLocal()
        if self.user.role in ['head', 'pm']:
            projects = db.query(models.Project).all()
        elif self.user.role == 'customer':
            projects = db.query(models.Project).filter(models.Project.customer_id == self.user.id).all()
        else:
            projects = db.query(models.Project).join(models.Task).filter(models.Task.assignee_id == self.user.id).distinct().all()
        db.close()

        # Используем обычный Treeview из tkinter (стилизованный) для таблиц
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0)
        style.configure("Treeview.Heading", background="#1f538d", foreground="white", relief="flat")
        style.map("Treeview", background=[('selected', '#1f538d')])

        columns = ("id", "title", "status", "budget")
        self.tree = ttk.Treeview(self.tab_projects, columns=columns, show="headings", height=10)
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=50, anchor="center")
        self.tree.heading("title", text="Наименование")
        self.tree.column("title", width=300)
        self.tree.heading("status", text="Статус")
        self.tree.column("status", width=100, anchor="center")
        self.tree.heading("budget", text="Бюджет (руб)")
        self.tree.column("budget", width=120, anchor="e")

        for p in projects:
            self.tree.insert("", "end", values=(p.id, p.title, p.status, f"{p.planned_budget:,.2f}"))
            
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
    def build_tasks_tab(self):
        task_label = ctk.CTkLabel(self.tab_tasks, text="Список назначенных задач", font=ctk.CTkFont(size=18, weight="bold"))
        task_label.pack(pady=10)

        db = SessionLocal()
        if self.user.role in ['head', 'pm']:
            tasks = db.query(models.Task).all()
        else:
            tasks = db.query(models.Task).filter(models.Task.assignee_id == self.user.id).all()
        db.close()
        
        columns = ("id", "title", "project", "status", "deadline")
        self.ttree = ttk.Treeview(self.tab_tasks, columns=columns, show="headings", height=10)
        self.ttree.heading("id", text="ID")
        self.ttree.column("id", width=40, anchor="center")
        self.ttree.heading("title", text="Задача")
        self.ttree.column("title", width=250)
        self.ttree.heading("project", text="Проект ID")
        self.ttree.column("project", width=80, anchor="center")
        self.ttree.heading("status", text="Статус")
        self.ttree.column("status", width=100, anchor="center")
        self.ttree.heading("deadline", text="Дедлайн")
        self.ttree.column("deadline", width=100, anchor="center")

        for t in tasks:
            self.ttree.insert("", "end", values=(t.id, t.title, t.project_id, t.status, t.deadline))
            
        self.ttree.pack(fill="both", expand=True, padx=10, pady=10)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ИС Проектов - Десктопная версия (Python UI)")
        self.geometry("800x600")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.login_frame = LoginFrame(self, self.show_dashboard)
        self.dashboard_frame = None

        self.show_login()

    def show_login(self):
        if self.dashboard_frame:
            self.dashboard_frame.destroy()
        self.login_frame = LoginFrame(self, self.show_dashboard)
        self.login_frame.grid(row=0, column=0, sticky="nsew", padx=200, pady=100)

    def show_dashboard(self, user):
        self.login_frame.destroy()
        self.dashboard_frame = DashboardFrame(self, user, self.show_login)
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")

if __name__ == "__main__":
    app = App()
    app.mainloop()
