from .models import Team, Activity, Leaderboard, Item, UserParticipated, Notification
from notifications.views import *
from accounts.models import CustomUser
from django.db.models import Count, Exists, OuterRef
from django.db.models.functions import TruncDay
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import cloudinary.uploader
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
import dateutil.parser
from django.views.generic import TemplateView
from django.urls import reverse
from django.core.mail import send_mail
from django.db.models import Sum, Q


class ServiceWorker(TemplateView):
    template_name = "sw.js"
    content_type = "application/javascript"


def offline(request):
    return render(request, "offline.html")


def home(request):
    if not request.user.is_authenticated:
        return redirect("send_login_link")
    else:
        # fetch approved and active activities
        activities = Activity.objects.filter(is_active=True).order_by("event_date")
        # set the date range
        start_date = datetime.today()
        end_date = start_date + timedelta(days=30)
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
                is_approved=True,
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
        recent_past_activities = []

        # filter activities by date if query_date is present
        query_date = request.GET.get("query_date", None)
        if query_date is not None:
            activities = Activity.objects.filter(event_date__date=query_date).order_by(
                "event_date"
            )
            # format in 'A, d, B' format
            query_date = datetime.strptime(query_date, "%Y-%m-%d").strftime("%A, %d %B")
        else:
            today = timezone.make_aware(datetime.today())
            tomorrow = today + timedelta(days=1)
            upcoming_start = tomorrow + timedelta(days=1)

            today_activities = activities.filter(event_date__date=today.date())
            tomorrow_activities = activities.filter(event_date__date=tomorrow.date())
            upcoming_activities = activities.filter(
                event_date__date__gte=upcoming_start.date()
            )

            user_participations = UserParticipated.objects.filter(
                activity=OuterRef("pk"), user=request.user
            )

            # Fetch 10 most recent past activities
            recent_past_activities = (
                Activity.objects.filter(is_approved=True, event_date__lt=datetime.now())
                .order_by("-event_date")[:5]
                .annotate(user_has_participated=Exists(user_participations))
            )

            for activity in recent_past_activities:
                activity.is_active = False
                activity.save()
            activities = None

        # update context
        context = {
            "activities": activities,
            "today_activities": today_activities,
            "tomorrow_activities": tomorrow_activities,
            "upcoming_activities": upcoming_activities,
            "dates_with_activities": dates_with_activities,
            "recent_past_activities": recent_past_activities,
            "query_date": query_date,
        }
        return render(request, "home.html", context)


def add_activity(request):
    if not request.user.is_authenticated:
        return redirect("send_login_link")
    leaderboards = Leaderboard.objects.all()
    return render(request, "add_activity.html", {"leaderboards": leaderboards})


def bookmark_activity(request, pk):
    activity = Activity.objects.get(pk=pk)
    user = request.user
    if user in activity.interested_users.all():
        activity.interested_users.remove(user)
    else:
        activity.interested_users.add(user)
    if request.GET.get("from_activity_page"):
        return render(request, "partials/activity_header.html", {"activity": activity})
    else:
        return render(request, "partials/activity_card.html", {"activity": activity})


def leave_activity(request, pk):
    activity = Activity.objects.get(pk=pk)
    user = request.user
    activity.interested_users.remove(user)
    return redirect("profile")


def edit_activity(request, pk):
    if request.user.is_staff:
        activity = Activity.objects.get(pk=pk)
        leaderboards = Leaderboard.objects.all()
        return render(
            request,
            "edit_activity.html",
            {"activity": activity, "leaderboards": leaderboards},
        )
    else:
        return redirect("home")


