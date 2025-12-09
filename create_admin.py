import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from accounts.models import Student

email = 'admin@natureclub.com'
password = 'admin123'
fullname = 'System Administrator'

if not Student.objects.filter(email=email).exists():
    Student.objects.create(fullname=fullname, email=email, password=password, is_admin=True)
    print(f"SUCCESS: Admin account created.\nEmail: {email}\nPassword: {password}")
else:
    print(f"INFO: Admin account already exists for {email}")
    user = Student.objects.get(email=email)
    if not user.is_admin:
        user.is_admin = True
        user.save()
        print(f"SUCCESS: Updated existing user {email} to be an admin.")
