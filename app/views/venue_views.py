
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from app.models import Venue


@login_required
def venue_form(request, id=None):
    user = request.user

    if not user.is_organizer:
        return redirect("events")

    venues = Venue.get_venues_by_user(user)
    venue = {}

    if request.method == "POST":
        venue_id = request.POST.get("id")
        name = request.POST.get("name")
        address = request.POST.get("address")
        city = request.POST.get("city")
        capacity = int(request.POST.get("capacity"))
        contact = request.POST.get("contact")
        if venue_id is None:
            success, data = Venue.new(name, address, city, capacity, contact, user)
            if not success: 
                return render(
                    request,
                    "app/venue/venue_form.html",
                    {
                        "errors": data,
                        "venue": venue, 
                        "user_is_organizer": request.user.is_organizer, 
                        "venues": venues
                    },
                )
        else:
            venue = get_object_or_404(Venue, pk=venue_id)
            venue.update(name, address, city, capacity, contact, user)
        return redirect("venues")

    venue = {}
    if id is not None:
        venue = get_object_or_404(Venue, pk=id)

    venues = Venue.get_venues_by_user(user)
    return render(
        request,
        "app/venue/venue_form.html",
        {
            "venue": venue, 
            "user_is_organizer": request.user.is_organizer, 
            "venues": venues
        },
    )

@login_required
def venues(request):
    user = request.user
    if not user.is_organizer:
        return redirect("events")
    venues = Venue.get_venues_by_user(user)

    return render(
        request,
        "app/venue/venues.html",
        {"venues": venues},
    )

@login_required
def venue_detail(request, id):
    venue = get_object_or_404(Venue, pk=id)
    return render(request, "app/venue/venue_detail.html", {"venue": venue, "user_is_organizer": request.user.is_organizer})

@login_required
def venue_delete(request, id):
    user = request.user
    if not user.is_organizer:
        return redirect("venues")

    if request.method == "POST":
        event = get_object_or_404(Venue, pk=id)
        event.delete()
        return redirect("venues")

    return redirect("events")