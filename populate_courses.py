import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from accounts.models import Course

courses_data = [
    {
        'title': 'Web Design & Development Course for Beginners',
        'price': 'Kshs50,000',
        'image': 'images/pics/web development.jpg',
        'duration': '2HRS',
        'instructor': 'KING\'S',
        'rating': 5.0,
        'reviews': 123,
        'description': 'Learn the basics of web design and development.'
    },
    {
        'title': 'Graphic Design Course for Beginners',
        'price': 'Kshs50,000',
        'image': 'images/pics/graphic design.jpg',
        'duration': '2HRS',
        'instructor': 'KING\'S',
        'rating': 5.0,
        'reviews': 123,
        'description': 'Master the art of graphic design.'
    },
    {
        'title': 'Video Editing Course for Beginners',
        'price': 'Kshs50,000',
        'image': 'images/pics/video editting.jpg',
        'duration': '2HRS',
        'instructor': 'KING\'S',
        'rating': 5.0,
        'reviews': 123,
        'description': 'Learn how to edit videos like a pro.'
    },
    {
        'title': 'Online Marketing Course for Beginners',
        'price': 'Kshs50,000',
        'image': 'images/pics/online marketing.jpg',
        'duration': '2HRS',
        'instructor': 'KING\'S',
        'rating': 5.0,
        'reviews': 123,
        'description': 'Understand the fundamentals of online marketing.'
    }
]

for data in courses_data:
    if not Course.objects.filter(title=data['title']).exists():
        Course.objects.create(**data)
        print(f"Created course: {data['title']}")
    else:
        print(f"Course already exists: {data['title']}")
