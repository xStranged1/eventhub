import datetime

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import localtime

from app.models import Event, User, Venue


class BaseEventTestCase(TestCase):
    """Clase base con la configuración común para todos los tests de eventos"""

    def setUp(self):
        # Crear un usuario organizador
        self.organizer = User.objects.create_user(
            username="organizador",
            email="organizador@test.com",
            password="password123",
            is_organizer=True,
        )

        # Crear un usuario regular
        self.regular_user = User.objects.create_user(
            username="regular",
            email="regular@test.com",
            password="password123",
            is_organizer=False,
        )

        # Crear algunos eventos de prueba
        self.event1 = Event.objects.create(
            title="Evento 1",
            description="Descripción del evento 1",
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
            organizer=self.organizer,
        )

        self.event2 = Event.objects.create(
            title="Evento 2",
            description="Descripción del evento 2",
            scheduled_at=timezone.now() + datetime.timedelta(days=2),
            organizer=self.organizer,
        )

        # Cliente para hacer peticiones
        self.client = Client()

        # Verificar que el organizador es una instancia válida de User
        self.assertIsInstance(self.organizer, User)

class EventsListViewTest(BaseEventTestCase):
    """Tests para la vista de listado de eventos"""

    def test_events_view_with_login(self):
        """Test que verifica que la vista events funciona cuando el usuario está logueado"""
        # Login con usuario regular
        self.client.login(username="regular", password="password123")

        # Hacer petición a la vista events
        response = self.client.get(reverse("events"))

        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/event/events.html")
        self.assertIn("events", response.context)
        self.assertIn("user_is_organizer", response.context)
        self.assertEqual(len(response.context["events"]), 2)
        self.assertFalse(response.context["user_is_organizer"])

        # Verificar que los eventos están ordenados por fecha
        events = list(response.context["events"])
        self.assertEqual(events[0].id, self.event1.id)  # type: ignore
        self.assertEqual(events[1].id, self.event2.id)  # type: ignore

    def test_events_view_with_organizer_login(self):
        """Test que verifica que la vista events funciona cuando el usuario es organizador"""
        # Login con usuario organizador
        self.client.login(username="organizador", password="password123")

        # Hacer petición a la vista events
        response = self.client.get(reverse("events"))

        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user_is_organizer"])

    def test_events_view_without_login(self):
        """Test que verifica que la vista events redirige a login cuando el usuario no está logueado"""
        # Hacer petición a la vista events sin login
        response = self.client.get(reverse("events"))

        # Verificar que redirecciona al login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].startswith("/accounts/login/"))

class EventDetailViewTest(BaseEventTestCase):
    """Tests para la vista de detalle de un evento"""

    def test_event_detail_view_with_login(self):
        """Test que verifica que la vista event_detail funciona cuando el usuario está logueado"""
        # Login con usuario regular
        self.client.login(username="regular", password="password123")

        # Hacer petición a la vista event_detail
        response = self.client.get(reverse("event_detail", args=[self.event1.id]))  # type: ignore

        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/event/event_detail.html")
        self.assertIn("event", response.context)
        self.assertEqual(response.context["event"].id, self.event1.id)  # type: ignore

    def test_event_detail_view_without_login(self):
        """Test que verifica que la vista event_detail redirige a login cuando el usuario no está logueado"""
        # Hacer petición a la vista event_detail sin login
        response = self.client.get(reverse("event_detail", args=[self.event1.id]))  # type: ignore

        # Verificar que redirecciona al login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].startswith("/accounts/login/"))

    def test_event_detail_view_with_invalid_id(self):
        """Test que verifica que la vista event_detail devuelve 404 cuando el evento no existe"""
        # Login con usuario regular
        self.client.login(username="regular", password="password123")

        # Hacer petición a la vista event_detail con ID inválido
        response = self.client.get(reverse("event_detail", args=[999]))

        # Verificar respuesta
        self.assertEqual(response.status_code, 404)

