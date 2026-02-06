from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Creating a router for our new API ViewSets
router = DefaultRouter()
router.register(r'lessons', views.LessonViewSet)
router.register(r'words', views.WordViewSet)

urlpatterns = [

    path("", views.base, name="base"),
    path("ping/", views.ping, name="ping"),

    # --- New API URLs ---
    # This includes all routes for lessons and words (GET, POST, etc.)
    path("api/", include(router.urls)),
]