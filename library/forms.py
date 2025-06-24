# library/forms.py

from django import forms
from .models import Book, Author, CategoryBook, Publisher, Borrow, Reserve, User
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = CategoryBook
        fields = ['name']


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['name']


class ReserveForm(forms.ModelForm):
    class Meta:
        model = Reserve
        fields = []


class BorrowForm(forms.ModelForm):
    class Meta:
        model = Borrow
        fields = ['book', 'scheduled_return_date']  # Include return date

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ensure book selection is disabled
        self.fields['book'].widget.attrs['readonly'] = True
        self.fields['book'].widget.attrs['style'] = 'pointer-events: none; background-color: #f3f3f3;'

        # Add a date picker for scheduled return date
        self.fields['scheduled_return_date'].widget = forms.DateInput(attrs={
                                                                      'type': 'date'})


class BorrowForm(forms.ModelForm):
    class Meta:
        model = Borrow
        fields = ['scheduled_return_date']
        widgets = {
            'scheduled_return_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_scheduled_return_date(self):
        scheduled_return_date = self.cleaned_data.get('scheduled_return_date')
        if scheduled_return_date and scheduled_return_date <= timezone.now():
            raise forms.ValidationError(
                "Scheduled return date must be in the future.")
        return scheduled_return_date


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'description', 'category',
                  'author', 'isbn', 'copies', 'photo', 'publisher']


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User  # Use your custom User model
        fields = ['ra', 'name', 'email', 'phone', 'password1', 'password2']
