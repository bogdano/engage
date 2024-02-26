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
from django.http import HttpResponse

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
            return render(request, 'auth/login_link_expired.html')

    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist, LoginToken.DoesNotExist):
        return render(request, 'auth/login_link_invalid.html')

    # Log the user in without requiring a password
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    
    # Mark the token as used or delete it
    token_record.delete()

    return redirect('homepage')  

def register(request):
    if request.method == 'POST':
        # Extract form data
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        position = request.POST.get('position', '')
        description = request.POST.get('description', '')

        # Basic validation (you can add more according to your needs)
        if not email or not first_name or not last_name:
            return HttpResponse('Missing fields', status=400)

        uploaded_image_url = ''
        if 'profile_picture' in request.FILES:
            uploaded_image = cloudinary.uploader.upload(request.FILES['profile_picture'])
            uploaded_image_url = uploaded_image['url']

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
        send_mail(subject, message, 'noreply@example.com', [email])

        # Redirect or return a success message
        return render(request, 'auth/email_sent.html')
    else:
        return render(request, 'auth/register.html')

def logout_view(request):
    logout(request)
    return redirect('homepage')  # Replace 'home' with the URL to redirect after logout
