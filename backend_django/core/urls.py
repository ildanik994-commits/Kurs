from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('projects/', views.list_projects, name='projects'),
    path('workspace/', views.employee_workspace, name='workspace'),
    path('projects/gantt/', views.gantt_chart, name='gantt_chart'),
    path('projects/new/', views.new_project, name='new_project'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/message/', views.project_message, name='project_message'),
    path('projects/<int:project_id>/upload/', views.upload_document, name='upload_document'),
    path('documents/<int:doc_id>/download/', views.download_doc, name='download_doc'),
    path('tasks/', views.list_tasks, name='tasks'),
    path('tasks/kanban/', views.kanban_board, name='kanban_board'),
    path('tasks/new/', views.new_task, name='new_task'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('api/tasks/<int:task_id>/update-status/', views.update_task_status_api, name='update_task_status_api'),
    path('users/', views.list_users, name='users'),
    path('leads/', views.list_leads, name='leads'),
    path('leads/new/', views.new_lead, name='new_lead'),
    path('leads/<int:lead_id>/approve/', views.approve_lead, name='approve_lead'),
    path('leads/<int:lead_id>/reject/', views.reject_lead, name='reject_lead'),
    path('notifications/', views.notifications_page, name='notifications'),
    path('api/notifications/count/', views.notif_count, name='notif_count'),
    path('projects/<int:project_id>/export/excel/', views.export_excel, name='export_excel'),
    path('projects/<int:project_id>/export/word/', views.export_word, name='export_word'),
    path('api/1c/sync-employees/', views.sync_employees_1c, name='sync_employees_1c'),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
