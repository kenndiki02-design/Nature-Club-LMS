from django.urls import path
from . import views

urlpatterns = [
    # Base Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('team/', views.team, name='team'),
    path('testimonial/', views.testimonial, name='testimonial'),
    
    # Authentication
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    
    # Dashboards
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('instructor-dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Courses
    path('courses/', views.courses, name='courses'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('enroll/<int:course_id>/', views.enroll, name='enroll'),
    
    # Student Actions
    path('lessons/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('assignments/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('forum/post/<int:course_id>/', views.post_forum_message, name='post_forum_message'),
    path('review/add/<int:course_id>/', views.add_review, name='add_review'),
    
    # Instructor Actions
    path('instructor/add-course/', views.instructor_add_course, name='instructor_add_course'),
    path('instructor/edit-course/<int:course_id>/', views.instructor_edit_course, name='instructor_edit_course'),
    path('instructor/archive-course/<int:course_id>/', views.instructor_archive_course, name='instructor_archive_course'),
    path('instructor/add-lesson/<int:course_id>/', views.instructor_add_lesson, name='instructor_add_lesson'),
    path('instructor/add-resource/<int:course_id>/', views.instructor_add_resource, name='instructor_add_resource'),
    path('instructor/add-assignment/<int:course_id>/', views.instructor_add_assignment, name='instructor_add_assignment'),
    path('instructor/add-live/<int:course_id>/', views.instructor_add_live, name='instructor_add_live'),
    path('instructor/grade-submission/<int:submission_id>/', views.instructor_grade_submission, name='instructor_grade_submission'),
    
    # Admin Actions
    path('admin/approve-instructor/<int:user_id>/', views.admin_approve_instructor, name='admin_approve_instructor'),
    path('admin/reject-instructor/<int:user_id>/', views.admin_reject_instructor, name='admin_reject_instructor'),
    path('admin/suspend-user/<int:user_id>/', views.admin_suspend_user, name='admin_suspend_user'),
    path('admin/unsuspend-user/<int:user_id>/', views.admin_unsuspend_user, name='admin_unsuspend_user'),
    path('admin/delete-user/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin/add-course/', views.admin_add_course, name='admin_add_course'),
    path('admin/edit-course/<int:course_id>/', views.admin_edit_course, name='admin_edit_course'),
    path('admin/delete-course/<int:course_id>/', views.admin_delete_course, name='admin_delete_course'),
    path('admin/add-announcement/', views.admin_add_announcement, name='admin_add_announcement'),
    
    # Certificate & Verification
    path('verify/', views.verify_certificate, name='verify_certificate_search'),
    path('verify/<str:certificate_number>/', views.verify_certificate, name='verify_certificate'),
    path('certificate/download/<int:certificate_id>/', views.download_certificate, name='download_certificate'),
]
