from django.db import models
from django.contrib.auth.models import AbstractUser

def validate_event(data):
    errors = {}

    title = data.get("title", "")
    description = data.get("description", "")

    if title == "":
        errors["title"] = "Por favor ingrese un titulo"

    if description == "":
        errors["description"] = "Por favor ingrese una descripcion"

    return errors

class User(AbstractUser):
    is_organizer = models.BooleanField(default=False)

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @classmethod
    def save_event(cls, event_data):
        errors = validate_event(event_data)

        if len(errors.keys()) > 0:
            return False, errors

        Event.objects.create(
            title=event_data.get("title"),
            description=event_data.get("description"),
            date=event_data.get("date"),
            organizer=event_data.get("organizer"),
        )

        return True, None

    def update_client(self, event_data):
        self.title = event_data.get("title", "") or self.title
        self.description = event_data.get("description", "") or self.description
        self.date = event_data.get("date", "") or self.date
        self.organizer = event_data.get("organizer", "") or self.organizer

        self.save()
