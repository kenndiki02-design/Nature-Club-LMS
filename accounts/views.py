import os
import uuid
import qrcode
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.conf import settings

# ReportLab imports for Certificate PDF
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Rect, String, Line

from .models import (
    Category, Course, Student, Lesson, DownloadableResource,
    Assignment, AssignmentSubmission, LiveClass, StudentCourseProgress,
    Certificate, Notification, Announcement, DiscussionForumMessage, CourseReview
)

# Helpers
def create_notification(user, message_text):
    Notification.objects.create(user=user, message=message_text)

# Base & Public Views
def home(request):
    featured_courses = Course.objects.filter(is_archived=False)[:3]
    announcements = Announcement.objects.all()[:4]
    
    # Statistics
    total_students = User.objects.filter(student__role='student').count()
    total_instructors = User.objects.filter(student__role='instructor', student__status='active').count()
    total_courses = Course.objects.filter(is_archived=False).count()
    
    # Reviews
    reviews = CourseReview.objects.order_by('-created_at')[:4]
    
    context = {
        'featured_courses': featured_courses,
        'announcements': announcements,
        'total_students': total_students if total_students else 150,
        'total_instructors': total_instructors if total_instructors else 15,
        'total_courses': total_courses if total_courses else 5,
        'reviews': reviews,
    }
    return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        messages.success(request, f"Thank you, {name}! Your message has been sent successfully.")
        return redirect('contact')
    return render(request, 'contact.html')

def team(request):
    return render(request, 'team.html')

def testimonial(request):
    reviews = CourseReview.objects.order_by('-created_at')[:8]
    return render(request, 'testimonial.html', {'reviews': reviews})

def error_404(request):
    return render(request, '404.html')

