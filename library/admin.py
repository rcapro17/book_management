# library/admin.py
from django.contrib import admin
from .models import User, Book, Borrow, CategoryBook, Author, Publisher, Reserve

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('ra', 'name', 'email', 'phone', 'is_active', 'is_staff')
    search_fields = ('ra', 'name', 'email')
    list_filter = ('is_active', 'is_staff')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'copies', 'category', 'publisher')
    search_fields = ('title', 'isbn')
    list_filter = ('category', 'author', 'publisher')

@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'borrow_date', 'return_date', 'scheduled_return_date')
    search_fields = ('user__name', 'book__title')
    list_filter = ('borrow_date', 'return_date', 'scheduled_return_date')

@admin.register(CategoryBook)
class CategoryBookAdmin(admin.ModelAdmin):
    list_display = ('category_name',)
    search_fields = ('category_name',)

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

