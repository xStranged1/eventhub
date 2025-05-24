from django.db.models import Sum
from django.test import TestCase
from django.utils import timezone

from app.models import Event, Ticket, User


class TicketLimitUnitTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="pass")
        self.organizer = User.objects.create_user(username="org1", password="pass", is_organizer=True)
        self.event = Event.objects.create(
            title="Evento Test",
            description="Test",
            scheduled_at=timezone.now() + timezone.timedelta(days=2),
            organizer=self.organizer
        )

    def test_user_cannot_purchase_more_than_5_tickets(self):
        """Verifica que un usuario no pueda superar los 5 tickets por evento"""
        # Crear 3 tickets primero
        success, result = Ticket.new(user=self.user, event=self.event, quantity=3, ticket_type="GENERAL")
        self.assertTrue(success, "Initial ticket creation should succeed")
        # Intentar crear 3 más (total = 6)
        success, errors = Ticket.new(user=self.user, event=self.event, quantity=3, ticket_type="GENERAL")
        self.assertFalse(success, "Should fail when exceeding 5 tickets")
        self.assertIn("quantity", errors, "Error should indicate quantity issue")
        self.assertEqual(
            errors["quantity"],
            "No puedes comprar más de 5 entradas por evento.",
            "Error message should match"
        )
        # Verify total tickets
        total_tickets = Ticket.objects.filter(user=self.user, event=self.event).aggregate(total_quantity=Sum('quantity'))['total_quantity']
        self.assertEqual(total_tickets, 3, "Only 3 tickets should be created")