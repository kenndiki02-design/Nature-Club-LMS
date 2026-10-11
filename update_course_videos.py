import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from accounts.models import Course

# Mapping of course titles (or parts of titles) to YouTube URLs
video_links = {
    'Web Design': 'https://www.youtube.com/watch?v=B-ytMSuwbf8',
    'Graphic Design': 'https://www.youtube.com/watch?v=sTcuqb5K_jI',
    'Video Editing': 'https://www.youtube.com/watch?v=J3KjQ4c4X64',
    'Online Marketing': 'https://www.youtube.com/watch?v=nU-IIXJLjoM',
    'Database Connectivity': 'https://www.youtube.com/watch?v=HXV3zeQKqGY' # Placeholder for the test course
}

courses = Course.objects.all()

for course in courses:
    for key, url in video_links.items():
        if key in course.title:
            course.video_url = url
            course.save()
            print(f"Updated '{course.title}' with video: {url}")
            break
    else:
        print(f"No video link found for '{course.title}'")
