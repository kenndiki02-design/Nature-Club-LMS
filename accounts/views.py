from django.shortcuts import render, redirect
from .models import Student, Course

def register(request):
    message = ''
    if request.method == 'POST':
        fullname = request.POST['fullname']
        email = request.POST['email']
        password = request.POST['password']
        
        if Student.objects.filter(email=email).exists():
            message = 'Email already registered'
        else:
            Student.objects.create(fullname=fullname, email=email, password=password)
            message = 'Registration successful'
    return render(request, 'accounts/register.html', {'message': message})

def login(request):
    message = ''
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = Student.objects.filter(email=email, password=password).first()
    
        if user:
            request.session['user_id'] = user.id
            if user.is_admin:
                return redirect('admin_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            message = "Invalid email or password"
    return render(request, 'accounts/login.html', {'message': message})

def student_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user = Student.objects.filter(id=request.session['user_id']).first()
    if not user:
        request.session.flush()
        return redirect('login') 
    return render(request, 'student_dashboard.html', {'user': user, 'enrolled_courses': user.enrolled_courses.all()})

def admin_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user = Student.objects.filter(id=request.session['user_id']).first()
    if not user:
        request.session.flush()
        return redirect('login')

    if not user.is_admin:
        return redirect('student_dashboard')
    
    students = Student.objects.prefetch_related('enrolled_courses').all()
    return render(request, 'admin_dashboard.html', {'user': user, 'students': students})

def enroll(request, course_id):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user = Student.objects.filter(id=request.session['user_id']).first()
    if not user:
         request.session.flush()
         return redirect('login')

    course = Course.objects.filter(id=course_id).first()
    if course:
        user.enrolled_courses.add(course)
    
    return redirect('student_dashboard')

import re

def profile(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user = Student.objects.filter(id=request.session['user_id']).first()
    if not user:
        request.session.flush()
        return redirect('login') 

    message = ''
    error = ''

    if request.method == 'POST':
        user.fullname = request.POST['fullname']
        user.email = request.POST['email']
        user.phone = request.POST['phone']
        user.bio = request.POST['bio']

        # Validation
        if Student.objects.filter(email=user.email).exclude(id=user.id).exists():
            error = 'Email is already taken by another account.'
        elif user.phone and not re.match(r'^\+?1?\d{9,15}$', user.phone):
             error = 'Invalid phone number format. Use 10-15 digits.'
        else:
            user.save()
            message = 'Profile updated successfully'

    return render(request, 'profile.html', {'user': user, 'message': message, 'error': error})

def logout(request):
    request.session.flush()
    return redirect('home')

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def courses(request):
    courses = Course.objects.all()
    enrolled_course_ids = []
    if 'user_id' in request.session:
        user = Student.objects.filter(id=request.session['user_id']).first()
        if user:
            enrolled_course_ids = user.enrolled_courses.values_list('id', flat=True)
    
    return render(request, 'courses.html', {'courses': courses, 'enrolled_course_ids': enrolled_course_ids})

def team(request):
    return render(request, 'team.html')

def testimonial(request):
    return render(request, 'testimonial.html')

def error_404(request):
    return render(request, '404.html')