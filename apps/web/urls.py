from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("accounts/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("resumes/", views.resume_list, name="resumes"),
    path("jobs/", views.jobs, name="jobs"),
    path("jobs/<int:job_id>/", views.job_detail, name="job-detail"),
    path("jobs/<int:job_id>/save/", views.save_job, name="save-job"),
    path("applications/", views.applications, name="applications"),
    path("applications/<int:application_id>/", views.update_application, name="update-application"),
    path("assistant/", views.assistant, name="assistant"),
]
