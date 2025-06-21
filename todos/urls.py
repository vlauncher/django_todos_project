from django.urls import path, include
from rest_framework.routers import DefaultRouter
from todos.views import TodoViewSet

router = DefaultRouter()
router.register(r'todos', TodoViewSet, basename='todo')

urlpatterns = [
    path('', include(router.urls))
]