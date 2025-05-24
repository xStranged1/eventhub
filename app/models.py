from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum
from django.utils.crypto import get_random_string


class User(AbstractUser):
    is_organizer = models.BooleanField(default=False)

    @classmethod
    def validate_new_user(cls, email, username, password, password_confirm):
        errors = {}

        if email is None:
            errors["email"] = "El email es requerido"
        elif User.objects.filter(email=email).exists():
            errors["email"] = "Ya existe un usuario con este email"

        if username is None:
            errors["username"] = "El username es requerido"
        elif User.objects.filter(username=username).exists():
            errors["username"] = "Ya existe un usuario con este nombre de usuario"

        if password is None or password_confirm is None:
            errors["password"] = "Las contraseñas son requeridas"
        elif password != password_confirm:
            errors["password"] = "Las contraseñas no coinciden"

        return errors


class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    is_active = models.BooleanField()

    def __str__(self):
        return self.name
    
    @classmethod
    def validate(cls, name, description, is_active):
        errors = {}

        if name == "":
            errors["name"] = "El nombre de categoría es requerido"

        if description == "":
            errors["description"] = "La descripcion de categoría es requerida"

        if is_active is not None and not isinstance(is_active, bool):
            errors["is_active"] = "is_active debería ser boolean"
        return errors

    @classmethod
    def new(cls, name, description, is_active):
        errors = Category.validate(name, description, is_active)

        if len(errors.keys()) > 0:
            return False, errors

        Category.objects.create(
            name=name,
            description=description,
            is_active=is_active,
        )

        return True, None

    def update(self, name, description, is_active):
        self.name = name or self.name
        self.description = description or self.description
        self.is_active = is_active or self.is_active
        self.save()

class Venue(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    capacity = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='venues')
    contact = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
    @classmethod
    def validate(cls, name, address, city, capacity, contact):
        errors = {}

        if name == "":
            errors["name"] = "El nombre del lugar es requerido"

        if address == "":
            errors["address"] = "La dirección del lugar es requerida"

        if city == "":
            errors["city"] = "La ciudad del lugar es requerida"
        
        if capacity is not None and not isinstance(capacity, int):
            errors["capacity"] = "La capacidad del lugar debe ser numérica"

        if contact == "":
            errors["contact"] = "El contacto del lugar es requerida"
        return errors

    @classmethod
    def new(cls, name, address, city, capacity, contact, user):
        errors = Venue.validate(name, address, city, capacity, contact)

        if len(errors.keys()) > 0:
            return False, errors

        new_venue = Venue.objects.create(
            name=name,
            address=address,
            city=city,
            capacity=capacity,
            contact=contact,
            user=user,
        )
        return True, new_venue

    def update(self, name, address, city, capacity, contact, user): # TO DO: validate this
        self.name = name or self.name
        self.address = address or self.address
        self.city = city or self.city
        self.capacity = capacity or self.capacity
        self.contact = contact or self.contact
        self.user = user or self.user
        self.save()
        return True, None

    @classmethod
    def get_venues_by_user(cls, user):
        return cls.objects.filter(user=user)

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    scheduled_at = models.DateTimeField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='events'
    )
    venue = models.ForeignKey(Venue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @classmethod
    def validate(cls, title, categories, venue, description, scheduled_at):
        errors = {}
        if title == "":
            errors["title"] = "Por favor ingrese un titulo"

        if description == "":
            errors["description"] = "Por favor ingrese una descripcion"

        return errors

    @classmethod
    def new(cls, title, categories, venue, description, scheduled_at, organizer):
        errors = Event.validate(title, categories, venue, description, scheduled_at)

        if len(errors.keys()) > 0:
            return False, errors
        event = Event.objects.create(
            title=title,
            venue=venue,
            description=description,
            scheduled_at=scheduled_at,
            organizer=organizer,
        )
        event.categories.set(categories)
        return True, None
    
    def update(self, title, categories, venue, description, scheduled_at, organizer):
        self.title = title or self.title
        self.description = description or self.description
        self.venue = venue or self.venue
        self.scheduled_at = scheduled_at or self.scheduled_at
        self.organizer = organizer or self.organizer

        if categories is not None:
            if isinstance(categories, models.Manager):
                raise ValueError("Error updating event.categories")
            self.save()
            self.categories.set(categories)

        self.save()

class Refund(models.Model):
    approved = models.BooleanField(default=None, null=True, blank=True)
    aproval_date = models.DateTimeField(null=True, blank=True)
    ticket_code = models.CharField(max_length=200)
    reason = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="refunded_tickets")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name="refunded_tickets")
    
    class Meta:
        unique_together = ("ticket_code", "user")

    def __str__(self): return self.ticket_code
    
class Comment(models.Model):
    # Estas variables son de relacion
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="comments")
    
    # Estas variables son de contenido que pidio el profesor
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    title=models.CharField(max_length=300)
    text=models.TextField()
    rating=models.IntegerField()
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.title} {self.text}({self.rating})'

    
class Ticket(models.Model):
    TICKET_TYPES = [
        ("GENERAL", "General"),
        ("VIP",     "VIP"),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    event = models.ForeignKey("app.Event", on_delete=models.CASCADE, related_name="tickets")
    
    buy_date    = models.DateField(auto_now_add=True)
    ticket_code = models.CharField(max_length=12, unique=True, editable=False)
    quantity    = models.PositiveIntegerField()
    type        = models.CharField(max_length=10, choices=TICKET_TYPES)

    def save(self, *args, **kwargs):
        if not self.ticket_code:
            self.ticket_code = get_random_string(length=12)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_code} - {self.user.username} - {self.event.title}"

    @classmethod
    def validate(cls, user, event, quantity, ticket_type):
        errors = {}
        if not isinstance(quantity, int) or quantity < 1:
            errors["quantity"] = "La cantidad debe ser un entero mayor o igual a 1."
        if ticket_type not in dict(cls.TICKET_TYPES):
            errors["type"] = "El tipo de ticket no es válido."
        # Check total tickets per user per event
        existing_tickets = Ticket.objects.filter(user=user, event=event).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
        if existing_tickets + quantity > 5:
            errors["quantity"] = "No puedes comprar más de 5 entradas por evento."
        return errors

    @classmethod
    def new(cls, user, event, quantity, ticket_type):
        errors = cls.validate(user, event, quantity, ticket_type)
        if errors:
            return False, errors
        ticket = cls.objects.create(
            user=user,
            event=event,
            quantity=quantity,
            type=ticket_type
        )
        return True, ticket
    
    @classmethod
    def update(self, quantity=None, ticket_type=None):
        # Si no se pasa un parámetro, se mantiene el valor actual
        new_qty  = quantity    if quantity is not None    else self.quantity
        new_type = ticket_type if ticket_type is not None else self.type

        errors = self.validate(self.user, self.event, new_qty, new_type)
        if errors:
            return False, errors

        self.quantity = new_qty
        self.type     = new_type
        self.save()
        return True, None

class Notification(models.Model):
    title=models.CharField(max_length=200)
    massage=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='notifications')
    addressee=models.ManyToManyField(User)

    prioridadOpciones=[    
        ('High', 'HIGH'),
        ('Medium', 'MEDIUM'),
        ('Low', 'LOW'),
        ]
    
    Priority=models.CharField(choices=prioridadOpciones, default='Medium')
    is_read=models.BooleanField(default=False)