class EventFormViewTest(BaseEventTestCase):
    """Tests para la vista del formulario de eventos"""

    def test_event_form_view_with_organizer(self):
        """Test que verifica que la vista event_form funciona cuando el usuario es organizador"""
        # Login con usuario organizador
        self.client.login(username="organizador", password="password123")

        # Hacer petición a la vista event_form para crear nuevo evento (id=None)
        response = self.client.get(reverse("event_form"))

        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/event/event_form.html")
        self.assertIn("event", response.context)
        self.assertTrue(response.context["user_is_organizer"])

    def test_event_form_view_with_regular_user(self):
        """Test que verifica que la vista event_form redirige cuando el usuario no es organizador"""
        # Login con usuario regular
        self.client.login(username="regular", password="password123")

        # Hacer petición a la vista event_form
        response = self.client.get(reverse("event_form"))

        # Verificar que redirecciona a events
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("events")) # type: ignore

    def test_event_form_view_without_login(self):
        """Test que verifica que la vista event_form redirige a login cuando el usuario no está logueado"""
        # Hacer petición a la vista event_form sin login
        response = self.client.get(reverse("event_form"))

        # Verificar que redirecciona al login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/")) # type: ignore

    def test_event_form_edit_existing(self):
        """Test que verifica que se puede editar un evento existente"""
        # Login con usuario organizador
        self.client.login(username="organizador", password="password123")

        # Hacer petición a la vista event_form para editar evento existente
        response = self.client.get(reverse("event_edit", args=[self.event1.id])) # type: ignore

        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/event/event_form.html")
        self.assertEqual(response.context["event"].id, self.event1.id) # type: ignore

class EventFormSubmissionTest(BaseEventTestCase):
    """Tests para la creación y edición de eventos mediante POST"""

    def test_event_form_post_create(self):
        """Test que verifica que se puede crear un evento mediante POST con fecha dinámica"""
        # Login con usuario organizador
        self.client.login(username="organizador", password="password123")

        # Crear un venue de prueba
        venue = Venue.objects.create(
            name="Venue de prueba",
            address="Dirección de prueba",
            city="Ciudad de prueba",
            capacity=100,
            contact="Contacto de prueba",
            user=self.organizer
        )

        # Usar una fecha/hora futura
        future_dt = timezone.now() + datetime.timedelta(days=2, hours=3)
        date_str = future_dt.date().isoformat()      # 'YYYY-MM-DD'
        time_str = future_dt.time().strftime("%H:%M")  # 'HH:MM'

        # Datos para el evento
        event_data = {
            "title": "Nuevo Evento",
            "description": "Descripción del nuevo evento",
            "date": date_str,
            "time": time_str,
            "venue": venue.pk,
            "organizer": self.organizer.pk
        }

        # Hacer petición POST a la vista event_form
        response = self.client.post(reverse("event_form"), event_data)

        # Verificar que redirecciona a events
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse("events"))

        # Verificar que se creó el evento
        self.assertTrue(Event.objects.filter(title="Nuevo Evento").exists())
        evento = Event.objects.get(title="Nuevo Evento")

        # La descripción y relaciones
        self.assertEqual(evento.description, "Descripción del nuevo evento")
        self.assertEqual(evento.organizer, self.organizer)
        self.assertEqual(evento.venue, venue)

        # Verificar la fecha y hora programadas
        # Comparamos año, mes, día, hora y minuto con el objeto future_dt
        scheduled = localtime(evento.scheduled_at)
        self.assertEqual(scheduled.date(), future_dt.date())
        self.assertEqual(scheduled.hour, future_dt.hour)
        self.assertEqual(scheduled.minute, future_dt.minute)

    def test_event_form_post_edit(self):
        """Test que verifica que se puede editar un evento existente mediante POST con fecha dinámica"""
        # Login con usuario organizador
        self.client.login(username="organizador", password="password123")

        # Elegimos una nueva fecha/hora basada en timezone.now()
        future_dt = timezone.now() + datetime.timedelta(days=5, hours=4, minutes=15)
        date_str = future_dt.date().isoformat()          # 'YYYY-MM-DD'
        time_str = future_dt.time().strftime("%H:%M")    # 'HH:MM'

        # Datos para actualizar el evento
        updated_data = {
            "id": str(self.event1.id),  # este campo es importante # type: ignore
            "title": "Evento 1 Actualizado",
            "description": "Nueva descripción actualizada",
            "date": date_str,
            "time": time_str,
        }

        # Hacer petición POST para editar el evento
        response = self.client.post(
            reverse("event_edit", args=[self.event1.id]),
            updated_data
        )

        # Verificar que redirecciona a events
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse("events"))

        # Recargar modelo desde BD y verificar cambios
        self.event1.refresh_from_db()
        self.assertEqual(self.event1.title, "Evento 1 Actualizado")
        self.assertEqual(self.event1.description, "Nueva descripción actualizada")

        # Comprobamos scheduled_at usando hora local
        scheduled = localtime(self.event1.scheduled_at)
        self.assertEqual(scheduled.date(), future_dt.date())
        self.assertEqual(scheduled.hour, future_dt.hour)
        self.assertEqual(scheduled.minute, future_dt.minute)

