# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_archive_notification_email(user_email, todo_title):
    subject = f'Todo "{todo_title}" Archived'
    message = f'Your todo "{todo_title}" has been archived successfully.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )