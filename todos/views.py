# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Todo
from .serializers import TodoSerializer
from .services import TodoService
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter todos based on query params and user"""
        todos = TodoService.get_cached_todo_list(self.request.user.id)
        if self.request.query_params.get('completed'):
            completed = self.request.query_params.get('completed').lower() == 'true'
            todos = todos.filter(completed=completed)
        if self.request.query_params.get('archived'):
            archived = self.request.query_params.get('archived').lower() == 'true'
            todos = todos.filter(archived=archived)
        return todos

    def create(self, request, *args, **kwargs):
        """Create a new todo"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            validated_data['user'] = request.user
            todo = TodoService.create_todo(validated_data)
            serializer = self.get_serializer(todo)
            return Response({
                'status': 'success',
                'message': 'Todo created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'error',
            'message': 'Failed to create todo',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Update todo"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            todo = TodoService.update_todo(instance, serializer.validated_data)
            serializer = self.get_serializer(todo)
            return Response({
                'status': 'success',
                'message': 'Todo updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'status': 'error',
            'message': 'Failed to update todo',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """Delete todo"""
        instance = self.get_object()
        TodoService.delete_todo(instance)
        return Response({
            'status': 'success',
            'message': 'Todo deleted successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def toggle_complete(self, request, pk=None):
        """Custom action to toggle completion status"""
        todo = self.get_object()
        todo = TodoService.toggle_complete(todo)
        serializer = self.get_serializer(todo)
        return Response({
            'status': 'success',
            'message': f'Todo marked as {"completed" if todo.completed else "incomplete"}',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def toggle_archive(self, request, pk=None):
        """Custom action to toggle archive status"""
        todo = self.get_object()
        todo = TodoService.toggle_archive(todo)
        serializer = self.get_serializer(todo)
        return Response({
            'status': 'success',
            'message': f'Todo {"archived" if todo.archived else "unarchived"} successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """List todos with custom response format"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'message': 'Todos retrieved successfully',
            'count': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve single todo with custom response format"""
        instance = TodoService.get_cached_todo(self.kwargs['pk'])
        serializer = self.get_serializer(instance)
        return Response({
            'status': 'success',
            'message': 'Todo retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)