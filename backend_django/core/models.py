import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser

# === Tables for Lookups (Dictionaries) ===

class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name

class ProjectStatus(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name

class TaskStatus(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name

class DocumentType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name

class BudgetCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name

# === Main Tables ===

class User(AbstractUser):
    # overrides abstract user fields where necessary
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    avatar_url = models.CharField(max_length=1000, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    
    def __str__(self):
        return self.username

class Project(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    status = models.ForeignKey(ProjectStatus, on_delete=models.SET_NULL, null=True, related_name="projects")
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    planned_budget = models.FloatField(default=0.0)
    actual_cost = models.FloatField(default=0.0)
    
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="projects_as_customer")
    pm = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="projects_as_pm")
    
    def __str__(self):
        return self.title

class ProjectStage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="stages")
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.project.title} - {self.name}"

class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    stage = models.ForeignKey(ProjectStage, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    status = models.ForeignKey(TaskStatus, on_delete=models.SET_NULL, null=True, related_name="tasks")
    deadline = models.DateField(blank=True, null=True)
    cost = models.FloatField(default=0.0)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")

    def __str__(self):
        return self.title

class WorkLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="work_logs")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="work_logs")
    hours = models.FloatField()
    log_date = models.DateField(default=datetime.date.today)

class Document(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=255)
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True, related_name="documents")
    file_path = models.FileField(upload_to="documents/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="authored_documents")

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class ProjectMessage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField()
    is_revision = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class ProjectBudgetItem(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="budget_items")
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE, related_name="budget_items")
    planned_amount = models.FloatField(default=0.0)
    actual_amount = models.FloatField(default=0.0)

class TaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="history")
    old_status = models.ForeignKey(TaskStatus, on_delete=models.SET_NULL, null=True, related_name="+")
    new_status = models.ForeignKey(TaskStatus, on_delete=models.SET_NULL, null=True, related_name="+")
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="history_changes")
    changed_at = models.DateTimeField(auto_now_add=True)

class Lead(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    budget = models.FloatField(default=0.0)
    desired_deadline = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=255, default="Новая")
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leads")
    tz_file_path = models.FileField(upload_to="leads_tz/", blank=True, null=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class SystemLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="system_logs")
    action = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
