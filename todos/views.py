from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db import IntegrityError
from .models import Todo
from .serializers import TodoSerializer
from .services import (
    create_todo,
    update_todo,
    toggle_todo_complete,
    toggle_todo_archive,
    delete_todo,
    get_todo_by_id,
    get_user_todos
)

class TodoViewSet(viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return todos for the authenticated user only."""
        return get_user_todos(self.request.user.id)

    def create(self, request, *args, **kwargs):
        """Create a todo for the authenticated user."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            todo = create_todo(request.user, serializer.validated_data)
            serializer = self.get_serializer(todo)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        """List todos for the authenticated user."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific todo if owned by the authenticated user."""
        todo = get_todo_by_id(kwargs.get('pk'), request.user.id)
        if not todo:
            return Response({"detail": "Todo not found or not owned by user"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(todo)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Update a todo if owned by the authenticated user."""
        todo = get_todo_by_id(kwargs.get('pk'), request.user.id)
        if not todo:
            return Response({"detail": "Todo not found or not owned by user"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(data=request.data, partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        todo = update_todo(todo, serializer.validated_data, partial=kwargs.get('partial', False))
        serializer = self.get_serializer(todo)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_complete(self, request, pk=None):
        """Toggle completion status of a todo if owned by the authenticated user."""
        todo = get_todo_by_id(pk, request.user.id)
        if not todo:
            return Response({"detail": "Todo not found or not owned by user"}, status=status.HTTP_404_NOT_FOUND)
        todo = toggle_todo_complete(todo)
        serializer = self.get_serializer(todo)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_archive(self, request, pk=None):
        """Toggle archive status of a todo if owned by the authenticated user."""
        todo = get_todo_by_id(pk, request.user.id)
        if not todo:
            return Response({"detail": "Todo not found or not owned by user"}, status=status.HTTP_404_NOT_FOUND)
        todo = toggle_todo_archive(todo)
        serializer = self.get_serializer(todo)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete a todo if owned by the authenticated user."""
        todo = get_todo_by_id(kwargs.get('pk'), request.user.id)
        if not todo:
            return Response({"detail": "Todo not found or not owned by user"}, status=status.HTTP_404_NOT_FOUND)
        delete_todo(todo)
        return Response(status=status.HTTP_204_NO_CONTENT)