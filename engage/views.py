from .models import Team, Activity, Leaderboard, Item, ActivityType, UserParticipated
from accounts.models import CustomUser
from django.db.models import Sum, Count, Exists, OuterRef, Prefetch
from django.db.models.functions import TruncDay
from django.http import HttpRequest
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import cloudinary.uploader
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView

# class ServiceWorker(TemplateView):
#     template_name = "sw.js"
#     content_type = "application/javascript"

def home(request):
    if not request.user.is_authenticated:
        return redirect("send_login_link")
    else:
        # fetch approved and active activities
        activities = Activity.objects.filter(is_approved=True, is_active=True).order_by("event_date")
        # set the date range 
        start_date = datetime.today()
        end_date = start_date + timedelta(days=15)
        # generate the date range
        date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
        # fetch activities within the date range and count them by date
        activities_in_range = activities.annotate(date=TruncDay('event_date')) \
            .filter(event_date__date__gte=start_date.date(), event_date__date__lte=end_date.date()) \
            .values('date') \
            .annotate(total_activities=Count('id')) \
            .order_by('date')
        # convert QuerySet to a dict for easier access
        activities_dict = {activity['date'].date(): activity['total_activities'] for activity in activities_in_range}
        # prepare dates with activities info for the template
        dates_with_activities = []
        for date in date_range:
            dates_with_activities.append({
                'date': date,
                'has_activities': date.date() in activities_dict,
                'total_activities': activities_dict.get(date.date(), 0)
            })

        today_activities = []
        tomorrow_activities = []
        upcoming_activities = []
        recent_past_activities = []

        # filter activities by date if query_date is present
        query_date = request.GET.get('query_date', None)
        if query_date is not None:
            activities = Activity.objects.filter(is_approved=True, event_date__date=query_date).order_by("event_date")
            # format in 'A, d, B' format
            query_date = datetime.strptime(query_date, '%Y-%m-%d').strftime('%A, %d %B')
        else:
            today = make_aware(datetime.today())
            tomorrow = today + timedelta(days=1)
            upcoming_start = tomorrow + timedelta(days=1)

            today_activities = activities.filter(event_date__date=today.date())
            tomorrow_activities = activities.filter(event_date__date=tomorrow.date())
            upcoming_activities = activities.filter(event_date__date__gte=upcoming_start.date())

            user_participations = UserParticipated.objects.filter(
                activity=OuterRef('pk'), 
                user=request.user
            )

            # Fetch 10 most recent past activities
            recent_past_activities = Activity.objects \
                .filter(is_approved=True, event_date__lt=datetime.now()) \
                .order_by("-event_date")[:5] \
                .annotate(user_has_participated=Exists(user_participations))
            
            for activity in recent_past_activities:
                activity.is_active = False
                activity.save()
            activities = None

        # update context
        context = {
            'activities': activities,
            'today_activities': today_activities,
            'tomorrow_activities': tomorrow_activities,
            'upcoming_activities': upcoming_activities,
            'dates_with_activities': dates_with_activities,
            'recent_past_activities': recent_past_activities,
            'query_date': query_date
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

def load_more_activities(request):
    offset = int(request.GET.get('offset', 0))
    next_offset = offset + 5
    past_activities = Activity.objects.filter(is_approved=True, is_active=False).order_by("-event_date")[offset:next_offset]
    if not past_activities or len(past_activities) < 5:
        html = render_to_string('partials/past_activities.html', {'past_activities': past_activities, 'no_more_activities': True})
        return HttpResponse(html)
    html = render_to_string('partials/past_activities.html', {'past_activities': past_activities})
    return HttpResponse(html)

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
            uploaded_image = cloudinary.uploader.upload(request.FILES["photo"], quality="50", fetch_format="auto")
            uploaded_image_url = uploaded_image["url"]

        leaderboard_names = request.POST.getlist("leaderboards")
        # Create new Leaderboard instances if necessary
        leaderboards = [Leaderboard.objects.get_or_create(leaderboard_name=name)[0] for name in leaderboard_names]

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
            return render(request, "activity_pending.html")
    else:
        return JsonResponse({"error": "Invalid request method"})


def activity(request, pk):
    if not request.user.is_authenticated:
        return redirect("send_login_link")
    activity = Activity.objects.get(pk=pk)
    other_interested_users = activity.interested_users.all().exclude(pk=request.user.pk)
    user_has_participated = activity.participated_users.filter(pk=request.user.pk).exists()
    return render(request, "activity.html", {"activity": activity, "other_interested_users": other_interested_users, "user_has_participated": user_has_participated})


def additional_users(request, pk):
    users = Activity.objects.get(id=pk).interested_users.all().exclude(pk=request.user.pk)[8:]
    return render(request, 'partials/additional_users.html', {'users': users})


# MAX, THIS IS WHERE YOU NEED TO ADD THE LOGIC TO UPDATE TEAM/LEADERBOARD POINTS
def award_participation_points(request, pk):
    user = request.user
    activity = Activity.objects.get(pk=pk)
    if user in activity.participated_users.all():
        return JsonResponse({"error": "User has already been awarded points for this activity"})
    else:
        user.balance += activity.points
        user.lifetime_points += activity.points
        user.save()
        activity.participated_users.add(user)
        activity.user_has_participated=True
        if request.GET.get('from_activity_page'):
            return render(request, "partials/points_display.html", {"activity": activity})
        else:
            return render(request, "partials/activity_card.html", {"activity": activity})




def new_item(request):
    if request.method == "POST":
        name = request.POST.get("itemName")
        points = request.POST.get("pointCost")
        description = request.POST.get("itemDescription")
        uploaded_image = cloudinary.uploader.upload(request.FILES["photo"], quality="50", fetch_format="auto")
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

def activity_leaderboard(request):
    activities = Activity.objects.all()
    activity_types = ActivityType.objects.all()

    date_filter = request.GET.get('date_filter')
    
    # Handle the new date_filter options
    if date_filter == "this_year":
        start_date = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        activities = activities.filter(created_at__gte=start_date)
    elif date_filter == "this_month":
        now = timezone.now()
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        activities = activities.filter(created_at__gte=start_date)
    # No need to filter for "all_time" since it includes everything

    return render(request, 'leaderboard.html', {
        'activities': activities,
        'activity_types': activity_types
    })


def leaderboard(request):
    
    return render(request, "leaderboard.html")


def individual_leaderboard(request):
    # Assuming lifetime_points or a similar field exists in CustomUser
    users = CustomUser.objects.annotate(total_points=Sum("lifetime_points")).order_by("-total_points")
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
    user = request.user 
    return render(request, 'profile.html', {"user": user})

def edit_profile(request):
    # This is to check if the user is authenticated before allowing the edit
    if not request.user.is_authenticated:
        return redirect('profile')
    
    else:
   
        if request.method == 'POST':
        # Get the current user
            user = request.user

        # Update the user fields with the data from the form
            if 'email' in request.POST and request.POST['email']:
                user.email = request.POST['email']
            if 'first_name' in request.POST and request.POST['first_name']:
                user.first_name = request.POST['first_name']
            if 'last_name' in request.POST and request.POST['last_name']:
                user.last_name = request.POST['last_name']
            if 'position' in request.POST:
                user.position = request.POST['position']
            if 'description' in request.POST:
                user.description = request.POST['description']
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
            # Handle profile picture upload if provided
            # This part is up to you depending on how you handle profile picture uploads
                pass

        # Save the updated user information
            user.save()

        # Redirect to the profile page or any other appropriate page
            return redirect('profile')
        else:
            return render(request, 'edit_profile.html')

