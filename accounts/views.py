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
    user = Student.objects.get(id=request.session['user_id'])
    return render(request, 'student_dashboard.html', {'user': user, 'enrolled_courses': user.enrolled_courses.all()})

def admin_dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')
    user = Student.objects.get(id=request.session['user_id'])
    if not user.is_admin:
        return redirect('student_dashboard')
    
    students = Student.objects.all()
    return render(request, 'admin_dashboard.html', {'user': user, 'students': students})

def enroll(request, course_id):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user = Student.objects.get(id=request.session['user_id'])
    course = Course.objects.get(id=course_id)
    
    user.enrolled_courses.add(course)
    return redirect('student_dashboard')

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
    return render(request, 'courses.html', {'courses': courses})

def team(request):
    return render(request, 'team.html')

def testimonial(request):
    return render(request, 'testimonial.html')

def error_404(request):
    return render(request, '404.html')