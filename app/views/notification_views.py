
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from app.form import NotificationForm
from app.models import Event, Notification, User


@login_required
def notification_list(request):
    notifications = Notification.objects.all()
    events = Event.objects.all()
    user= request.user

    search_query = request.GET.get('search', '').strip()
    event_id = request.GET.get('event')
    priority = request.GET.get('priority')


    # Filtrar por búsqueda (asumiendo que buscás en el título o contenido)
    if search_query:
        notifications = notifications.filter(Q(title__icontains=search_query))

    if event_id:
        notifications = notifications.filter(event__id=event_id)

    if priority:
        notifications = notifications.filter(Priority=priority)


    if user.is_organizer:
        return render(request, 'app/notification/list.html', {'notifications': notifications,'events': events})
    else:
        notifications = Notification.objects.filter(addressee=request.user).order_by('-created_at')
        unread_count = Notification.objects.filter(addressee=request.user, is_read=False).count()
        return render(request, 'app/notification/bandejaEntrada.html', {'notifications': notifications, 'unread_count': unread_count })


@login_required
def notification_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        massage = request.POST.get('massage')
        priority = request.POST.get('priority')
        is_read = request.POST.get('is_read') == 'on'
        recipient = request.POST.get('recipient')
        event_id = request.POST.get('event')
        specific_user=request.POST.get('specific_user')
   
        event=Event.objects.get(id = event_id)

        notification=Notification.objects.create(
            title=title,
            massage=massage,
            created_at=timezone.now().date(), 
            Priority=priority,
            is_read=is_read,
            event=event,
        )


        if recipient == 'all':
            addressee_users = User.objects.filter(Ticket__event=event).distinct()
            notification.addressee.set(addressee_users)  
        elif recipient == 'specific':
            try:
                specific_user = User.objects.get(id=specific_user)
                if specific_user.is_organizer:
                     # Manejar el caso en que el usuario específico es admin (no se envian notificaciones a admins)
                    eventos = Event.objects.all()
                    users = User.objects.all()
                    return render(request, 'app/notification/create.html', {'eventos': eventos, 'users': users, 'error': 'El usuario específico es administrador.'})
                else:
                    notification.addressee.set([specific_user]) 
            except User.DoesNotExist:
                # Manejar el caso en que el usuario específico no existe
                eventos = Event.objects.all()
                users = User.objects.all()
                return render(request, 'app/notification/create.html', {'eventos': eventos, 'users': users, 'error': 'El usuario específico no existe.'})


        return redirect('/notification/')  
    
    eventos= Event.objects.all()
    users = User.objects.all()
    
    return render(request, 'app/notification/create.html', {'eventos': eventos, 'users': users})

@login_required
def notification_detail(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    return render(request, 'app/notification/detail.html', {'notification': notification})

@login_required
def notification_edit(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    if request.method == 'POST':
        form = NotificationForm(request.POST, instance=notification)
        if form.is_valid():
            form.save()
            return redirect('/notification/')
    else:
        form = NotificationForm(instance=notification)
    return render(request, 'app/notification/edit.html', {'form': form})

@login_required
def notification_delete(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    if request.method == 'POST':
        notification.delete()
        return redirect('/notification/')
    return render(request, 'app/notification/delete_confirm.html', {'notification': notification})


@login_required
def notification_mark_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    if request.method == 'POST':
        notification.is_read = True
        notification.save()
        return redirect('/notification/')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/')) # refresh last screen

@login_required
def notification_mark_all_as_read(request):
    if request.method == 'GET':
        Notification.objects.filter(addressee=request.user, is_read=False).update(is_read=True)
        return redirect('/notification/')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/')) # refresh last screen
