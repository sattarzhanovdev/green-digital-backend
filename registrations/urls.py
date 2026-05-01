from django.urls import path

from . import views

urlpatterns = [
    path("registrations/", views.create_registration),
    path("admin/login/", views.admin_login),
    path("admin/dashboard/", views.dashboard),
    path("admin/registrations/", views.AdminRegistrationsView.as_view()),
    path("admin/registrations/<int:pk>/", views.AdminRegistrationDetailView.as_view()),
    path("admin/export/csv/", views.export_csv),
]
