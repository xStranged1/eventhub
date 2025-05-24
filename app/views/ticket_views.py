from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from ..models import Event, Ticket


@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(user=request.user).order_by('-buy_date')
    return render(request, "app/ticket/my_tickets.html", {"tickets": tickets})


@login_required
def ticket_delete(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    user = request.user

    # Solo el dueño o el organizador del evento pueden eliminar
    if ticket.user == user or (user.is_organizer and ticket.event.organizer == user):
        if request.method == "POST":
            ticket.delete()
    return redirect("my_tickets")


@login_required
def purchase_ticket(request, event_id):
    """
    Vista para crear un nuevo Ticket usando Ticket.new()
    """
    user = request.user
    if user.is_organizer:
        return redirect("event_detail", id=event_id)

    event = get_object_or_404(Event, pk=event_id)

    if request.method == "POST":
        qty   = int(request.POST.get("quantity", 1))
        ttype = request.POST.get("type", "GENERAL")
        existing_qty = Ticket.objects.filter(user=user, event=event).aggregate(total=Sum('quantity'))['total'] or 0
        if existing_qty + qty > 5:
            return render(request, "app/ticket/purchase_ticket.html", {
                "event": event,
                "errors": {"quantity": "No podes comprar más de 5 tickets para un mismo evento"},
                "ticket_types": dict(Ticket.TICKET_TYPES).keys()
            })
        success, result = Ticket.new(user, event, qty, ttype)
        if not success:
            # result es un dict de errores
            return render(request, "app/ticket/purchase_ticket.html", {
                "event": event,
                "errors": result,
                "ticket_types": dict(Ticket.TICKET_TYPES).keys()
            })
        return redirect("my_tickets")

    return render(request, "app/ticket/purchase_ticket.html", {
        "event": event,
        "ticket_types": dict(Ticket.TICKET_TYPES).keys()
    })


@login_required
def edit_ticket(request, ticket_id):
    """
    Vista para editar un Ticket existente usando ticket.update()
    """
    ticket = get_object_or_404(Ticket, pk=ticket_id, user=request.user)

    if request.method == "POST":
        qty   = int(request.POST.get("quantity", ticket.quantity))
        ttype = request.POST.get("type", ticket.type)
        success, errors = ticket.update(qty, ttype)
        if not success:
            return render(request, "app/ticket/purchase_ticket.html", {
                "ticket": ticket,
                "event": ticket.event,
                "errors": errors,
                "ticket_types": dict(Ticket.TICKET_TYPES).keys()
            })
        return redirect("my_tickets")

    return render(request, "app/ticket/purchase_ticket.html", {
        "ticket": ticket,
        "event": ticket.event,
        "ticket_types": dict(Ticket.TICKET_TYPES).keys()
    })


@login_required
def event_tickets(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    # Asegúrate que solo el organizador puede ver los tickets
    if request.user != event.organizer:
        return redirect("events")

    tickets = Ticket.objects.filter(event=event).order_by('-buy_date')
    return render(request, "app/ticket/event_tickets.html", {
        "event": event,
        "tickets": tickets
    })

@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    user = request.user

    # Sólo el dueño o el organizador del evento pueden verlo
    if ticket.user != user and not (user.is_organizer and ticket.event.organizer == user):
        return redirect("my_tickets")

    return render(request, "app/ticket/ticket_detail.html", {
        "ticket": ticket,
        "user_is_organizer": user.is_organizer,
    })