import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BitPin.settings")
import django

django.setup()

from Content.models import User, Content


def create_users(num_users=1000):
    users = [User(user_name=f"user_{i}") for i in range(num_users)]
    User.objects.bulk_create(users)
    print(f"{num_users} users created.")


def create_contents(num_contents=100):
    contents = [
        Content(title=f"Content Title {i}", content=f"This is the content body for Content {i}.")
        for i in range(num_contents)
    ]
    Content.objects.bulk_create(contents)
    print(f"{num_contents} contents created.")


if __name__ == "__main__":
    # number of users and contents
    create_users(num_users=1000)
    create_contents(num_contents=100)