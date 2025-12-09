import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from accounts.models import Course

course_data = {
    'title': 'Database Connectivity Test Course',
    'price': 'Free',
    'image': 'images/pics/web design.jpg', # Reusing an existing image
    'duration': '10 MINS',
    'instructor': 'System Admin',
    'rating': 5.0,
    'reviews': 1,
    'description': 'This is a test course to verify database connectivity.'
}

if not Course.objects.filter(title=course_data['title']).exists():
    Course.objects.create(**course_data)
    print(f"SUCCESS: Created course '{course_data['title']}'")
else:
    print(f"INFO: Course '{course_data['title']}' already exists")
