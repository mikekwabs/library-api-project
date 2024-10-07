from django.contrib.auth.models import User
from rest_framework import generics,permissions,status
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import BookSerializer,AuthorSerializer, UserSerializer
from books.models import Book, Author, FavoriteBook
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin,UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import FavoriteBookSerializer
from scripts.utils import get_book_recommendations

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny] #Allow anyone to register

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]  #Allow anyone to register

# GET /books/- get all books
class BookListView(generics.GenericAPIView, ListModelMixin):
    queryset = Book.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'author__name']  #Search by title or author name

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
# GET /books/:id - get an existing book
class BookDetailView(generics.GenericAPIView, RetrieveModelMixin):
    queryset = Book.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BookSerializer
    lookup_field = 'id'

    def get(self, request,*args, **kwargs):
        print(self.queryset)
        return self.retrieve(request, *args, **kwargs)

# POST /books - Create a new book (protected)
class BookCreateView(generics.GenericAPIView, CreateModelMixin):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self,request,*args, **kwargs):
        return self.create(request,*args, **kwargs)
    

# PUT /books/:id - Update an existing book (protected)
class BookUpdateView(generics.GenericAPIView,UpdateModelMixin):
    queryset = Book.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated] #Protect the endpoint
    serializer_class = BookSerializer
    lookup_field = 'id'

    def put(self,request,*args, **kwargs):
        return self.update(request, *args, **kwargs)

# DELETE /books/:id - Delete a book (protected)
class BookDeleteView(generics.GenericAPIView, DestroyModelMixin):
    queryset = Book.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated] #Protect the endpoint
    serializer_class = BookSerializer
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


#Views for Authors

# GET /authors/ - get all authors
class AuthorListView(generics.GenericAPIView, ListModelMixin):
    queryset = Author.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AuthorSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# GET /authors/:id - get an existing author
class AuthorDetailView(generics.GenericAPIView, RetrieveModelMixin):
    queryset = Author.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AuthorSerializer
    lookup_field = 'id'

    def get(self, request,*args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    

# POST /authors - Create a new author (protected)
class AuthorCreateView(generics.GenericAPIView, CreateModelMixin):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request,*args, **kwargs):
        return self.create(request,*args, **kwargs)
    

# PUT /authors/:id - Update an existing author (protected)
class AuthorUpdateView(generics.GenericAPIView,UpdateModelMixin):
    queryset = Author.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated] #Protect the endpoint
    serializer_class = AuthorSerializer
    lookup_field = 'id'

    def put(self,request,*args, **kwargs):
        return self.update(request, *args, **kwargs)
    

# DELETE /books/:id - Delete a book (protected)
class AuthorDeleteView(generics.GenericAPIView, DestroyModelMixin):
    queryset = Author.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated] #Protect the endpoint
    serializer_class = AuthorSerializer
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
#Recommendation
def get_recommendation(user, top_n=5):
    #Get the user's favorite books
    favorite_book_instance = FavoriteBook.objects.filter(user=user).prefetch_related('favorites').first()
    
    if not favorite_book_instance or favorite_book_instance.favorites.count() == 0:
        return []
    
    favorite_books = list(favorite_book_instance.favorites.all())

    #Get all books excluding the user's favorite
    all_books = list(Book.objects.exclude(id__in=[book.id for book in favorite_books]))

    if not all_books:
        return []

    #Get recommendation using the recommendation function
    recommended_books = get_book_recommendations(favorite_books, all_books, top_n=5)

    return recommended_books
   

#Favourites
class AddFavoriteBookView(generics.CreateAPIView):
    queryset = FavoriteBook.objects.all()
    serializer_class = FavoriteBookSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  #Authenticated user only can add to favorite


    def perform_create(self,serializer):
        #Save the favorite book for the autheticated user
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        #Call the paren's create method to handle logic
        response = super().create(request, *args, **kwargs)

        #Obtain recommendation after adding to favorite
        recommendations = get_recommendation(self.request.user, top_n=5)

        #Add the recommendation to the response
        response.data['recommendations'] = BookSerializer(recommendations, many=True).data

        return response
        
#Remove favourite
class RemoveFavoriteBookView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FavoriteBookSerializer

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        book_id = self.kwargs.get('book_id')  # Get book_id from the URL

        # Get the user's FavoriteBook instance
        try:
            favorite_book_instance = FavoriteBook.objects.get(user=user)
        except FavoriteBook.DoesNotExist:
            return Response({"detail": "No favorite list found for this user."}, status=status.HTTP_404_NOT_FOUND)

        # Find the book to remove
        try:
            book_to_remove = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

        # Remove the book if it's in the favorites
        if book_to_remove in favorite_book_instance.favorites.all():
            favorite_book_instance.favorites.remove(book_to_remove)
            favorite_book_instance.save()
            return Response({"detail": "Book removed from favorites."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "This book is not in your favorites."}, status=status.HTTP_400_BAD_REQUEST)

    

#List all favorites
class ListFavoriteBooksView(generics.ListAPIView, ListModelMixin):
    queryset = FavoriteBook.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FavoriteBookSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)