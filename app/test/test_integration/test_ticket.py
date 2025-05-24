from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from app.models import Event, Ticket
from django.db.models import Sum

User = get_user_model()

class TicketLimitIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.organizer = User.objects.create_user(username="org1", password="pass", is_organizer=True)
        self.event = Event.objects.create(
            title="Evento X",
            description="desc",
            scheduled_at=timezone.now() + timezone.timedelta(days=1),
            organizer=self.organizer
        )

    def test_cannot_purchase_more_than_five_tickets(self):
        """Verifica que un usuario no pueda comprar más de 5 entradas por evento."""
        # Crear 4 tickets inicialmente
        success, _ = Ticket.new(user=self.user, event=self.event, quantity=4, ticket_type="GENERAL")
        self.assertTrue(success, "Initial ticket creation should succeed")

        # Intentar comprar 2 más (total = 6)
        success, result = Ticket.new(user=self.user, event=self.event, quantity=2, ticket_type="GENERAL")
        self.assertFalse(success, "Should fail when exceeding 5 tickets")
        self.assertIn("quantity", result, "Error should indicate quantity issue")
        self.assertEqual(
            result["quantity"],
            "No puedes comprar más de 5 entradas por evento.",
            "Error message should match"
        )

        # Verificar que el total de tickets sigue siendo 4
        total_tickets = Ticket.objects.filter(user=self.user, event=self.event).aggregate(total_quantity=Sum('quantity'))['total_quantity']
        self.assertEqual(total_tickets, 4, "No additional tickets should be created")
    