def update_activity(request, pk):
    if request.method == "POST" and request.user.is_staff:
        activity = Activity.objects.get(pk=pk)
        title = request.POST.get("title")
        points = request.POST.get("points")
        description = request.POST.get("description")
        address = request.POST.get("address")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        event_date = request.POST.get("event_date")
        end_date = request.POST.get("end_date")
        uploaded_image_url = activity.photo
        if "photo" in request.FILES:
            uploaded_image = cloudinary.uploader.upload(
                request.FILES["photo"],
                quality="75",
                fetch_format="webp",
                height=700,
            )
            uploaded_image_url = uploaded_image["secure_url"]
        leaderboard_names = request.POST.getlist("leaderboards")
        leaderboards = [
            Leaderboard.objects.get_or_create(leaderboard_name=name, defaults={'leaderboard_color': 'amber'})[0]
            for name in leaderboard_names
        ]
        activity.title = title
        activity.points = int(points)
        activity.description = description
        activity.address = address
        activity.latitude = latitude
        activity.longitude = longitude
        activity.event_date = event_date
        activity.end_date = end_date
        activity.photo = uploaded_image_url
        activity.leaderboards.clear()
        activity.leaderboards.add(*leaderboards)

        event_date_naive = dateutil.parser.parse(event_date)
        event_date_aware = timezone.make_aware(event_date_naive, timezone.get_default_timezone())
        if event_date_aware > timezone.now():
            activity.is_active = True
            for user in activity.participated_users.all():
                user.balance -= activity.points
                user.lifetime_points -= activity.points
                user.save()
                activity.participated_users.remove(user)

        activity.save()
        redirect_url = reverse("activity", args=[activity.pk])
        response = HttpResponse("Redirecting...")
        response["HX-Redirect"] = redirect_url
        return response


def delete_activity(request, pk):
    if request.method == "DELETE" and request.user.is_staff:
        activity = Activity.objects.get(pk=pk)
        activity.delete()
        return redirect("home")


@login_required
def approve_activity(request, pk):
    if request.user.is_staff:
        # Retrieve the activity based on primary key (pk)
        activity = Activity.objects.get(pk=pk)
        activity.is_approved = True
        activity.save()

        # Fetch all users to notify them about the approval
        users = (
            CustomUser.objects.all()
        )  # Consider excluding the activity creator if needed

        activity_url = request.build_absolute_uri(
            reverse("activity", args=[activity.pk])
        )

        # Create a notification for each user
        notifications = [
            Notification(
                recipient=user,
                title=f"New Activity Posted: {activity.title}",
                message=f"The activity titled '<a href=\"{activity_url}\">{activity.title}</a>' has been approved and is now live!",
                read=False,
            )
            for user in users
        ]
        Notification.objects.bulk_create(
            notifications
        )  # Use bulk_create for efficiency

        # Redirect to the homepage or another appropriate page
        return redirect("home")


def load_more_activities(request):
    offset = int(request.GET.get("offset", 0))
    next_offset = offset + 5
    user_participations = UserParticipated.objects.filter(
        activity=OuterRef("pk"), user=request.user
    )
    past_activities = (
        Activity.objects.filter(is_approved=True, is_active=False)
        .order_by("-event_date")[offset:next_offset]
        .annotate(user_has_participated=Exists(user_participations))
    )
    if not past_activities or len(past_activities) < 5:
        return render(
            request,
            "partials/past_activities.html",
            {"past_activities": past_activities, "no_more_activities": True},
        )
    return render(
        request, "partials/past_activities.html", {"past_activities": past_activities}
    )


