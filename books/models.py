from django.db import models
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError



class Author(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name
    

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.title
    

class FavoriteBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    favorites = models.ManyToManyField(Book, related_name="favorited_by", blank=True)

    def add_favorite(self, book):
        if self.favorites.count() >= 20:
            raise ValidationError("You cannot add more than 20 favorite books.")
        self.favorites.add(book)

    def remove_favorite(self, book):
        FavoriteBook.objects.filter(user=self, book=book).delete()

    def __str__(self) -> str:
        return f"{self.user.username}'s Favorite books."


