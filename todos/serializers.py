from rest_framework import serializers
from .models import Todo

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['id', 'title', 'description', 'archived', 'completed']
        read_only_fields = ['id']

    def validate_title(self, value):
        """Validate title length and uniqueness"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long")
        if Todo.objects.filter(title__iexact=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("A todo with this title already exists")
        return value

    def validate_description(self, value):
        """Validate description content"""
        if not value.strip():
            raise serializers.ValidationError("Description cannot be empty")
        return value

    def validate(self, data):
        """Cross-field validation"""
        if data.get('archived') and not data.get('completed'):
            raise serializers.ValidationError({
                'archived': 'Cannot archive an incomplete todo'
            })
        return data