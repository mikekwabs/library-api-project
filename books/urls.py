from django.urls import path
from .views import BookCreateView,BookDeleteView, BookDetailView, BookListView, BookUpdateView, RegisterView, LoginView, AuthorListView, AuthorDetailView, AuthorCreateView, AuthorDeleteView, AuthorUpdateView, AddFavoriteBookView,RemoveFavoriteBookView, ListFavoriteBooksView

urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"), #POST /register
    path('login/',LoginView.as_view(), name="login"), #POST /login
    path('books/', BookListView.as_view(), name="books-list"), #Retrieve all books
    path('books/<int:id>/', BookDetailView.as_view(), name="book-detail"),
    path('books/create/', BookCreateView.as_view(), name="book-create"),
    path('books/<int:id>/update/', BookUpdateView.as_view(), name="book-update"),
    path('books/<int:id>/delete/', BookDeleteView.as_view(), name="book-delete") ,
    path('authors/', AuthorListView.as_view(), name="authors-list"), #Retrieve all authors
    path('authors/<int:id>/', AuthorDetailView.as_view(), name="author-detail"),
    path('authors/create/', AuthorCreateView.as_view(), name="author-create"),
    path('authors/<int:id>/update/', AuthorUpdateView.as_view(), name="author-update"),
    path('authors/<int:id>/delete/', AuthorDeleteView.as_view(), name="author-delete") ,
    path('favorites/add/', AddFavoriteBookView.as_view(), name="add-favorite"),
    path('favorites/', ListFavoriteBooksView.as_view(), name="favorites-list"),
    path('favorites/remove/<int:book_id>/', RemoveFavoriteBookView.as_view(), name='remove-favorite')

]
