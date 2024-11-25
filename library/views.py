# library/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import Book, Author, Publisher, Borrow, Reserve, CategoryBook
from .forms import BookForm, AuthorForm, CategoryForm, PublisherForm, BorrowForm, ReserveForm
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

def index(request):
    return render(request, 'library/index.html')

# def book_list(request):
#     books = Book.objects.all()
#     return render(request, 'library/book_list.html', {'books': books})

def book_list(request):
    categories = CategoryBook.objects.prefetch_related('book_set__author').all()
    return render(request, 'library/book_list.html', {'categories': categories})


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'library/book_detail.html', {'book': book})

def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('book_detail', args=[pk]))
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form})

@login_required
def reserve_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = ReserveForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.book = book
            reservation.user = request.user  # Correct field assignment
            reservation.save()
            return redirect('library:book_detail', pk=book.pk)
    else:
        form = ReserveForm()
    return render(request, 'library/reserve_book.html', {'form': form, 'book': book})

@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')  # Adjust to your actual book list view name
    return render(request, 'library/book_confirm_delete.html', {'book': book})

@login_required
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BorrowForm(request.POST)
        if form.is_valid():
            borrow = form.save(commit=False)
            borrow.book = book
            borrow.user = request.user  # Correct field assignment
            borrow.save()
            return redirect('library:book_detail', pk=book.pk)
    else:
        form = BorrowForm()
    return render(request, 'library/borrow_book.html', {'form': form, 'book': book})

@login_required
def return_book(request, pk):
    borrow = get_object_or_404(Borrow, pk=pk)
    if request.method == 'POST':
        borrow.return_date = timezone.now()  # Correct field assignment
        borrow.save()
        return redirect('library:book_detail', pk=borrow.book.pk)
    return render(request, 'library/return_book.html', {'borrow': borrow})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('library:index')
        else:
            return render(request, 'library/login.html', {'error': 'Invalid username or password'})
    return render(request, 'library/login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('library:login')
    else:
        form = UserCreationForm()
    return render(request, 'library/register.html', {'form': form})

def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book_list')  # Adjust to your actual book list view name
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form})

# Listagem de autores
def author_list(request):
    authors = Author.objects.all()
    return render(request, 'library/author_list.html', {'authors': authors})



# Detalhe de autor
def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    return render(request, 'library/author_detail.html', {'author': author})

# Criação de autor
def author_create(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('author_list')
    else:
        form = AuthorForm()
    return render(request, 'library/author_form.html', {'form': form})

# Atualização de autor
def author_update(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            return redirect('author_detail', pk=author.pk)
    else:
        form = AuthorForm(instance=author)
    return render(request, 'library/author_form.html', {'form': form})

# Exclusão de autor
def author_delete(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        author.delete()
        return redirect('author_list')
    return render(request, 'library/author_confirm_delete.html', {'author': author})


# Listagem de categorias
def category_list(request):
    categories = CategoryBook.objects.all()
    return render(request, 'library/category_list.html', {'categories': categories})

# Detalhe de categoria
def category_detail(request, pk):
    category = get_object_or_404(CategoryBook, pk=pk)
    return render(request, 'library/category_detail.html', {'category': category})

# Criação de categoria
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'library/category_form.html', {'form': form})

# Atualização de categoria
def category_update(request, pk):
    category = get_object_or_404(CategoryBook, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_detail', pk=category.pk)
    else:
        form = CategoryForm(instance=category)
    return render(request, 'library/category_form.html', {'form': form})

# Exclusão de categoria
def category_delete(request, pk):
    category = get_object_or_404(CategoryBook, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'library/category_confirm_delete.html', {'category': category})


# Listagem de publishers
def publisher_list(request):
    publishers = Publisher.objects.all()
    return render(request, 'library/publisher_list.html', {'publishers': publishers})

# Detalhe de publisher
def publisher_detail(request, pk):
    publisher = get_object_or_404(Publisher, pk=pk)
    return render(request, 'library/publisher_detail.html', {'publisher': publisher})

# Criação de publisher
def publisher_create(request):
    if request.method == 'POST':
        form = PublisherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('publisher_list')
    else:
        form = PublisherForm()
    return render(request, 'library/publisher_form.html', {'form': form})

# Atualização de publisher
def publisher_update(request, pk):
    publisher = get_object_or_404(Publisher, pk=pk)
    if request.method == 'POST':
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            form.save()
            return redirect('publisher_detail', pk=publisher.pk)
    else:
        form = PublisherForm(instance=publisher)
    return render(request, 'library/publisher_form.html', {'form': form})

# Exclusão de publisher
def publisher_delete(request, pk):
    publisher = get_object_or_404(Publisher, pk=pk)
    if request.method == 'POST':
        publisher.delete()
        return redirect('publisher_list')
    return render(request, 'library/publisher_confirm_delete.html', {'publisher': publisher})