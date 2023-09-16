from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from .tokens import generate_token
from django.core.mail import EmailMessage
from django.conf import settings

# Create your views here.
def home(request):
    return render(request,'home.html')

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        user = User.objects.create_user(username,email,pass1)
        user.first_name=fname
        user.last_name=lname
        user.is_active = False
        user.save()


        messages.success(request,"your account has been succesfully created")

        #email
        current_site = get_current_site(request)
        subject = 'Confirm your email @ saviour developers'
        message = render_to_string('email.html',{
            "name": username,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": generate_token.make_token(user)
        })
        email = EmailMessage(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email]
        )

        email.fail_silently=True
        email.send()

        return redirect('login')
        
    return render(request,'authentication/signup.html')

def activate(request, uid64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid64))
        user = User.objects.get(pk = uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None

    if user is not None and generate_token.check_token(user,token):
        user.is_active = True
        user.save()
        login(request,user)
        return redirect('home')
    else:
        return render(request, 'failed.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass1')

        user1 = authenticate(username = username ,password = pass1)

        if user1 is not None:
            login(request, user1)
            fname = user1.first_name
            messages.success(request,"you've logged in succesfully")
            return render(request,"index.html",{'fname':fname})
        
        else:
            messages.error(request,"bad credentials")
            return redirect('login')
        
    return render(request,'authentication/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')