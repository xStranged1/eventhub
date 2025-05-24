from .models import Notification


def notification_icon(request):
    unread_count = 0  # Definimos por defecto
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(addressee=request.user, is_read=False).count()
        icon = f'<i class="bi bi-bell{"-fill text-danger" if unread_count > 0 else ""}"></i>'
    else:
        icon = '<i class="bi bi-bell"></i>'
    return {'icon': icon, 'unread_count': unread_count}
