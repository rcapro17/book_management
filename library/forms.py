# library/forms.py

from django import forms
from .models import Book, Author, CategoryBook, Publisher, Borrow, Reserve

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn','description', 'publisher', 'category', 'photo', 'copies']


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'photo', 'bio']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = CategoryBook
        fields = ['category_name']

class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['name']

class BorrowForm(forms.ModelForm):
    class Meta:
        model = Borrow
        fields = ['book', 'scheduled_return_date']

class ReserveForm(forms.ModelForm):
    class Meta:
        model = Reserve
        fields = []
