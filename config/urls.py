"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django_admin_workflow.views import WorkflowPageView

admin.sites.site.index_title = "Accueil"
admin.sites.site.site_title = "Django workflow"
admin.sites.site.site_header = "Workflow pour Django"

urlpatterns = [
    path("workflow/", WorkflowPageView.as_view(),
         {'workflow':"apptest/workflow.toml"}, name='workflow'),
    path('', admin.site.urls),
]
