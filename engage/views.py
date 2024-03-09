from .models import Team, Activity, Leaderboard, Item
from accounts.models import CustomUser
from django.db.models import Sum
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
 