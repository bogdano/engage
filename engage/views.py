from .models import Team, Activity, Leaderboard, Item, ActivityType
from accounts.models import CustomUser
from django.db.models import Sum, Prefetch
from django.http import HttpRequest
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import JsonResponse
import cloudinary.uploader


def homepage(request):
    if not request.user.is_authenticated:
        return render(request, "auth/send_login_link.html")
    else:
        activities = Activity.objects.filter(is_approved=True, is_active=True).order_by(
            "event_date"
        )
        return render(request, "home.html", {"activities": activities})


def add_activity(request):
    leaderboards = Leaderboard.objects.all()
    return render(request, "add_activity.html", {"leaderboards": leaderboards})


def new_item(request):
    if request.method == "POST":
        name = request.POST.get("itemName")
        points = request.POST.get("pointCost")
        description = request.POST.get("itemDescription")
        uploaded_image = cloudinary.uploader.upload(request.FILES["photo"])
        uploaded_image_url = uploaded_image["url"]
    item = Item.objects.create(
        name=name, description=description, price=points, image=uploaded_image_url
    )
    item.save()
    items = Item.objects.all()
    return render(request, "store.html", {"items": items})


def add_item(request):
    return render(request, "new_item.html")


def new_activity(request):
    if request.method == "POST":
        title = request.POST.get("title")
        points = request.POST.get("points")
        description = request.POST.get("description")
        creator = request.user
        address = request.POST.get("address")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        event_date = request.POST.get("event_date")
        end_date = request.POST.get("end_date")
        # upload photo to cloudinary and store URL in database
        uploaded_image_url = ""
        if "photo" in request.FILES:
            uploaded_image = cloudinary.uploader.upload(request.FILES["photo"])
            uploaded_image_url = uploaded_image["url"]

        leaderboard_names = request.POST.getlist("leaderboards")
        # Create new Leaderboard instances if necessary
        leaderboards = [
            Leaderboard.objects.get_or_create(pk=pk)[0] for pk in leaderboard_names
        ]

        activity = Activity.objects.create(
            title=title,
            points=points,
            description=description,
            creator=creator,
            address=address,
            latitude=latitude,
            longitude=longitude,
            event_date=event_date,
            end_date=end_date,
            photo=uploaded_image_url,
        )
        # Link the Leaderboard instances to the Activity instance
        activity.leaderboards.add(*leaderboards)
        if request.user.is_staff:
            activity.is_approved = True
            activity.save()
            return render(request, "activity_added.html")
        else:
            return render(request, "activity_pending.html")
    else:
        return JsonResponse({"error": "Invalid request method"})


def activity(request, pk):
    activity = Activity.objects.get(pk=pk)
    return render(request, "activity.html", {"activity": activity})

def activity_leaderboard(request):
    activities = Activity.objects.all()

    # Filter by activity type if 'type' is in request.GET
    activity_type = request.GET.get('type')
    if activity_type:
        activities = activities.filter(activity_type__name=activity_type)

    # Example of filtering activities from the last 30 days
    start_date = request.GET.get('start_date')
    if start_date:
        # Assuming 'start_date' is in YYYY-MM-DD format
        activities = activities.filter(created_at__date__gte=start_date)
    
    # Further filtering based on end date or other criteria can be similarly added

    return render(request, 'your_template.html', {'activities': activities})


def item(request, pk):
    item = Item.objects.get(pk=pk)
    return render(request, "item_details.html", {"item": item})


def leaderboard(request):
    # start_date = request.GET.get('start_date')
    # end_date = request.GET.get('end_date')
    # start_date_parsed = parse_date(start_date) if start_date else None
    # end_date_parsed = parse_date(end_date) if end_date else None

    # queryset = Activity.objects.all()

    # if start_date_parsed:
    #     queryset = queryset.filter(date_completed__gte=start_date_parsed)
    # if end_date_parsed:
    #     queryset = queryset.filter(date_completed__lte=end_date_parsed)

    # leaderboard_data = queryset.values('user__id', 'user__email').annotate(total_points=Sum('points')).order_by('-total_points')

    # data = list(leaderboard_data)
    # return JsonResponse(data, safe=False)
    return render(request, "leaderboard.html")


def individual_leaderboard(request):
    # Fetch users and their points
    users = UserProfile.objects.annotate(total_points=Sum("points")).order_by(
        "-total_points"
    )
    return render(request, "partials/individual_leaderboard.html", {"users": users})


def team_leaderboard_view(request):
    teams = Team.objects.prefetch_related(
        Prefetch(
            'member',
            queryset=CustomUser.objects.annotate(total_points=Sum('lifetime_points'))
        )
    ).annotate(team_points=Sum('member__lifetime_points')).order_by('-team_points')

    return render(request, 'partials/team_leaderboard.html', {'teams': teams})


def leaderboard_view(request: HttpRequest):
    # Order users by lifetime points
    users = CustomUser.objects.all().order_by('-lifetime_points')
    
    if request.headers.get('HX-Request', False):
        # return the partial content
        return render(request, 'partials/individual_leaderboard.html', {'users': users})
    else:
        # return the entire page
        return render(request, 'leaderboard.html', {'users': users})



def store(request):
    items = Item.objects.all()
    return render(request, "store.html", {"items": items})


def notifications(request):
    return render(request, "notifications.html")


def profile(request):
    user = CustomUser.objects.all()
    return render(request, 'profile.html', {"user": user})