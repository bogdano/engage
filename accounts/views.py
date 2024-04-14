import sys
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login, logout
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from .models import LoginToken, CustomUser
import cloudinary.uploader
import uuid
from django.db.models import Q

def send_login_link(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            print('User with email address ' + email + ' not found')
            user = None

        if user:
            # Create a new LoginToken for the user
            print('Creating token for user', user)
            token = LoginToken.objects.create(user=user, token=uuid.uuid4())
            token.save()

            # Create a unique link for the user to log in
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            login_link = f'http://{domain}/accounts/login/{uid}/{token.token}/'  # Use the token's string representation
            print('Login link:', login_link)
            
            # Send the login link via email
            subject = 'Your Login Link'
            message = render_to_string('auth/login_link.html', {'login_link': login_link})
            from_email = 'noreply@engage.bogz.dev'
            send_mail(subject, message, from_email, [email])
            return render(request, 'auth/send_login_link.html',  {'success': 'An email with your login link has been sent to ' + email + '. Please check your inbox.'})
        else:
            return render(request, 'auth/register.html', {'error': 'User with email address ' + email + ' not found'})
    else:
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'auth/send_login_link.html')


def login_with_link(request, uidb64, token):
    if request.user.is_authenticated:
        return redirect('home')
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
        print('User:', user)
        token_record = LoginToken.objects.get(user=user, token=token)
        print('Found token:', token_record.token)
        # Check if the token is expired 
        if timezone.now() > token_record.expiration_date: # or token_record.used == True:
            print('Token expired')
            # token_record.delete()
            return render(request, 'auth/send_login_link.html', {'error': 'This login link has expired. Please request a new one.'})
        else:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            # delete the aleady used token (links sent to Microsoft Defender servers which use 
            # Safelinks to scan links, thereby deleting the token before the user can use it to login)
            # that's why the .used == true condition before token deletion is commented out above
            # print(f"deleting token {token}")
            token_record.used = True
            token_record.save()
            return redirect('home')

    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist, LoginToken.DoesNotExist):
        # print out type of error in console
        print('Error:', sys.exc_info()[0])
        return render(request, 'auth/send_login_link.html', {'error': 'Invalid login link. Please request a new one.'})

def register(request):
    if request.method == 'POST':
        # Extract form data
        email = request.POST.get('email')
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'auth/send_login_link.html', {'error': 'User already exists. Please login.'})
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        position = request.POST.get('position', '')
        description = request.POST.get('description', '')

        # Basic validation (you can add more according to your needs)
        if not email or not first_name or not last_name:
            return render(request, 'auth/register.html', {'error': 'Please fill in all required fields'})

        uploaded_image_url = ''
        if 'profile_picture' in request.FILES:
            uploaded_image = cloudinary.uploader.upload(request.FILES['profile_picture'], upload_preset="gj4yeadt")
            uploaded_image_url = uploaded_image['secure_url']

        # Create the user
        user = CustomUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            position=position,
            profile_picture=uploaded_image_url,
            description=description,
        )

        # Generate a login token for the new user
        token = LoginToken.objects.create(user=user, token=uuid.uuid4())

        # Create a unique link for the user to log in
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        login_link = f'http://{domain}/accounts/login/{uid}/{token.token}/'

        # Send the login link via email
        subject = 'Welcome! Use this link to log in'
        message = render_to_string('auth/login_link.html', {'login_link': login_link})
        send_mail(subject, message, 'noreply@engage.bogz.dev', [email])

        # Redirect or return a success message
        return render(request, 'auth/email_sent.html')
    else:
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'auth/register.html')

def logout_view(request):
    # get all expired tokens and all used tokens
    tokens_query = LoginToken.objects.filter(Q(expiration_date__lt=timezone.now()) | Q(used=True))
    expired_or_used_tokens = tokens_query.all()
    # delete all expired tokens periodically, on logout because we can't delete tokens on access cause of Microsoft
    for token in expired_or_used_tokens:
        token.delete()
        
    logout(request)
    return redirect('home') 
