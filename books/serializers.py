from rest_framework import serializers
from .models import Author,Book, FavoriteBook
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    author = serializers.CharField()

    class Meta:
        model = Book
        fields = '__all__'

    def create(self, validated_data):
        #After accepting name of author as string, we extract from the validated data.
        author_name = validated_data.pop('author')
        author, created = Author.objects.get_or_create(name=author_name) #Create or get the author
        book = Book.objects.create(author=author, **validated_data) #Create the book with author
        return book
    
    def update(self, instance, validated_data):
        author_name = validated_data.pop('author', None)
        if author_name:
            author, created = Author.objects.get_or_create(name=author_name)
            instance.author = author  #Set new author
        
        #Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        #Save updated instance
        instance.save()
        return instance


class FavoriteBookSerializer(serializers.ModelSerializer):
    favorites = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), many=True)

    class Meta:
        model = FavoriteBook
        fields = ['favorites']

    def validate(self, data):
        user = self.context['request'].user
        
        # Get or create the FavoriteBook instance for the user
        favorite_book_instance, created = FavoriteBook.objects.get_or_create(user=user)

        # Check the count of current favorites plus new favorites
        if favorite_book_instance.favorites.count() + len(data['favorites']) > 20:
            raise serializers.ValidationError("You can only have up to 20 favorite books.")
        
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        favorite_book_instance, created = FavoriteBook.objects.get_or_create(user=user)

        favorites = validated_data.get('favorites', [])
        
        for book in favorites:
            if favorite_book_instance.favorites.count() < 20:
                favorite_book_instance.favorites.add(book)
            else:
                raise serializers.ValidationError("You cannot add more than 20 favorite books.")
        
        favorite_book_instance.save()
        return favorite_book_instance
    
    