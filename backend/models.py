from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
import datetime
from database import Base

# === Tables for Lookups (Dictionaries) ===

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    users = relationship("User", back_populates="role")

class ProjectStatus(Base):
    __tablename__ = "project_statuses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    projects = relationship("Project", back_populates="status")

class TaskStatus(Base):
    __tablename__ = "task_statuses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    tasks = relationship("Task", back_populates="status")

class DocumentType(Base):
    __tablename__ = "document_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    documents = relationship("Document", back_populates="document_type")

class BudgetCategory(Base):
    __tablename__ = "budget_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    budget_items = relationship("ProjectBudgetItem", back_populates="category")

# === Main Tables ===

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    full_name = Column(String)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    position = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"))

    role = relationship("Role", back_populates="users")
    projects_as_customer = relationship("Project", back_populates="customer", foreign_keys="[Project.customer_id]")
    projects_as_pm = relationship("Project", back_populates="pm", foreign_keys="[Project.pm_id]")
    tasks = relationship("Task", back_populates="assignee")
    work_logs = relationship("WorkLog", back_populates="user")
    authored_documents = relationship("Document", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    notifications = relationship("Notification", back_populates="user")
    system_logs = relationship("SystemLog", back_populates="user")
    leads = relationship("Lead", back_populates="customer")
    history_changes = relationship("TaskHistory", back_populates="changed_by_user")
    sent_messages = relationship("ProjectMessage", foreign_keys="[ProjectMessage.sender_id]", back_populates="sender")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    status_id = Column(Integer, ForeignKey("project_statuses.id"))
    start_date = Column(Date)
    end_date = Column(Date, nullable=True)
    planned_budget = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    customer_id = Column(Integer, ForeignKey("users.id"))
    pm_id = Column(Integer, ForeignKey("users.id"))

    status = relationship("ProjectStatus", back_populates="projects")
    customer = relationship("User", foreign_keys=[customer_id], back_populates="projects_as_customer")
    pm = relationship("User", foreign_keys=[pm_id], back_populates="projects_as_pm")
    stages = relationship("ProjectStage", back_populates="project")
    tasks = relationship("Task", back_populates="project")
    documents = relationship("Document", back_populates="project")
    budget_items = relationship("ProjectBudgetItem", back_populates="project")
    messages = relationship("ProjectMessage", back_populates="project", order_by="ProjectMessage.created_at")

class ProjectStage(Base):
    __tablename__ = "project_stages"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)

    project = relationship("Project", back_populates="stages")
    tasks = relationship("Task", back_populates="stage")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    stage_id = Column(Integer, ForeignKey("project_stages.id"), nullable=True)
    title = Column(String, index=True)
    description = Column(Text)
    status_id = Column(Integer, ForeignKey("task_statuses.id"))
    deadline = Column(Date, nullable=True)
    cost = Column(Float, default=0.0)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    project = relationship("Project", back_populates="tasks")
    stage = relationship("ProjectStage", back_populates="tasks")
    status = relationship("TaskStatus", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks")
    work_logs = relationship("WorkLog", back_populates="task")
    comments = relationship("Comment", back_populates="task")
    history = relationship("TaskHistory", back_populates="task")

class WorkLog(Base):
    __tablename__ = "work_logs"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    hours = Column(Float)
    log_date = Column(Date, default=datetime.date.today)

    task = relationship("Task", back_populates="work_logs")
    user = relationship("User", back_populates="work_logs")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String)
    document_type_id = Column(Integer, ForeignKey("document_types.id"))
    file_path = Column(String, nullable=True)  # path to uploaded file
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    author_id = Column(Integer, ForeignKey("users.id"))

    project = relationship("Project", back_populates="documents")
    document_type = relationship("DocumentType", back_populates="documents")
    author = relationship("User", back_populates="authored_documents")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="comments")

class ProjectMessage(Base):
    """Chat messages within a project — visible to customer, PM and head."""
    __tablename__ = "project_messages"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    is_revision = Column(Boolean, default=False)  # True = revision request from customer
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")

class ProjectBudgetItem(Base):
    __tablename__ = "project_budget_items"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    category_id = Column(Integer, ForeignKey("budget_categories.id"))
    planned_amount = Column(Float, default=0.0)
    actual_amount = Column(Float, default=0.0)

    project = relationship("Project", back_populates="budget_items")
    category = relationship("BudgetCategory", back_populates="budget_items")

class TaskHistory(Base):
    __tablename__ = "task_history"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    old_status_id = Column(Integer, ForeignKey("task_statuses.id"), nullable=True)
    new_status_id = Column(Integer, ForeignKey("task_statuses.id"))
    changed_by = Column(Integer, ForeignKey("users.id"))
    changed_at = Column(DateTime, default=datetime.datetime.utcnow)

    task = relationship("Task", back_populates="history")
    changed_by_user = relationship("User", back_populates="history_changes")

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    budget = Column(Float, default=0.0)
    desired_deadline = Column(Date, nullable=True)
    status = Column(String, default="Новая")
    customer_id = Column(Integer, ForeignKey("users.id"))
    tz_file_path = Column(String, nullable=True)   # attached TZ file

    customer = relationship("User", back_populates="leads")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    link = Column(String, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="notifications")

class SystemLog(Base):
    __tablename__ = "system_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="system_logs")