def new_activity(request):
    if request.method == "POST":
        title = request.POST.get("title")
        points = request.POST.get("points")
        description = request.POST.get("description")
        creator = request.user
        address = request.POST.get("address")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        event_date_naive = dateutil.parser.parse(request.POST.get("event_date"))
        end_date_naive = dateutil.parser.parse(request.POST.get("end_date"))
        event_date = timezone.make_aware(event_date_naive, timezone.get_default_timezone())
        end_date = timezone.make_aware(end_date_naive, timezone.get_default_timezone())
        # upload photo to cloudinary and store URL in database
        uploaded_image_url = ""
        if "photo" in request.FILES:
            uploaded_image = cloudinary.uploader.upload(request.FILES["photo"], quality="75", fetch_format="webp", height=700,)
            uploaded_image_url = uploaded_image["secure_url"]
        leaderboard_names = request.POST.getlist("leaderboards")
        # Create new Leaderboard instances if necessary
        leaderboards = [
            Leaderboard.objects.get_or_create(leaderboard_name=name, defaults={'leaderboard_color': 'amber'})[0]
            for name in leaderboard_names
        ]
        alert = bool(request.POST.get("alert"))

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
            alert=alert,
        )
        # Link the Leaderboard instances to the Activity instance
        activity.leaderboards.add(*leaderboards)
        if request.user.is_staff:
            activity.is_approved = True
            activity.save()
            if alert:
                # Fetch all users to notify them about the new activity
                creator = creator.first_name + " " + creator.last_name
                users = CustomUser.objects.filter(is_staff=False, is_active=True)
                activity_url = request.build_absolute_uri(reverse('activity', args=[activity.pk]))
                subject = 'Important activity added to Engage'
                message = 'Hello!\n' + creator + ' just added a new activity titled "' \
                            + title + '" to Engage! \nIt expires at ' + end_date.strftime("%-I:%M %p") \
                            + ' on ' + end_date.strftime("%A, %d %B") + '. \n' \
                            + '"' + description + '"\nCheck it out <a href="' \
                            + activity_url + '">here</a>.'
                from_email = 'noreply@engage.bogz.dev'
                # Send an email about the activity to each user
                for user in users:
                    send_mail(subject, message, from_email, [user.email])

        redirect_url = reverse("activity", args=[activity.pk])
        response = HttpResponse("Redirecting...")
        response["HX-Redirect"] = redirect_url
        return response
    else:
        return JsonResponse({"error": "Invalid request method"})


def activity(request, pk):
    if not request.user.is_authenticated:
        return redirect("send_login_link")
    try:
        activity = Activity.objects.get(pk=pk)
    except Activity.DoesNotExist:
        return redirect("home")
    other_interested_users = activity.interested_users.all().exclude(pk=request.user.pk)
    activity.user_has_participated = activity.participated_users.filter(
        pk=request.user.pk
    ).exists()
    return render(
        request,
        "activity.html",
        {
            "activity": activity,
            "other_interested_users": other_interested_users,
        },
    )


def additional_users(request, pk):
    users = (
        Activity.objects.get(id=pk)
        .interested_users.all()
        .exclude(pk=request.user.pk)[8:]
    )
    return render(request, "partials/additional_users.html", {"users": users})


def award_participation_points(request, pk):
    user = request.user
    activity = Activity.objects.get(pk=pk)
    if user in activity.participated_users.all():
        return JsonResponse(
            {"error": "User has already been awarded points for this activity"}
        )
    else:
        user.balance += activity.points
        user.lifetime_points += activity.points
        user.save()
        activity.participated_users.add(user)
        activity.user_has_participated = True
        update_team_rankings()
        if request.GET.get("from_activity_page"):
            return render(request, "partials/activity_header.html", {"activity": activity})
        else:
            return render(request, "partials/activity_card.html", {"activity": activity})

def update_team_rankings():
    teams = Team.objects.all()
    now = timezone.now()
    start_date = timezone.make_aware(datetime(now.year, now.month, 1))
    user_participations = UserParticipated.objects.filter(date_participated__gte=start_date)
    teams = Team.objects.annotate(
            team_points=Sum('member__userparticipated__activity__points', filter=Q(member__userparticipated__in=user_participations))
        ).order_by('-team_points')
    # save order of each team in team.monthly rank based on order in teams
    for i, team in enumerate(teams):
        team.monthly_rank = i+1
        team.save()        


def edit_item(request, pk):
    item = Item.objects.get(pk=pk)
    item.name = request.POST.get("itemName")
    item.price = request.POST.get("pointCost")
    item.description = request.POST.get("itemDescription")
    if "photo" in request.FILES:
        image = cloudinary.uploader.upload(request.FILES["photo"], upload_preset="p4p2xtey")
        item.image = image["secure_url"]
    item.save()
    items = Item.objects.all()
    user = request.user
    return render(request, "store.html", {"items": items, "user": user})


