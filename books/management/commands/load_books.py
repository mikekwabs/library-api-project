import os
import django
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from books.models import Book, Author

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library.settings')
django.setup()




class Command(BaseCommand):
    help = 'Load books from JSON file into the database'

    def handle(self, *args, **kwargs):
        with open('C:/Users/HP/Desktop/django-spotter/scripts/filtered_books.json') as f:
            data = json.load(f)
            for book_data in data:
                    # Get or create the author
                    author, created = Author.objects.get_or_create(name=book_data['author'])

                    # Create the book instance
                    Book.objects.get_or_create(
                        title=book_data['title'],
                        author=author, 
                        description=book_data['description']
                    )
                    print(f"Book '{book_data['title']}' has been added.")

