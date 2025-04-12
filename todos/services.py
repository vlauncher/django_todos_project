# services.py
from django.db import transaction
from .models import Todo
from django.core.cache import cache
from .tasks import send_archive_notification_email

class TodoService:
    CACHE_TIMEOUT = 60 * 60  # 1 hour

    @staticmethod
    @transaction.atomic
    def create_todo(validated_data):
        """Create a new todo with transaction"""
        todo = Todo.objects.create(**validated_data)
        # Invalidate cache
        cache.delete(f'todo_list_{todo.user.id}')
        return todo

    @staticmethod
    @transaction.atomic
    def update_todo(instance, validated_data):
        """Update todo with transaction"""
        was_archived = instance.archived
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Trigger email if newly archived
        if not was_archived and instance.archived:
            send_archive_notification_email.delay(
                instance.user.email,
                instance.title
            )
        
        # Invalidate cache
        cache.delete(f'todo_{instance.id}')
        cache.delete(f'todo_list_{instance.user.id}')
        return instance

    @staticmethod
    @transaction.atomic
    def delete_todo(instance):
        """Delete todo with transaction"""
        user_id = instance.user.id
        todo_id = instance.id
        instance.delete()
        # Invalidate cache
        cache.delete(f'todo_{todo_id}')
        cache.delete(f'todo_list_{user_id}')

    @staticmethod
    @transaction.atomic
    def toggle_complete(instance):
        """Toggle completion status with transaction"""
        instance.completed = not instance.completed
        instance.save()
        # Invalidate cache
        cache.delete(f'todo_{instance.id}')
        cache.delete(f'todo_list_{instance.user.id}')
        return instance

    @staticmethod
    @transaction.atomic
    def toggle_archive(instance):
        """Toggle archive status with transaction"""
        was_archived = instance.archived
        instance.archived = not instance.archived
        instance.save()
        
        # Trigger email if newly archived
        if not was_archived and instance.archived:
            send_archive_notification_email.delay(
                instance.user.email,
                instance.title
            )
        
        # Invalidate cache
        cache.delete(f'todo_{instance.id}')
        cache.delete(f'todo_list_{instance.user.id}')
        return instance

    @staticmethod
    def get_cached_todo(todo_id):
        """Get todo from cache or database"""
        cache_key = f'todo_{todo_id}'
        todo = cache.get(cache_key)
        if not todo:
            todo = Todo.objects.get(id=todo_id)
            cache.set(cache_key, todo, TodoService.CACHE_TIMEOUT)
        return todo

    @staticmethod
    def get_cached_todo_list(user_id):
        """Get todo list from cache or database"""
        cache_key = f'todo_list_{user_id}'
        todos = cache.get(cache_key)
        if not todos:
            todos = Todo.objects.filter(user_id=user_id)
            cache.set(cache_key, todos, TodoService.CACHE_TIMEOUT)
        return todos