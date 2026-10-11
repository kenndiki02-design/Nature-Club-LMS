import uuid
from django.db import models
from django.contrib.auth.models import User

# Category for Courses
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

# Course model
class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.CharField(max_length=50, default='Free')
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    image_static_path = models.CharField(max_length=200, blank=True, null=True) # Fallback to static
    duration = models.CharField(max_length=50)
    difficulty = models.CharField(
        max_length=50, 
        choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')], 
        default='Beginner'
    )
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'student__role': 'instructor'}, related_name='instructed_courses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    enrolled_students = models.ManyToManyField(User, related_name='enrolled_courses_list', blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        if self.image_static_path:
            return f"/static/{self.image_static_path}"
        return "/static/images/pics/logo.png"

# Student / User Profile Model (we keep the name Student to preserve request.user.student compatibility)
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    role = models.CharField(
        max_length=20, 
        choices=[('student', 'Student'), ('instructor', 'Instructor'), ('admin', 'Administrator')], 
        default='student'
    )
    status = models.CharField(
        max_length=20, 
        choices=[('active', 'Active'), ('suspended', 'Suspended'), ('pending_approval', 'Pending Approval')], 
        default='active'
    )
    enrolled_courses = models.ManyToManyField('Course', blank=True, related_name='students_enrolled')
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def email(self):
        return self.user.email

    @property
    def fullname(self):
        return f"{self.user.first_name} {self.user.last_name}" if (self.user.first_name or self.user.last_name) else self.user.username

    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_superuser

# Lesson Model
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True) # Text notes
    video_url = models.URLField(blank=True, null=True) # Watch video lessons
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

# Downloadable resource
class DownloadableResource(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='resources/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Assignment Model
class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    max_marks = models.PositiveIntegerField(default=100)

    def __str__(self):
        return self.title

# Assignment Submission
class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    text_submission = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_submissions')

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

# Live Class Model
class LiveClass(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='live_classes')
    title = models.CharField(max_length=200)
    meeting_link = models.URLField()
    scheduled_time = models.DateTimeField()

    def __str__(self):
        return self.title

# Student Course Progress
class StudentCourseProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed_lessons = models.ManyToManyField(Lesson, blank=True)
    last_accessed_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='last_accessed_by')
    last_accessed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

    @property
    def progress_percentage(self):
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            return 0
        completed = self.completed_lessons.count()
        return int((completed / total_lessons) * 100)

# Certificate Model
class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    certificate_number = models.CharField(max_length=100, unique=True)
    issued_date = models.DateField(auto_now_add=True)
    verification_uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.certificate_number})"

# Notification Model
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

# Announcement Model
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

# Discussion Forum Message
class DiscussionForumMessage(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='forum_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

# Course Review
class CourseReview(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.rating})"
