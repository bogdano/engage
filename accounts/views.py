from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login, logout
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from .models import LoginToken, CustomUser
from .forms import UserRegistrationForm
import cloudinary.uploader
import uuid

def send_login_link(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            user = None

        if user:
            # Create a new LoginToken for the user
            token = LoginToken.objects.create(user=user, token=uuid.uuid4())
            
            # Create a unique link for the user to log in
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            login_link = f'http://{domain}/accounts/login/{uid}/{token.token}/'  # Use the token's string representation
            
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
        user = CustomUser.objects.get(pk=uid)
        token_record = LoginToken.objects.get(user=user, token=token)
        
        # Check if the token is expired
        if timezone.now() > token_record.expiration_date:
            token_record.delete()
            return render(request, 'auth/login_link_invalid.html')

    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist, LoginToken.DoesNotExist):
        return render(request, 'auth/login_link_invalid.html')

    # Log the user in without requiring a password
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    
    # Mark the token as used or delete it
    token_record.delete()

    return render(request, 'home.html')  # Replace 'home' with the URL to redirect after login

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Upload the profile picture to Cloudinary
            uploaded_image = None
            if 'profile_picture' in request.FILES:
                uploaded_image = cloudinary.uploader.upload(request.FILES['profile_picture'])
            
            # Create the user
            user = CustomUser.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                position=form.cleaned_data.get('position', ''),
                profile_picture=uploaded_image['url'] if uploaded_image else '',
                description=form.cleaned_data.get('description', ''),
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
            from_email = 'noreply@example.com'
            send_mail(subject, message, from_email, [user.email])
            
            # Redirect or return a success message
            return render(request, 'auth/email_sent.html')  # Adjust as necessary
    else:
        form = UserRegistrationForm()
    
    return render(request, 'auth/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('homepage')  # Replace 'home' with the URL to redirect after logout
