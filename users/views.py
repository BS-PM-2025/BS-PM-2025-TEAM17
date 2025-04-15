from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .models import User
from .form import RegisterUserForm
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

#import our user model and our RegistercUsercForm
# Create your views here.


#register student only(done : omar)


def register_student(request):
    if request.method=='POST':
        form=RegisterUserForm(request.POST)
        if form.is_valid():
            var=form.save(commit=False)
            var.is_student=True
            var.username=var.email
            #the username became automaticly the email
            var.save()
            messages.info(request,'Your acoount has been created...')
            return redirect('login')
        else:
            messages.warning(request,'something went wrong')
            return redirect('register-student')
    else:
        form=RegisterUserForm()
        contex={'form':form}
        return render( request,'users/register_student.html',contex)
    

#register lect only(done : omar)
    
def register_lect(request):
    if request.method=='POST':
        form=RegisterUserForm(request.POST)
        if form.is_valid():
            var=form.save(commit=False)
            var.is_lect=True
            var.username=var.email
            var.save() 
            #Donoractive.objects.create(user=var)
            messages.info(request,'Your acoount has been created,please login')
            return redirect('login')
        else:
            messages.warning(request,'something went wrong')
            return redirect('register-lect')
    else:
        form=RegisterUserForm()
        contex={'form':form}
        return render( request,'users/register_lect.html',contex)


#user login(done : omar)
def login_user(request):
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('password')

        user=authenticate(request,username=email,password=password)
        if user is not None and user.is_active:
            login(request,user)
            return redirect('dashboard')
        else:
            messages.warning(request,'somthing went wrong')
            return redirect('login')
    else:
        return render(request,'users/login.html')
    


#11
##user logout(to-do : Nashaat)
##user can logout so he end his session
def logout_user(request):
    logout(request)
    messages.info(request,'your session has ended')
    return redirect('login')


@require_POST
def add_user(request):
    # Sprint 2-Hassan
    email = request.POST.get('email')
    password = request.POST.get('password')
    role = request.POST.get('role')

    if User.objects.filter(email=email).exists():
        messages.error(request, 'User already exists.')
    else:
        user = User.objects.create(
            email=email,
            username=email,
            password=make_password(password),
            is_student=role == 'student',
            is_lect=role == 'lecturer',
            is_superuser=role == 'superuser',
        )
        messages.success(request, 'User created successfully.')
    return redirect('dashboard')

# to -do : Elias
@require_POST
def delete_user(request):
    # to -do : Elias
    
    return redirect('dashboard')

@require_POST
def change_user_role(request):
    #done : omar
    user_id = request.POST.get('user_id')
    role = request.POST.get('role')
    try:
        user = User.objects.get(id=user_id)
        user.is_student = role == 'student'
        user.is_lect = role == 'lecturer'
        user.is_superuser = role == 'superuser'
        user.save()
        messages.success(request, 'Role updated.')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    return redirect('dashboard')

            
            







    
 
