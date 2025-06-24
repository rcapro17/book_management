# library/admin.py
from .services import fetch_book_info, save_book_cover
from .models import Book, Publisher, Author
from django.contrib import admin
from .models import User, Book, Borrow, CategoryBook, Author, Publisher, Reserve, Aviso
from django.urls import path
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from .services import fetch_book_info
from django.utils.html import format_html


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('ra', 'name', 'email', 'phone', 'is_active', 'is_staff')
    search_fields = ('ra', 'name', 'email')
    list_filter = ('is_active', 'is_staff')


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'book_cover',
                    'copies', 'category', 'publisher')
    search_fields = ('title', 'isbn')
    list_filter = ('category', 'author', 'publisher')

    fields = ('title', 'description', 'category', 'author', 'isbn',
              'copies', 'reserved_by', 'photo', 'publisher')

    def get_urls(self):
        # Get the default URLs
        urls = super().get_urls()
        # Define custom URL
        custom_urls = [
            path('fetch-book-info/', self.admin_site.admin_view(self.fetch_book_info),
                 name='fetch_book_info'),
        ]
        return custom_urls + urls

    def fetch_book_info(self, request):
        """Handles AJAX request to fetch book info from Google Books API."""
        isbn = request.GET.get("isbn", "")
        if not isbn:
            return JsonResponse({"error": "No ISBN provided"}, status=400)

        book_data = fetch_book_info(isbn)
        if not book_data:
            return JsonResponse({"error": "Book not found"}, status=404)

        book, created = Book.objects.get_or_create(isbn=isbn, defaults={
            "title": book_data["title"],
            "description": book_data["description"],
            "publisher": Publisher.objects.get_or_create(name=book_data["publisher"])[0],
        })

        author, _ = Author.objects.get_or_create(name=book_data["author"])
        book.author = author

        # Save the book cover if available
        save_book_cover(book, book_data.get("image_url"))

        book.save()

        return JsonResponse({
            "message": "Book fetched successfully",
            "title": book.title,
            "author": book.author.name,
            "isbn": book.isbn,
            "cover": book.photo.url if book.photo else None
        })

    def fetch_from_api_button(self, obj):
        """Add a button to fetch book info from the API."""
        return mark_safe(f'<button type="button" class="fetch-book-btn" data-isbn="{obj.isbn}">Fetch Data</button>')

    fetch_from_api_button.short_description = "Fetch from API"

    def book_cover(self, obj):
        """Displays the book cover if available."""
        if obj.photo:
            return format_html(f'<img src="{obj.photo.url}" width="50" height="75" style="border-radius:5px;"/>')
        return "No Cover"

    book_cover.short_description = "Cover"


admin.site.register(Book, BookAdmin)


@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data_publicacao')
    search_fields = ('titulo',)
    ordering = ('-data_publicacao',)


@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'borrow_date',
                    'return_date', 'scheduled_return_date')
    search_fields = ('user__name', 'book__title')
    list_filter = ('borrow_date', 'return_date', 'scheduled_return_date')


@admin.register(CategoryBook)
class CategoryBookAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class ReserveAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'reserved_at')
    list_filter = ('reserved_at',)  # Filter by reserved_at


admin.site.register(Reserve, ReserveAdmin)
