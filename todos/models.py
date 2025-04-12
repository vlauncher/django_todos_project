from django.db import models
from users.models import User

# Create your models here.

class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    archived = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Todos"
        ordering = ["completed", "title"]
        db_table = "todos"