def delete_item(request, pk):
    item = Item.objects.get(pk=pk)
    item.delete()
    return redirect("store")


def edit_item_form(request, pk):
    item = Item.objects.get(pk=pk)
    return render(request, "edit_item.html", {"item": item})


def new_item(request):
    if not request.user.is_authenticated:
        return redirect("send_login_link")
    if request.method == "POST":
        name = request.POST.get("itemName")
        points = request.POST.get("pointCost")
        description = request.POST.get("itemDescription")
        uploaded_image = cloudinary.uploader.upload(request.FILES["photo"], upload_preset="p4p2xtey")
        uploaded_image_url = uploaded_image["secure_url"]
        item = Item.objects.create(name=name, description=description, price=points, image=uploaded_image_url)
        item.save()
    items = Item.objects.all()
    return render(request, "store.html", {"items": items})


def add_item(request):
    if not request.user.is_authenticated:
        return redirect("send_login_link")
    elif request.user.is_staff:
        return render(request, "new_item.html")
    else:
        return redirect("home")


def item(request, pk):
    if not request.user.is_authenticated:
        return redirect("send_login_link")
    item = Item.objects.get(pk=pk)
    return render(request, "item_details.html", {"item": item})


def store(request):
    if not request.user.is_authenticated:
        return redirect("send_login_link")
    items = Item.objects.all()
    return render(request, "store.html", {"items": items})


@login_required
def profile(request, pk=None):
    if pk:
        user = CustomUser.objects.get(pk=pk)
    else:
        user = request.user
        
    try:
        team = Team.objects.get(member=user)
    except Team.DoesNotExist:
        team = None
    except Team.MultipleObjectsReturned:
        team = Team.objects.filter(member=user).first()

    interested = Activity.objects.filter(
        interested_users=user, is_approved=True
    ).order_by("event_date")
    interested = interested.exclude(participated_users=user)
    # true if user is interested  in any activity that is active
    participated = Activity.objects.filter(
        participated_users=user, is_active=False
    ).order_by("-event_date")[:5]
    return render(
        request,
        "profile.html",
        {
            "user": user,
            "team": team,
            "interested": interested,
            "participated": participated,
        },
    )


def additional_past_activities(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    # return past acttivities a user has participated in
    participated_activities = Activity.objects.filter(
        participated_users=user, is_active=False
    ).order_by("-event_date")[5:]
    return render(
        request,
        "partials/additional_past_activities.html",
        {"activities": participated_activities},
    )


@login_required
def edit_profile(request):
    # This is to check if the user is authenticated before allowing the edit
    if not request.user.is_authenticated:
        return redirect("home")
    else:
        if request.method == "POST":
            # Get the current user
            user = request.user
            # Update the user fields with the data from the form
            if "email" in request.POST and request.POST["email"]:
                user.email = request.POST["email"]
            if "first_name" in request.POST and request.POST["first_name"]:
                user.first_name = request.POST["first_name"]
            if "last_name" in request.POST and request.POST["last_name"]:
                user.last_name = request.POST["last_name"]
            if "position" in request.POST:
                user.position = request.POST["position"]
            if "description" in request.POST:
                user.description = request.POST["description"]
            if "profile_picture" in request.FILES:
                user.profile_picture = request.FILES["profile_picture"]
                # Handle profile picture upload if provided
                # Upload the image to Cloudinary
                uploaded_image = cloudinary.uploader.upload(
                    request.FILES["profile_picture"], upload_preset="gj4yeadt"
                )
                # Get the URL of the uploaded image from Cloudinary
                user.profile_picture = uploaded_image["secure_url"]
                # This part is up to you depending on how you handle profile picture uploads
                pass

            # Save the updated user information
            user.save()

            # Redirect to the profile page or any other appropriate page
            return redirect("profile")
        else:
            return render(request, "edit_profile.html")
