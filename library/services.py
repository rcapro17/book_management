import requests
from django.core.files.base import ContentFile
from .models import Book

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes?q=isbn:{}"


def fetch_book_info(isbn):
    """Fetch book data from Google Books API."""
    response = requests.get(GOOGLE_BOOKS_API_URL.format(isbn))
    data = response.json()

    if "items" not in data:
        return None

    book_data = data["items"][0]["volumeInfo"]

    # Get book details
    title = book_data.get("title", "Unknown Title")
    description = book_data.get("description", "")
    authors = book_data.get("authors", ["Unknown Author"])
    publisher = book_data.get("publisher", "Unknown Publisher")

    # Get book cover image
    image_url = book_data.get("imageLinks", {}).get("thumbnail")

    return {
        "title": title,
        "description": description,
        "author": authors[0],  # Take the first author
        "publisher": publisher,
        "image_url": image_url
    }


def save_book_cover(book, image_url):
    """Download and save the book cover."""
    if not image_url:
        return  # No image available

    response = requests.get(image_url)
    if response.status_code == 200:
        book.photo.save(f"{book.isbn}.jpg", ContentFile(
            response.content), save=True)