class EventDeleteViewTest(BaseEventTestCase):
    """Tests para la eliminación de eventos"""

    def test_event_delete_with_organizer(self):
        """Test que verifica que un organizador puede eliminar un evento"""
        # Iniciar sesión como organizador
        self.client.login(username="organizador", password="password123")

        # Verificar que el evento existe antes de eliminar
        self.assertTrue(Event.objects.filter(pk=self.event1.id).exists()) # type: ignore

        # Hacer una petición POST para eliminar el evento
        response = self.client.post(reverse("event_delete", args=[self.event1.id])) # type: ignore

        # Verificar que redirecciona a la página de eventos
        self.assertRedirects(response, reverse("events"))

        # Verificar que el evento ya no existe
        self.assertFalse(Event.objects.filter(pk=self.event1.id).exists()) # type: ignore

    def test_event_delete_with_regular_user(self):
        """Test que verifica que un usuario regular no puede eliminar un evento"""
        # Iniciar sesión como usuario regular
        self.client.login(username="regular", password="password123")

        # Verificar que el evento existe antes de intentar eliminarlo
        self.assertTrue(Event.objects.filter(pk=self.event1.id).exists()) # type: ignore

        # Hacer una petición POST para intentar eliminar el evento
        response = self.client.post(reverse("event_delete", args=[self.event1.id])) # type: ignore

        # Verificar que redirecciona a la página de eventos sin eliminar
        self.assertRedirects(response, reverse("events"))

        # Verificar que el evento sigue existiendo
        self.assertTrue(Event.objects.filter(pk=self.event1.id).exists()) # type: ignore

    def test_event_delete_with_get_request(self):
        """Test que verifica que la vista redirecciona si se usa GET en lugar de POST"""
        # Iniciar sesión como organizador
        self.client.login(username="organizador", password="password123")

        # Hacer una petición GET para intentar eliminar el evento
        response = self.client.get(reverse("event_delete", args=[self.event1.id])) # type: ignore

        # Verificar que redirecciona a la página de eventos
        self.assertRedirects(response, reverse("events"))

        # Verificar que el evento sigue existiendo
        self.assertTrue(Event.objects.filter(pk=self.event1.id).exists()) # type: ignore

    def test_event_delete_nonexistent_event(self):
        """Test que verifica el comportamiento al intentar eliminar un evento inexistente"""
        # Iniciar sesión como organizador
        self.client.login(username="organizador", password="password123")

        # ID inexistente
        nonexistent_id = 9999

        # Verificar que el evento con ese ID no existe
        self.assertFalse(Event.objects.filter(pk=nonexistent_id).exists())

        # Hacer una petición POST para eliminar el evento inexistente
        response = self.client.post(reverse("event_delete", args=[nonexistent_id]))

        # Verificar que devuelve error 404
        self.assertEqual(response.status_code, 404)

    def test_event_delete_without_login(self):
        """Test que verifica que la vista redirecciona a login si el usuario no está autenticado"""
        # Verificar que el evento existe antes de intentar eliminarlo
        self.assertTrue(Event.objects.filter(pk=self.event1.id).exists()) # type: ignore

        # Hacer una petición POST sin iniciar sesión
        response = self.client.post(reverse("event_delete", args=[self.event1.id])) # type: ignore

        # Verificar que redirecciona al login
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/")) # type: ignore

        # Verificar que el evento sigue existiendo
        self.assertTrue(Event.objects.filter(pk=self.event1.id).exists()) # type: ignore

