from .models import Team, Activity, Leaderboard, Item, UserParticipated
from .forms import TeamCreateForm, JoinTeamForm
from accounts.models import CustomUser
from django.db.models import Sum, Count, Exists, OuterRef, Prefetch, Q
from django.db.models.functions import TruncDay
from django.http import HttpRequest
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
import cloudinary.uploader
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView
from django.contrib import messages

# class ServiceWorker(TemplateView):
#     template_name = "sw.js"
#     content_type = "application/javascript"


def home(request):
    if not request.user.is_authenticated:
        return redirect("send_login_link")
    else:
        # fetch approved and active activities
        activities = Activity.objects.filter(is_active=True).order_by(
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
            activities = Activity.objects.filter(event_date__date=query_date).order_by("event_date")
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
    return render(request, "partials/activity_card.html", {"activity": activity})


def bookmark_activity_from_activity(request, pk):
    activity = Activity.objects.get(pk=pk)
    user = request.user
    if user in activity.interested_users.all():
        activity.interested_users.remove(user)
    else:
        activity.interested_users.add(user)
    return render(request, "partials/bookmark_button.html", {"activity": activity})


def edit_activity(request, pk):
    if request.method == "GET" and request.user.is_staff:
        activity = Activity.objects.get(pk=pk)
        leaderboards = Leaderboard.objects.all()
        return render(request, "edit_activity.html", {"activity": activity, "leaderboards": leaderboards})


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
        uploaded_image_url = ""
        if "photo" in request.FILES:
            uploaded_image = cloudinary.uploader.upload(
                request.FILES["photo"], quality="50", fetch_format="auto"
            )
            uploaded_image_url = uploaded_image["url"]
        leaderboard_names = request.POST.getlist("leaderboards")
        leaderboards = [
            Leaderboard.objects.get_or_create(leaderboard_name=name)[0]
            for name in leaderboard_names
        ]
        activity.title = title
        activity.points = points
        activity.description = description
        activity.address = address
        activity.latitude = latitude
        activity.longitude = longitude
        activity.event_date = event_date
        activity.end_date = end_date
        activity.photo = uploaded_image_url
        activity.leaderboards.clear()
        activity.leaderboards.add(*leaderboards)
        activity.save()
        return redirect("home")


def delete_activity(request, pk):
    if request.method == "DELETE" and request.user.is_staff:
        activity = Activity.objects.get(pk=pk)
        activity.delete()
        return redirect("home")
    

def approve_activity(request, pk):
    if request.user.is_staff:
        activity = Activity.objects.get(pk=pk)
        activity.is_approved = True
        activity.save()
        return redirect("home")


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


def load_more_activities(request):
    offset = int(request.GET.get("offset", 0))
    next_offset = offset + 5
    user_participations = UserParticipated.objects.filter(activity=OuterRef("pk"), user=request.user)
    past_activities = Activity.objects.filter(
        is_approved=True, is_active=False
    ).order_by("-event_date")[offset:next_offset].annotate(user_has_participated=Exists(user_participations))
    if not past_activities or len(past_activities) < 5:
        return render(request, "partials/past_activities.html", {"past_activities": past_activities, "no_more_activities": True})
    return render(request, "partials/past_activities.html", {"past_activities": past_activities})


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
            uploaded_image = cloudinary.uploader.upload(
                request.FILES["photo"], quality="50", fetch_format="auto"
            )
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
        return redirect("home")
    else:
        return JsonResponse({"error": "Invalid request method"})


def activity(request, pk):
    if not request.user.is_authenticated:
        return redirect("send_login_link")
    activity = Activity.objects.get(pk=pk)
    other_interested_users = activity.interested_users.all().exclude(pk=request.user.pk)
    user_has_participated = activity.participated_users.filter(
        pk=request.user.pk
    ).exists()
    return render(
        request,
        "activity.html",
        {
            "activity": activity,
            "other_interested_users": other_interested_users,
            "user_has_participated": user_has_participated,
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
        if request.GET.get("from_activity_page"):
            return render(
                request, "partials/points_display.html", {"activity": activity}
            )
        else:
            return render(
                request, "partials/activity_card.html", {"activity": activity}
            )


def new_item(request):
    if request.method == "POST":
        name = request.POST.get("itemName")
        points = request.POST.get("pointCost")
        description = request.POST.get("itemDescription")
        uploaded_image = cloudinary.uploader.upload(
            request.FILES["photo"], quality="50", fetch_format="auto"
        )
        uploaded_image_url = uploaded_image["url"]
    item = Item.objects.create(
        name=name, description=description, price=points, image=uploaded_image_url
    )
    item.save()
    items = Item.objects.all()
    return render(request, "store.html", {"items": items})


def add_item(request):
    return render(request, "new_item.html")


def item(request, pk):
    item = Item.objects.get(pk=pk)
    return render(request, "item_details.html", {"item": item})


def leaderboard(request):

    return render(request, "leaderboard.html")


def individual_leaderboard_view(request):
    leaderboards = Leaderboard.objects.all()
    selected_leaderboard_id = request.GET.get('leaderboard_id', None)
    date_filter = request.GET.get('date_filter', None)

    # Default to None, will be used to filter by date if specified
    start_date = None

    now = datetime.now() 
    if date_filter == "this_year":
        start_date = datetime(now.year, 1, 1)
    elif date_filter == "this_month":
        start_date = datetime(now.year, now.month, 1)

    user_participations = UserParticipated.objects.all()

    if start_date:
        user_participations = user_participations.filter(date_participated__gte=start_date)

    if selected_leaderboard_id:
        user_participations = user_participations.filter(activity__leaderboards__id=selected_leaderboard_id)
    
    users_with_points = user_participations.values(
        'user__id', 'user__first_name', 'user__last_name'
    ).annotate(
        total_points=Sum('activity__points')
    ).order_by('-total_points')

    return render(request, "leaderboard.html", {
        "users_with_points": users_with_points,
        "leaderboards": leaderboards,
        "selected_leaderboard_id": selected_leaderboard_id,
        "date_filter": date_filter
    })


def team_leaderboard_view(request):
    leaderboards = Leaderboard.objects.all()
    selected_leaderboard_id = request.GET.get('leaderboard_id')
    teams_query = Team.objects.prefetch_related(
        Prefetch(
            "member",
            queryset=CustomUser.objects.annotate(total_points=Sum("lifetime_points"))
        )
    )

    # Filtering by leaderboard type
    leaderboard_id = request.GET.get('leaderboard_id')
    if leaderboard_id:
        teams_query = teams_query.filter(activities__leaderboards__id=leaderboard_id)

    # Filtering by date
    date_filter = request.GET.get('date_filter')
    now = timezone.now()

    if date_filter == "this_year":
        start_of_year = datetime(now.year, 1, 1)
        start_date = timezone.make_aware(start_of_year)
    elif date_filter == "this_month":
        start_of_month = datetime(now.year, now.month, 1)
        start_date = timezone.make_aware(start_of_month)
    else:
        start_date = timezone.make_aware(datetime(1, 1, 1)) 

    end_date = now

    teams = teams_query.annotate(team_points=Sum("member__lifetime_points")).order_by("-team_points")

    return render(request, "partials/team_leaderboard.html", {
        "teams": teams,
        "leaderboards": leaderboards,
        "selected_leaderboard_id": selected_leaderboard_id,
        "date_filter": date_filter
    })


def leaderboard_view(request):
    # Determine the mode (individual or team) based on a parameter
    leaderboard_mode = request.GET.get('leaderboard_mode', 'individual')

    context = {
        'leaderboard_mode': leaderboard_mode,
        'leaderboards': Leaderboard.objects.all(),
    }

    # Logic for individual leaderboard
    if leaderboard_mode == 'individual':
        users = CustomUser.objects.annotate(total_points=Sum("lifetime_points")).order_by("-total_points")
        context['users'] = users

    # Logic for team leaderboard
    elif leaderboard_mode == 'team':
        teams = Team.objects.annotate(team_points=Sum("member__lifetime_points")).order_by("-team_points")
        context['teams'] = teams

    return render(request, "leaderboard.html", context)

def list_teams(request):
    teams = Team.objects.all()
    join_form = JoinTeamForm()
    return render(request, 'list_teams.html', {'teams': teams, 'join_form': join_form})

def create_team(request):
    if request.method == 'POST':
        form = TeamCreateForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.leader = request.user
            team.save()
            messages.success(request, 'Team created successfully.')
            return redirect('list_teams')
    else:
        form = TeamCreateForm()
    return render(request, 'create_team.html', {'form': form})

def join_team(request):
    if request.method == 'POST':
        form = JoinTeamForm(request.POST)
        if form.is_valid():
            team_id = form.cleaned_data['team_id']
            team = get_object_or_404(Team, id=team_id)
            team.member.add(request.user)
            messages.success(request, 'Join request sent.')
            return redirect('list_teams')
    else:
        return redirect('list_teams')

def store(request):
    items = Item.objects.all()
    return render(request, "store.html", {"items": items})


def notifications(request):
    return render(request, "notifications.html")


def profile(request):
    user = request.user
    teams = Team.objects.all()
    return render(request, "profile.html", {"user": user, "teams": teams})

def outside_profile(request):
    user = request.user
    return render(request, "outside_profile.html", {"user": user})

def edit_profile(request):
    # This is to check if the user is authenticated before allowing the edit
    if not request.user.is_authenticated:
        return redirect("profile")

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
                uploaded_image = cloudinary.uploader.upload(request.FILES["profile_picture"])
                # Get the URL of the uploaded image from Cloudinary
                user.profile_picture = uploaded_image["url"]
                # This part is up to you depending on how you handle profile picture uploads
                pass

            # Save the updated user information
            user.save()

            # Redirect to the profile page or any other appropriate page
            return redirect("profile")
        else:
            return render(request, "edit_profile.html")
