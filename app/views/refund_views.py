from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from app.models import Refund, Ticket


@login_required
def refund_create(request):
    user = request.user
    user_tickets = Ticket.objects.filter(user=user)

    if request.method == "POST":
        ticket_code = request.POST.get("ticket_code")
        reason      = request.POST.get("reason", "").strip()
        errors = []

        # Usuario no puede tener otra solicitud activa
        if Refund.objects.filter(user=user, approved__isnull=True).exists():
            errors.append("Ya tienes una solicitud de reembolso pendiente o en proceso.")

        # El ticket debe existir y pertenecer al usuario
        ticket = Ticket.objects.filter(user=user, ticket_code=ticket_code).first()
        if not ticket:
            errors.append("Código de ticket inválido.")
        else:
            # No haber solicitado reembolso ya para este ticket
            if Refund.objects.filter(user=user, ticket_code=ticket_code).exists():
                errors.append("Ya existe una solicitud de reembolso para este ticket.")

        # Si hay errores, re-renderiza el formulario con todos ellos
        if errors:
            return render(request, "app/refund/refund_form.html", {
                "user_tickets":  user_tickets,
                "errors":        errors,
                "selected_code": ticket_code,
                "reason":        reason,
            })

        Refund.objects.create(
            ticket_code=ticket.ticket_code,
            reason=reason,
            user=user,
            event=ticket.event
        )
        return redirect("my_refunds")

    # GET: formulario vacío
    return render(request, "app/refund/refund_form.html", {
        "user_tickets": user_tickets
    })

@login_required
def my_refunds(request):
    refunds = Refund.objects.filter(user=request.user).order_by("-created_at")
    codes = {r.ticket_code for r in refunds}
    tickets = Ticket.objects.filter(ticket_code__in=codes)
    tickets_map = {t.ticket_code: t for t in tickets}
    return render(request, "app/refund/my_refunds.html", {"refunds": refunds, "tickets_map": tickets_map})

@login_required
def refund_edit(request, id):
     user = request.user
     user_tickets = Ticket.objects.filter(user=user)
     refund_obj = get_object_or_404(Refund, id=id, user=user)

     # Solo editar si está pendiente
     if refund_obj.approved is not None:
         return redirect("my_refunds")

     errors = []
     if request.method == "POST":
         ticket_code = request.POST.get("ticket_code")
         reason = request.POST.get("reason", "").strip()

         # Validaciones
         if not ticket_code:
             errors.append("Selecciona un ticket.")
         else:
            if Refund.objects.filter(user=user, ticket_code=ticket_code).exists():
             errors.append("Ya existe una solicitud de reembolso para este ticket.")

         if not reason:
             errors.append("El motivo es obligatorio.")

         # Verificar ticket propio
         ticket = Ticket.objects.filter(user=user, ticket_code=ticket_code).first()
         if not ticket:
             errors.append("Código de ticket inválido.")

         # Si no hay errores, guardar cambios
         if not errors:
             refund_obj.ticket_code = ticket_code
             refund_obj.reason = reason
             refund_obj.save()
             return redirect("my_refunds")

     # GET o errores
     return render(request, "app/refund/refund_form.html", {
         "user_tickets": user_tickets,
         "refund": refund_obj,
         "errors": errors,
         "selected_code": refund_obj.ticket_code,
         "reason": refund_obj.reason,
     })

@login_required
def refund_delete(request, id):
    refund_obj = get_object_or_404(Refund, id=id, user=request.user)
    if not refund_obj.approved:  # Ya la vio un organizer
        refund_obj.delete()

    return redirect("my_refunds")



# ORGANIZER

def is_organizer(user):
    return user.is_authenticated and user.is_organizer

@login_required
@require_POST
def approve_refund_request(request, pk):
    if not is_organizer(request.user):
        messages.error(request, "No tienes permisos para aprobar reembolsos.")
        return redirect('refunds_admin')

    refund_obj = get_object_or_404(Refund, pk=pk)
    if refund_obj.approved is None:  # Verifica si es pendiente
        refund_obj.approved = True
        refund_obj.aproval_date = timezone.now()
        refund_obj.save()
        messages.success(request, "Reembolso aprobado exitosamente.")
    return redirect('refunds_admin')

@login_required
@require_POST
def reject_refund_request(request, pk):
    if not is_organizer(request.user):
        messages.error(request, "No tienes permisos para rechazar reembolsos.")
        return redirect('refunds_admin')

    refund_obj = get_object_or_404(Refund, pk=pk)
    if refund_obj.approved is None:  # Verifica si es pendiente
        refund_obj.approved = False
        refund_obj.aproval_date = timezone.now()
        refund_obj.save()
        messages.success(request, "Reembolso rechazado exitosamente.")
    return redirect('refunds_admin')
# views.py
@login_required
def refund_requests_admin(request):
    user = request.user
    if not is_organizer(user):
        return redirect("events")
    refunds = Refund.objects.filter(event__organizer=user).order_by("-created_at")
    codes = {r.ticket_code for r in refunds}
    tickets = Ticket.objects.filter(ticket_code__in=codes)
    tickets_map = {t.ticket_code: t for t in tickets}

    # Agregar información adicional para el template
    context = {
        "refund_requests": refunds,
        "pending_count": refunds.filter(approved__isnull=True).count(),
        "approved_count": refunds.filter(approved=True).count(),
        "rejected_count": refunds.filter(approved=False).count(),
        "tickets_map": tickets_map,
    }

    return render(request, "app/refund/refund_request_admin.html", 
        context
    )