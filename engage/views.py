from .models import Team, Activity, Leaderboard, Item
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay
from accounts.models import CustomUser
from django.shortcuts import render, redirect
from django.http import JsonResponse
import cloudinary.uploader
from datetime import datetime, timedelta
from django.utils.timezone import make_aware


def homepage(request):
    if not request.user.is_authenticated:
        return render(request, "auth/send_login_link.html")
    else:
        # fetch approved and active activities
        activities = Activity.objects.filter(is_approved=True, is_active=True).order_by(
            "event_date"
        )
        # set the date range
        start_date = datetime.today()
        end_date = start_date + timedelta(days=15)
        # generate the date range
        date_range = [
            start_date + timedelta(days=x)
            for x in range((end_date - start_date).days + 1)
        ]
        # fetch activities within the date range and count them by date
        activities_in_range = (
            activities.annotate(date=TruncDay("event_date"))
            .filter(
                event_date__date__gte=start_date.date(),
                event_date__date__lte=end_date.date(),
            )
            .values("date")
            .annotate(total_activities=Count("id"))
            .order_by("date")
        )
        # convert QuerySet to a dict for easier access
        activities_dict = {
            activity["date"].date(): activity["total_activities"]
            for activity in activities_in_range
        }
        # prepare dates with activities info for the template
        dates_with_activities = []
        for date in date_range:
            dates_with_activities.append(
                {
                    "date": date,
                    "has_activities": date.date() in activities_dict,
                    "total_activities": activities_dict.get(date.date(), 0),
                }
            )

        today_activities = []
        tomorrow_activities = []
        upcoming_activities = []

        # filter activities by date if query_date is present
        query_date = request.GET.get("query_date", None)
        if query_date is not None:
            activities = Activity.objects.filter(event_date__date=query_date)
            # format in 'A, d, B' format
            query_date = datetime.strptime(query_date, "%Y-%m-%d").strftime("%A, %d %B")
        else:
            today = make_aware(datetime.today())
            tomorrow = today + timedelta(days=1)
            upcoming_start = tomorrow + timedelta(days=1)
            today_activities = activities.filter(event_date__date=today.date())
            tomorrow_activities = activities.filter(event_date__date=tomorrow.date())
            upcoming_activities = activities.filter(
                event_date__date__gte=upcoming_start.date()
            )
            activities = None

        # update context
        context = {
            "activities": activities,
            "today_activities": today_activities,
            "tomorrow_activities": tomorrow_activities,
            "upcoming_activities": upcoming_activities,
            "dates_with_activities": dates_with_activities,
            "query_date": query_date,
        }
        return render(request, "home.html", context)


def add_activity(request):
    leaderboards = Leaderboard.objects.all()
    return render(request, "add_activity.html", {"leaderboards": leaderboards})


def bookmark_activity(request, pk):
    activity = Activity.objects.get(pk=pk)
    user = request.user
    if user in activity.interested_users.all():
        activity.interested_users.remove(user)
    else:
        activity.interested_users.add(user)
    return render(request, "partials/activity_card.html", {"activity": activity})


def bookmark_activity_from_activity(request, pk):
    activity = Activity.objects.get(pk=pk)
    user = request.user
    if user in activity.interested_users.all():
        activity.interested_users.remove(user)
    else:
        activity.interested_users.add(user)
    return render(request, "partials/bookmark_button.html", {"activity": activity})


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
    user = request.user
    return render(request, "store.html", {"items": items, "user": user})


def add_item(request):
    if request.user.is_staff:
        return render(request, "new_item.html")
    else:
        return JsonResponse({"error": "You are not staff."})


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
            Leaderboard.objects.get_or_create(leaderboard_name=name)[0]
            for name in leaderboard_names
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


def team_leaderboard(request):
    # Fetch teams and their points
    teams = Team.objects.annotate(total_points=Sum("userprofile__points")).order_by(
        "-total_points"
    )
    return render(request, "partials/team_leaderboard.html", {"teams": teams})


def leaderboard_view(request):
    # Fetch the top 10 users by points
    top_users = UserProfile.objects.order_by("-points")[:10]
    return render(
        request, "partials/leaderboard_partial.html", {"top_users": top_users}
    )


def store(request):
    items = Item.objects.all()
    return render(request, "store.html", {"items": items})


def notifications(request):
    return render(request, "notifications.html")


def profile(request):
    user = CustomUser.objects.all()
    return render(request, "profile.html", {"user": user})
