import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from django.http import JsonResponse
from django.shortcuts import render
from core.auth import api_login_required
from rest_framework import viewsets
from .models import Lesson, Word
from .serializers import LessonSerializer, WordSerializer

TEAM_NAME = "team9"



@api_login_required
def ping(request):
    # Standard health check for the core system
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    # Renders the main index page
    return render(request, f"{TEAM_NAME}/index.html")

# --- New REST API ViewSets ---

class LessonViewSet(viewsets.ModelViewSet):
    # Basic CRUD for lessons
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

class WordViewSet(viewsets.ModelViewSet):
    # Basic CRUD for words
    queryset = Word.objects.all()
    serializer_class = WordSerializer