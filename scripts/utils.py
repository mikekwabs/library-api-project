from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def get_book_recommendations(favorite_books, all_books,top_n=5):
    #Extract title from the favorite books and all books
    favorite_titles = [book.title for book in favorite_books]
    all_titles = [book.title for book in all_books]

    #combine titles into one corpus
    combined_titles = favorite_titles + all_titles

    ## Use TF-IDF to vectorize the titles
    vectorizer = TfidfVectorizer().fit_transform(combined_titles)
    vectors = vectorizer.toarray()

    # Compute cosine similarity between favorite titles and all other titles
    favorite_vectors = vectors[:len(favorite_titles)]
    all_vectors = vectors[len(favorite_titles):]

    # Calculate similarity for each favorite book against all books
    similarities = cosine_similarity(favorite_vectors, all_vectors)

    # Rank books based on their similarity score
    mean_similarity = np.mean(similarities, axis=0)  # Mean similarity across all favorites
    top_indices = mean_similarity.argsort()[-top_n:][::-1]  # Top N recommended book indices

    # Return the top N recommended books
    recommended_books = [all_books[i] for i in top_indices]
    return recommended_books