# Authentication
def register(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    message = ''
    if request.method == 'POST':
        fullname = request.POST.get('fullname', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password', '')
        role = request.POST.get('role', 'student')
        
        first, last = fullname.split(" ", 1) if " " in fullname else (fullname, "")
        
        if User.objects.filter(username=email).exists():
            message = "Email is already registered"
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first,
                last_name=last
            )
            
            # Setup initial status
            status = 'pending_approval' if role == 'instructor' else 'active'
            
            student_profile = Student.objects.create(
                user=user,
                role=role,
                status=status,
                phone=phone
            )
            
            if role == 'instructor':
                message = "Registration successful! Your instructor account is pending approval by the administrator."
                messages.info(request, message)
                return redirect('login')
            else:
                auth_login(request, user)
                create_notification(user, "Welcome to Karatina University Nature Club LMS! Check out our courses.")
                return redirect('student_dashboard')
                
    return render(request, 'accounts/register.html', {'message': message})

def login(request):
    if request.user.is_authenticated:
        profile = getattr(request.user, 'student', None)
        if profile:
            if profile.role == 'admin' or request.user.is_superuser:
                return redirect('admin_dashboard')
            elif profile.role == 'instructor':
                return redirect('instructor_dashboard')
            else:
                return redirect('student_dashboard')
                
    message = ''
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            profile, created = Student.objects.get_or_create(user=user)
            
            if profile.status == 'suspended':
                message = "Your account has been suspended. Please contact the administrator."
            elif profile.status == 'pending_approval':
                message = "Your instructor registration is still pending administrator approval."
            else:
                auth_login(request, user)
                if profile.role == 'admin' or user.is_superuser:
                    return redirect('admin_dashboard')
                elif profile.role == 'instructor':
                    return redirect('instructor_dashboard')
                else:
                    return redirect('student_dashboard')
        else:
            message = "Invalid email or password"
            
    return render(request, 'accounts/login.html', {'message': message})

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home')

# Profiles
@login_required
def profile(request):
    student = request.user.student
    message = ''
    error = ''
    
    if request.method == 'POST':
        fullname = request.POST.get('fullname', '')
        phone = request.POST.get('phone', '')
        bio = request.POST.get('bio', '')
        profile_pic = request.FILES.get('profile_picture')
        
        first, last = fullname.split(" ", 1) if " " in fullname else (fullname, "")
        request.user.first_name = first
        request.user.last_name = last
        request.user.save()
        
        student.phone = phone
        student.bio = bio
        if profile_pic:
            student.profile_picture = profile_pic
        student.save()
        
        message = "Profile updated successfully!"
        
    return render(request, 'profile.html', {
        'user': student,
        'message': message,
        'error': error
    })

# Courses Listing
def courses(request):
    query = request.GET.get('q')
    category_slug = request.GET.get('category')
    
    courses_qs = Course.objects.filter(is_archived=False)
    if query:
        courses_qs = courses_qs.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category_slug:
        courses_qs = courses_qs.filter(category__slug=category_slug)
        
    categories = Category.objects.all()
    
    enrolled_course_ids = []
    if request.user.is_authenticated:
        enrolled_course_ids = request.user.student.enrolled_courses.values_list('id', flat=True)
        
    return render(request, 'courses.html', {
        'courses': courses_qs,
        'categories': categories,
        'enrolled_course_ids': enrolled_course_ids,
        'query': query
    })

@login_required
def enroll(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = request.user.student
    if student.role == 'student':
        student.enrolled_courses.add(course)
        course.enrolled_students.add(request.user)
        # Initialize Progress
        StudentCourseProgress.objects.get_or_create(student=request.user, course=course)
        create_notification(request.user, f"Successfully enrolled in course: {course.title}")
        messages.success(request, f"You have successfully enrolled in {course.title}!")
        return redirect('student_dashboard')
    else:
        messages.error(request, "Only students can enroll in courses.")
        return redirect('courses')

# Student Dashboard
@login_required
def student_dashboard(request):
    student = request.user.student
    if student.role != 'student':
        return redirect('home')
        
    enrolled_courses = student.enrolled_courses.all()
    
    # Calculate progress details
    course_details = []
    for c in enrolled_courses:
        progress, created = StudentCourseProgress.objects.get_or_create(student=request.user, course=c)
        course_details.append({
            'course': c,
            'progress': progress.progress_percentage,
            'last_lesson': progress.last_accessed_lesson
        })
        
    upcoming_assignments = Assignment.objects.filter(
        course__in=enrolled_courses,
        deadline__gte=timezone.now()
    ).order_by('deadline')
    
    notifications = Notification.objects.filter(user=request.user)[:10]
    
    upcoming_live = LiveClass.objects.filter(
        course__in=enrolled_courses,
        scheduled_time__gte=timezone.now()
    ).order_by('scheduled_time')
    
    certificates = Certificate.objects.filter(student=request.user)
    
    # Stats
    total_completed = 0
    for details in course_details:
        if details['progress'] == 100:
            total_completed += 1
            
    context = {
        'student': student,
        'course_details': course_details,
        'upcoming_assignments': upcoming_assignments,
        'notifications': notifications,
        'upcoming_live': upcoming_live,
        'certificates': certificates,
        'total_completed': total_completed,
    }
    return render(request, 'student_dashboard.html', context)

# Course Portal Detail View
@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = request.user.student
    
    # Verification of access
    has_access = False
    if student.role == 'admin' or request.user.is_superuser:
        has_access = True
    elif student.role == 'instructor' and course.instructor == request.user:
        has_access = True
    elif student.role == 'student' and course in student.enrolled_courses.all():
        has_access = True
        
    if not has_access:
        messages.error(request, "You do not have access to this course portal.")
        return redirect('courses')
        
    lessons = course.lessons.all().order_by('order')
    resources = course.resources.all()
    assignments = course.assignments.all()
    live_classes = course.live_classes.all()
    reviews = course.reviews.all().order_by('-created_at')
    forum_messages = course.forum_messages.all().order_by('created_at')
    
    # Active lesson
    lesson_id = request.GET.get('lesson')
    active_lesson = None
    if lesson_id:
        active_lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    elif lessons.exists():
        active_lesson = lessons.first()
        
    # Student specific details
    progress = None
    completed_lesson_ids = []
    assignment_submissions = {}
    
    if student.role == 'student':
        progress, _ = StudentCourseProgress.objects.get_or_create(student=request.user, course=course)
        if active_lesson:
            progress.last_accessed_lesson = active_lesson
            progress.save()
        completed_lesson_ids = progress.completed_lessons.values_list('id', flat=True)
        
        # Submissions
        for assignment in assignments:
            sub = AssignmentSubmission.objects.filter(assignment=assignment, student=request.user).first()
            assignment_submissions[assignment.id] = sub

    context = {
        'course': course,
        'lessons': lessons,
        'resources': resources,
        'assignments': assignments,
        'live_classes': live_classes,
        'reviews': reviews,
        'forum_messages': forum_messages,
        'active_lesson': active_lesson,
        'progress': progress,
        'completed_lesson_ids': completed_lesson_ids,
        'assignment_submissions': assignment_submissions,
        'role': student.role,
    }
    return render(request, 'course_detail.html', context)

# Student actions inside course
@login_required
def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course
    student = request.user.student
    
    if student.role == 'student':
        progress, _ = StudentCourseProgress.objects.get_or_create(student=request.user, course=course)
        progress.completed_lessons.add(lesson)
        
        # Trigger certificate generation if 100% completed
        if progress.progress_percentage == 100:
            cert_num = f"KU-NC-{course.id}-{request.user.id}-{uuid.uuid4().hex[:6].upper()}"
            Certificate.objects.get_or_create(
                student=request.user,
                course=course,
                defaults={'certificate_number': cert_num}
            )
            create_notification(request.user, f"Congratulations! You completed the course '{course.title}' and earned a certificate!")
            messages.success(request, f"Congratulations! You have completed '{course.title}' and generated your certificate.")
            
        return redirect(f"/courses/{course.id}/?lesson={lesson.id}")
    return redirect('courses')

@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.method == 'POST':
        file_up = request.FILES.get('file')
        text_sub = request.POST.get('text_submission', '')
        
        # Check if already submitted
        submission, created = AssignmentSubmission.objects.get_or_create(
            assignment=assignment,
            student=request.user
        )
        submission.file = file_up
        submission.text_submission = text_sub
        submission.submitted_at = timezone.now()
        submission.marks_obtained = None  # Reset grade upon resubmission
        submission.feedback = ''
        submission.save()
        
        # Notify instructor
        if assignment.course.instructor:
            create_notification(assignment.course.instructor, f"Student {request.user.student.fullname} submitted assignment '{assignment.title}'")
            
        messages.success(request, f"Assignment '{assignment.title}' submitted successfully.")
        return redirect(f"/courses/{assignment.course.id}/")
    return redirect('courses')

@login_required
def post_forum_message(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        msg = request.POST.get('message', '')
        if msg:
            DiscussionForumMessage.objects.create(
                course=course,
                user=request.user,
                message=msg
            )
    return redirect(f"/courses/{course.id}/")

@login_required
def add_review(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        rating = request.POST.get('rating', 5)
        review_text = request.POST.get('review_text', '')
        
        CourseReview.objects.update_or_create(
            course=course,
            student=request.user,
            defaults={'rating': int(rating), 'review_text': review_text}
        )
        
        # Update course average rating & reviews count
        all_reviews = course.reviews.all()
        course.rating = all_reviews.aggregate(Avg('rating'))['rating__avg'] or 5.0
        course.reviews = all_reviews.count()
        course.save()
        
        messages.success(request, "Review submitted successfully.")
    return redirect(f"/courses/{course.id}/")

# Instructor Dashboard
@login_required
def instructor_dashboard(request):
    student = request.user.student
    if student.role != 'instructor':
        return redirect('home')
        
    instructed_courses = Course.objects.filter(instructor=request.user)
    
    # Calculate stats
    total_students = Student.objects.filter(enrolled_courses__in=instructed_courses).distinct().count()
    
    # Submissions pending grading
    pending_submissions = AssignmentSubmission.objects.filter(
        assignment__course__in=instructed_courses,
        marks_obtained__isnull=True
    ).order_by('submitted_at')
    
    # Recent Activities
    notifications = Notification.objects.filter(user=request.user)[:10]
    
    # Categories for Course Creation Form
    categories = Category.objects.all()
    
    context = {
        'courses': instructed_courses,
        'total_students': total_students,
        'pending_submissions': pending_submissions,
        'notifications': notifications,
        'categories': categories,
    }
    return render(request, 'instructor_dashboard.html', context)

# Instructor Actions
@login_required
def instructor_add_course(request):
    student = request.user.student
    if student.role != 'instructor':
        return redirect('home')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price', 'Free')
        duration = request.POST.get('duration')
        difficulty = request.POST.get('difficulty', 'Beginner')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')
        
        category = get_object_or_404(Category, id=category_id) if category_id else None
        
        Course.objects.create(
            title=title,
            description=description,
            price=price,
            duration=duration,
            difficulty=difficulty,
            instructor=request.user,
            category=category,
            image=image
        )
        messages.success(request, f"Course '{title}' created successfully!")
    return redirect('instructor_dashboard')

@login_required
def instructor_edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        course.title = request.POST.get('title')
        course.description = request.POST.get('description')
        course.price = request.POST.get('price', 'Free')
        course.duration = request.POST.get('duration')
        course.difficulty = request.POST.get('difficulty')
        category_id = request.POST.get('category')
        if category_id:
            course.category = get_object_or_404(Category, id=category_id)
        image = request.FILES.get('image')
        if image:
            course.image = image
        course.save()
        messages.success(request, f"Course '{course.title}' updated successfully!")
    return redirect('instructor_dashboard')

@login_required
def instructor_archive_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    course.is_archived = True
    course.save()
    messages.success(request, f"Course '{course.title}' has been archived.")
    return redirect('instructor_dashboard')

@login_required
def instructor_add_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content', '')
        video_url = request.POST.get('video_url', '')
        order = request.POST.get('order', 0)
        
        Lesson.objects.create(
            course=course,
            title=title,
            content=content,
            video_url=video_url,
            order=int(order)
        )
        messages.success(request, f"Lesson '{title}' added to course.")
    return redirect(f"/courses/{course.id}/")

@login_required
def instructor_add_resource(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES.get('file')
        
        DownloadableResource.objects.create(
            course=course,
            title=title,
            file=file
        )
        messages.success(request, f"Resource '{title}' uploaded successfully.")
    return redirect(f"/courses/{course.id}/")

@login_required
def instructor_add_assignment(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        deadline_str = request.POST.get('deadline')
        max_marks = request.POST.get('max_marks', 100)
        
        deadline = timezone.datetime.fromisoformat(deadline_str) if deadline_str else timezone.now()
        
        Assignment.objects.create(
            course=course,
            title=title,
            description=description,
            deadline=deadline,
            max_marks=int(max_marks)
        )
        messages.success(request, f"Assignment '{title}' added.")
    return redirect(f"/courses/{course.id}/")

@login_required
def instructor_add_live(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        meeting_link = request.POST.get('meeting_link')
        scheduled_str = request.POST.get('scheduled_time')
        
        scheduled_time = timezone.datetime.fromisoformat(scheduled_str) if scheduled_str else timezone.now()
        
        LiveClass.objects.create(
            course=course,
            title=title,
            meeting_link=meeting_link,
            scheduled_time=scheduled_time
        )
        messages.success(request, f"Live class link for '{title}' added successfully.")
    return redirect(f"/courses/{course.id}/")

@login_required
def instructor_grade_submission(request, submission_id):
    submission = get_object_or_404(AssignmentSubmission, id=submission_id, assignment__course__instructor=request.user)
    if request.method == 'POST':
        marks = request.POST.get('marks_obtained')
        feedback = request.POST.get('feedback', '')
        
        submission.marks_obtained = int(marks)
        submission.feedback = feedback
        submission.graded_at = timezone.now()
        submission.graded_by = request.user
        submission.save()
        
        create_notification(submission.student, f"Your submission for assignment '{submission.assignment.title}' has been graded. Marks: {marks}/{submission.assignment.max_marks}")
        messages.success(request, f"Graded student submission successfully.")
        
    return redirect('instructor_dashboard')

# Admin Dashboard
@login_required
def admin_dashboard(request):
    if not request.user.student.is_admin and not request.user.is_superuser:
        return redirect('student_dashboard')
        
    students = Student.objects.filter(role='student')
    instructors = Student.objects.filter(role='instructor')
    pending_approvals = Student.objects.filter(role='instructor', status='pending_approval')
    
    courses_qs = Course.objects.all()
    categories = Category.objects.all()
    
    # Stats
    total_students = students.count()
    total_instructors = instructors.filter(status='active').count()
    total_pending = pending_approvals.count()
    total_courses = courses_qs.filter(is_archived=False).count()
    total_completed = StudentCourseProgress.objects.filter(completed_lessons__isnull=False).distinct().count() # estimate
    total_submissions = AssignmentSubmission.objects.count()
    total_certificates = Certificate.objects.count()
    
    # Admin context
    context = {
        'students': students,
        'instructors': instructors,
        'pending_approvals': pending_approvals,
        'courses': courses_qs,
        'categories': categories,
        'total_students': total_students,
        'total_instructors': total_instructors,
        'total_pending': total_pending,
        'total_courses': total_courses,
        'total_completed': total_completed,
        'total_submissions': total_submissions,
        'total_certificates': total_certificates,
    }
    return render(request, 'admin_dashboard.html', context)

# Admin actions
@login_required
def admin_approve_instructor(request, user_id):
    if not request.user.student.is_admin and not request.user.is_superuser:
        return redirect('student_dashboard')
        
    profile = get_object_or_404(Student, id=user_id, role='instructor')
    profile.status = 'active'
    profile.save()
    
    create_notification(profile.user, "Your instructor account has been approved by the administrator. You can now log in.")
    messages.success(request, f"Approved instructor application for {profile.fullname}.")
    return redirect('admin_dashboard')

@login_required
def admin_reject_instructor(request, user_id):
    if not request.user.student.is_admin and not request.user.is_superuser:
        return redirect('student_dashboard')
        
    profile = get_object_or_404(Student, id=user_id, role='instructor')
    profile.status = 'suspended'  # set to suspended/rejected
    profile.save()
    messages.warning(request, f"Rejected instructor application for {profile.fullname}.")
    return redirect('admin_dashboard')

@login_required
def admin_suspend_user(request, user_id):
    if not request.user.student.is_admin and not request.user.is_superuser:
        return redirect('student_dashboard')
        
    profile = get_object_or_404(Student, id=user_id)
    profile.status = 'suspended'
    profile.save()
    messages.success(request, f"Suspended account: {profile.fullname}.")
    return redirect('admin_dashboard')

@login_required
def admin_unsuspend_user(request, user_id):
    if not request.user.student.is_admin and not request.user.is_superuser:
        return redirect('student_dashboard')
        
    profile = get_object_or_404(Student, id=user_id)
    profile.status = 'active'
    profile.save()
    messages.success(request, f"Activated account: {profile.fullname}.")
    return redirect('admin_dashboard')

@login_required
def admin_delete_user(request, user_id):
    if not request.user.student.is_admin and not request.user.is_superuser:
        return redirect('student_dashboard')
        
    profile = get_object_or_404(Student, id=user_id)
    user = profile.user
    user.delete() # Cascade will delete the profile
    messages.success(request, f"Deleted user account.")
    return redirect('admin_dashboard')

@login_required
def admin_add_course(request):
    if not request.user.student.is_admin and not request.user.is_superuser:
        return redirect('student_dashboard')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price', 'Free')
        duration = request.POST.get('duration')
        difficulty = request.POST.get('difficulty', 'Beginner')
        category_id = request.POST.get('category')
        instructor_id = request.POST.get('instructor')
        image = request.FILES.get('image')
        
        category = get_object_or_404(Category, id=category_id) if category_id else None
        instructor = get_object_or_404(User, id=instructor_id) if instructor_id else None
        
        Course.objects.create(
            title=title,
            description=description,
            price=price,
            duration=duration,
            difficulty=difficulty,
            instructor=instructor,
            category=category,
            image=image
        )
        messages.success(request, f"Course '{title}' created successfully!")
    return redirect('admin_dashboard')

@login_required
def admin_edit_course(request, course_id):
    if not request.user.student.is_admin and not request.user.is_superuser:
        return redirect('student_dashboard')
        
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.title = request.POST.get('title')
        course.description = request.POST.get('description')
        course.price = request.POST.get('price', 'Free')
        course.duration = request.POST.get('duration')
        course.difficulty = request.POST.get('difficulty')
        category_id = request.POST.get('category')
        if category_id:
            course.category = get_object_or_404(Category, id=category_id)
        instructor_id = request.POST.get('instructor')
        if instructor_id:
            course.instructor = get_object_or_404(User, id=instructor_id)
        image = request.FILES.get('image')
        if image:
            course.image = image
        course.save()
        messages.success(request, f"Course '{course.title}' updated successfully!")
    return redirect('admin_dashboard')

@login_required
def admin_delete_course(request, course_id):
    if not request.user.student.is_admin and not request.user.is_superuser:
        return redirect('student_dashboard')
        
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    messages.success(request, "Course deleted successfully.")
    return redirect('admin_dashboard')

@login_required
def admin_add_announcement(request):
    if not request.user.student.is_admin and not request.user.is_superuser:
        return redirect('student_dashboard')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        Announcement.objects.create(title=title, content=content)
        messages.success(request, "Announcement added successfully!")
    return redirect('admin_dashboard')


# Certificate Verification Page
def verify_certificate(request, certificate_number=None):
    query = certificate_number or request.GET.get('cert_number')
    certificate = None
    searched = False
    
    if query:
        searched = True
        certificate = Certificate.objects.filter(
            Q(certificate_number__iexact=query) | Q(verification_uuid__hex__iexact=query.replace('-', ''))
        ).first()
        
    return render(request, 'verify_certificate.html', {
        'certificate': certificate,
        'query': query,
        'searched': searched
    })

# ReportLab PDF Certificate Generator
@login_required
def download_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id)
    
    # Security check: must be student who earned it, or admin/instructor
    if certificate.student != request.user and not request.user.student.is_admin and not request.user.is_superuser:
        raise Http404("You do not have permission to download this certificate.")
        
    # Generate QR Code representing the verification URL
    domain = request.get_host()
    proto = 'https' if request.is_secure() else 'http'
    verify_url = f"{proto}://{domain}/verify/{certificate.verification_uuid}/"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=1)
    qr.add_data(verify_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code image to BytesIO
    qr_io = BytesIO()
    qr_img.save(qr_io, format='PNG')
    qr_io.seek(0)
    
    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Certificate-{certificate.certificate_number}.pdf"'
    
    # Set up landscape letter page template
    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(letter),
        leftMargin=0.5*inch, rightMargin=0.5*inch,
        topMargin=0.5*inch, bottomMargin=0.5*inch
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Define custom certificate styles
    title_style = ParagraphStyle(
        'CertTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#1b4332'),  # Forest Green
        alignment=1, # Center
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CertSubtitle',
        parent=styles['Normal'],
        fontName='Times-BoldItalic',
        fontSize=28,
        textColor=colors.HexColor('#40916c'),  # Light green accent
        alignment=1, # Center
        spaceAfter=25
    )
    
    body_style = ParagraphStyle(
        'CertBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=15,
        textColor=colors.HexColor('#2d3142'),
        alignment=1, # Center
        leading=22,
        spaceAfter=10
    )
    
    student_style = ParagraphStyle(
        'CertStudent',
        parent=styles['Normal'],
        fontName='Times-BoldItalic',
        fontSize=26,
        textColor=colors.HexColor('#1b4332'),
        alignment=1,
        spaceAfter=10
    )
    
    course_style = ParagraphStyle(
        'CertCourse',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#40916c'),
        alignment=1,
        spaceAfter=20
    )
    
    sign_label_style = ParagraphStyle(
        'CertSignLabel',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.HexColor('#2d3142'),
        alignment=1
    )
    
    sign_style = ParagraphStyle(
        'CertSign',
        parent=styles['Normal'],
        fontName='Times-BoldItalic',
        fontSize=22,
        textColor=colors.HexColor('#1b4332'),
        alignment=1
    )
    
    verify_style = ParagraphStyle(
        'CertVerify',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#6c757d'),
        alignment=0 # Left
    )

    # Elements in flowable story
    story.append(Spacer(1, 0.6 * inch))
    story.append(Paragraph("KARATINA UNIVERSITY NATURE CLUB", title_style))
    story.append(Paragraph("Certificate of Completion", subtitle_style))
    story.append(Paragraph("This is to certify that", body_style))
    story.append(Paragraph(certificate.student.student.fullname, student_style))
    story.append(Paragraph("has successfully completed all requirements for the course", body_style))
    story.append(Paragraph(certificate.course.title, course_style))
    story.append(Paragraph(f"on this day {certificate.issued_date.strftime('%B %d, %Y')}", body_style))
    story.append(Spacer(1, 0.4 * inch))
    
    # Signature & QR Code Table
    # Left: QR Code & Verification info
    # Center: Ken Ndiki (Chairperson)
    # Right: Brian Kiprayan (Editor)
    
    # Inline QR image drawing
    from reportlab.platypus import Image as FlowableImage
    qr_flowable = FlowableImage(qr_io, width=1.1*inch, height=1.1*inch)
    
    verify_text = f"<b>Certificate No:</b><br/>{certificate.certificate_number}<br/><b>Verification URL:</b><br/>{verify_url}"
    verify_p = Paragraph(verify_text, verify_style)
    
    # Left side sub-table
    left_table = Table([[qr_flowable, verify_p]], colWidths=[1.2*inch, 2.3*inch])
    left_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    
    # Signatures
    sig_kn = Paragraph("<i>KN</i>", sign_style)
    sig_kn_label = Paragraph("<font size=12><b>Ken Ndiki</b></font><br/>Chairperson", sign_label_style)
    
    sig_bk = Paragraph("<i>BK</i>", sign_style)
    sig_bk_label = Paragraph("<font size=12><b>Brian Kiprayan</b></font><br/>Editor", sign_label_style)
    
    # Table layout
    data = [
        [left_table, sig_kn, sig_bk],
        ['', sig_kn_label, sig_bk_label]
    ]
    
    table = Table(data, colWidths=[3.7*inch, 3.1*inch, 3.1*inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('LINEBELOW', (1,0), (1,0), 1, colors.HexColor('#1b4332')),
        ('LINEBELOW', (2,0), (2,0), 1, colors.HexColor('#1b4332')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    
    story.append(table)
    
    # Draw Elegant Nature Border
    def draw_border(canvas, doc):
        canvas.saveState()
        # Page size: landscape letter is 11 inch x 8.5 inch (792 pt x 612 pt)
        width, height = 792, 612
        
        # Forest green background border (outer)
        canvas.setStrokeColor(colors.HexColor('#1b4332'))
        canvas.setLineWidth(12)
        canvas.rect(15, 15, width - 30, height - 30)
        
        # Light green inner decorative line
        canvas.setStrokeColor(colors.HexColor('#52b788'))
        canvas.setLineWidth(2)
        canvas.rect(26, 26, width - 52, height - 52)
        
        # Tiny earth-tone gold/bronze innermost frame line
        canvas.setStrokeColor(colors.HexColor('#d8a47f'))
        canvas.setLineWidth(1)
        canvas.rect(32, 32, width - 64, height - 64)
        
        # Add decorative corner elements (leaf accents or shapes)
        # Top-left corner design
        canvas.setFillColor(colors.HexColor('#1b4332'))
        canvas.rect(32, height - 50, 18, 18, fill=True, stroke=False)
        # Top-right corner design
        canvas.rect(width - 50, height - 50, 18, 18, fill=True, stroke=False)
        # Bottom-left corner design
        canvas.rect(32, 32, 18, 18, fill=True, stroke=False)
        # Bottom-right corner design
        canvas.rect(width - 50, 32, 18, 18, fill=True, stroke=False)
        
        canvas.restoreState()
        
    doc.build(story, onFirstPage=draw_border)
    return response