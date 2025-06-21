from django.db import transaction
from django.core.cache import cache
from .models import Todo
from .tasks import send_archive_notification_email

def get_todo_cache_key(todo_id, user_id):
    """Generate a cache key for a specific todo."""
    return f"todo_{user_id}_{todo_id}"

def get_user_todos_cache_key(user_id):
    """Generate a cache key for a user's todo list."""
    return f"user_todos_{user_id}"

@transaction.atomic
def create_todo(user, data):
    """Create a new todo with atomic transaction."""
    todo = Todo.objects.create(
        user=user,
        title=data.get('title'),
        description=data.get('description', ''),
        archived=False,
        completed=False
    )
    # Invalidate user todos cache
    cache.delete(get_user_todos_cache_key(user.id))
    return todo

@transaction.atomic
def update_todo(todo, data, partial=False):
    """Update an existing todo with atomic transaction."""
    if partial:
        for field, value in data.items():
            setattr(todo, field, value)
    else:
        todo.title = data.get('title', todo.title)
        todo.description = data.get('description', todo.description)
        todo.archived = data.get('archived', todo.archived)
        todo.completed = data.get('completed', todo.completed)
    todo.save()
    # Update cache for this todo
    cache.set(get_todo_cache_key(todo.id, todo.user.id), todo, timeout=3600)
    # Invalidate user todos cache
    cache.delete(get_user_todos_cache_key(todo.user.id))
    return todo

@transaction.atomic
def toggle_todo_archive(todo):
    """Toggle the archive status of a todo."""
    todo.archived = not todo.archived
    todo.save()
    if todo.archived:
        # Trigger async email notification
        send_archive_notification_email.delay(todo.user.email, todo.title)
    # Update cache for this todo
    cache.set(get_todo_cache_key(todo.id, todo.user.id), todo, timeout=3600)
    # Invalidate user todos cache
    cache.delete(get_user_todos_cache_key(todo.user.id))
    return todo

@transaction.atomic
def toggle_todo_complete(todo):
    """Toggle the completion status of a todo."""
    todo.completed = not todo.completed
    todo.save()
    # Update cache for this todo
    cache.set(get_todo_cache_key(todo.id, todo.user.id), todo, timeout=3600)
    # Invalidate user todos cache
    cache.delete(get_user_todos_cache_key(todo.user.id))
    return todo

@transaction.atomic
def delete_todo(todo):
    """Delete a todo with atomic transaction."""
    user_id = todo.user.id
    todo_id = todo.id
    todo.delete()
    # Delete todo cache
    cache.delete(get_todo_cache_key(todo_id, user_id))
    # Invalidate user todos cache
    cache.delete(get_user_todos_cache_key(user_id))

def get_todo_by_id(todo_id, user_id):
    """Retrieve a todo by ID, using cache if available."""
    cache_key = get_todo_cache_key(todo_id, user_id)
    todo = cache.get(cache_key)
    if not todo:
        try:
            todo = Todo.objects.get(id=todo_id, user_id=user_id)
            cache.set(cache_key, todo, timeout=3600)
        except Todo.DoesNotExist:
            return None
    return todo

def get_user_todos(user_id):
    """Retrieve all todos for a user, using cache if available."""
    cache_key = get_user_todos_cache_key(user_id)
    todos = cache.get(cache_key)
    if not todos:
        todos = Todo.objects.filter(user_id=user_id)
        cache.set(cache_key, todos, timeout=3600)
    return todos