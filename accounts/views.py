from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model, login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Team
from django.db.models import Sum

User = get_user_model()

def send_login_link(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.get(email=email)

        if user:
            # Generate a one-time use token for the user
            token = default_token_generator.make_token(user)

            # Create a unique link for the user to log in
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            login_link = f'http://{domain}/login/{uid}/{token}/'
            print("login,", login_link)

            # Send the login link via email
            subject = 'Your Login Link'
            message = render_to_string('auth/login_link.html', {'login_link': login_link})
            from_email = 'noreply@example.com'
            send_mail(subject, message, from_email, [email])

        return render(request, 'auth/email_sent.html')
    return render(request, 'auth/send_login_link.html')

def login_with_link(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        # Log the user in without requiring a password
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        return redirect('user_email')  # Replace 'home' with the URL to redirect after login

    return render(request, 'auth/login_link_invalid.html')

@login_required
def user_email(request):
    email = request.user.email
    return render(request, 'user.html', {'email': email})

def leaderboard(request):
    # renders the initial page
    return render(request, 'leaderboard.html')

def individual_leaderboard(request):
    # Fetch users and their points
    users = UserProfile.objects.annotate(total_points=Sum('points')).order_by('-total_points')
    return render(request, 'partials/individual_leaderboard.html', {'users': users})

def team_leaderboard(request):
    # Fetch teams and their points
    teams = Team.objects.annotate(total_points=Sum('userprofile__points')).order_by('-total_points')
    return render(request, 'partials/team_leaderboard.html', {'teams': teams})