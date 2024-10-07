from django.contrib import admin
from .models import Book, FavoriteBook, Author


# Register your models here.

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', "author", "description")
    search_fields = ('title', 'author__name')


admin.site.register(Book, BookAdmin)
admin.site.register(Author)
admin.site.register(FavoriteBook)