class EventFavoriteTest(BaseEventTestCase):
    """Tests para la funcionalidad de marcar eventos como favoritos"""
    
    def test_favorite_event_post(self):
        """Test que verifica que un usuario puede marcar un evento como favorito"""
        # Login con usuario regular
        self.client.login(username="regular", password="password123")

        # Hacer petición POST para marcar el evento como favorito
        response = self.client.post(reverse("event_favorite", args=[self.event1.id])) # type: ignore

        # Verificar que redirecciona a la vista de detalle del evento
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("event_detail", args=[self.event1.id])) # type: ignore

        # Verificar que el evento fue marcado como favorito
        self.assertTrue(self.regular_user.favorite_events.filter(id=self.event1.id).exists()) # type: ignore

class EventFilterIntegrationTest(BaseEventTestCase):
    """Test de integración para la vista event_filter con filtros aplicados"""

    def setUp(self):
        super().setUp()

        # Crear eventos adicionales para probar los filtros
        self.past_event = Event.objects.create(
            title="Evento Pasado",
            description="Este evento ya ocurrió",
            scheduled_at=timezone.now() - datetime.timedelta(days=3),
            organizer=self.organizer,
        )

        self.other_organizer = User.objects.create_user(
            username="otro",
            email="otro@test.com",
            password="password123",
            is_organizer=True,
        )

        self.other_event = Event.objects.create(
            title="Evento de otro organizador",
            description="Evento creado por otra persona",
            scheduled_at=timezone.now() + datetime.timedelta(days=4),
            organizer=self.other_organizer,
        )

    def test_filter_my_events(self):
        """Filtrar solo los eventos creados por el usuario logueado"""
        self.client.login(username="organizador", password="password123")
        response = self.client.get(reverse("event_filter"), {"my_events": True})

        self.assertEqual(response.status_code, 200)
        events = response.context["events"]
        for event in events:
            self.assertEqual(event.organizer, self.organizer)

    def test_search_filter(self):
        """Buscar eventos por texto"""
        self.client.login(username="organizador", password="password123")
        response = self.client.get(reverse("event_filter"), {"search": "Evento 1"})

        self.assertEqual(response.status_code, 200)
        events = response.context["events"]
        self.assertIn(self.event1, events)
        self.assertNotIn(self.event2, events)

    def test_combined_filters(self):
        """Aplicar múltiples filtros simultáneamente"""
        self.client.login(username="organizador", password="password123")
        response = self.client.get(
            reverse("event_filter"), {"my_events": True, "search": "Evento 1"}
        )

        self.assertEqual(response.status_code, 200)
        events = response.context["events"]

        self.assertIn(self.event1, events)
        for event in events:
            self.assertEqual(event.organizer, self.organizer)

    def test_no_filters_returns_all_future(self):
        """Sin filtros aplicados, retorna eventos futuros"""
        self.client.login(username="regular", password="password123")
        response = self.client.get(reverse("event_filter"))

        self.assertEqual(response.status_code, 200)
        events = response.context["events"]
        self.assertIn(self.event1, events)
        self.assertIn(self.event2, events)
        self.assertIn(self.other_event, events)
        self.assertNotIn(self.past_event, events)
