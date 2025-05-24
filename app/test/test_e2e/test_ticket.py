import datetime
from django.utils import timezone
from playwright.sync_api import expect
from app.models import Event, User, Ticket
from app.test.test_e2e.base import BaseE2ETest


class TicketLimitE2ETest(BaseE2ETest):
    """Tests E2E para verificar el límite de tickets por usuario"""

    def setUp(self):
        super().setUp()

        # Crear usuario regular
        self.regular_user = User.objects.create_user(
            username="usuario",
            email="usuario@example.com",
            password="password123",
            is_organizer=False,
        )

        # Crear organizador
        self.organizer = User.objects.create_user(
            username="organizador",
            email="organizador@example.com",
            password="password123",
            is_organizer=True,
        )

        # Crear evento
        event_date = timezone.make_aware(datetime.datetime(2025, 6, 1, 18, 0))
        self.event = Event.objects.create(
            title="Concierto de prueba",
            description="Concierto limitado",
            scheduled_at=event_date,
            organizer=self.organizer,
        )

    def llenar_formulario_pago(self):
        self.page.fill("#card_number", "1234567812345678")
        self.page.fill("#expiry_date", "2025-07")
        self.page.fill("#cvv", "123")
        self.page.fill("#card_name", "Usuario Ejemplo")
        self.page.check("#accept_terms")

    def comprar_ticket(self):
        self.page.goto(f"{self.live_server_url}/ticket/new/{self.event.id}/")
        self.llenar_formulario_pago()

        buy_button = self.page.get_by_role("button", name="Pagar y Comprar")
        expect(buy_button).to_be_visible()
        buy_button.click()

    def test_user_cannot_buy_more_than_5_tickets(self):
        """Verifica que un usuario no puede comprar más de 5 tickets para un mismo evento"""
        self.login_user("usuario", "password123")

        # Comprar los primeros 5 tickets
        for i in range(5):
            self.comprar_ticket()
        # Intentar comprar un 6º ticket
        self.comprar_ticket() 
        # Verificar en la base de datos
        ticket_count = Ticket.objects.filter(user=self.regular_user, event=self.event).count()
        self.assertEqual(ticket_count, 5)
