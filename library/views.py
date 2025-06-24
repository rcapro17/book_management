# library/views.py

from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from .models import Book, Author, Publisher, Borrow, Reserve, CategoryBook, Aviso
from .forms import BookForm, AuthorForm, CategoryForm, PublisherForm, BorrowForm, ReserveForm, CustomUserCreationForm
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
import logging
from .services import fetch_book_info, save_book_cover
import json
import requests
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q


def index(request):
    return render(request, 'library/home.html')


def home(request):
    avisos = Aviso.objects.all().order_by(
        '-data_publicacao')  # Ordenar por mais recentes
    return render(request, 'library/home.html', {'avisos': avisos})


def book_list(request):
    query = request.GET.get('q')

    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(publisher__name__icontains=query)
        )
    else:
        books = Book.objects.all()

    categories = {}
    for book in books:
        category_name = book.category.name if book.category else "Uncategorized"
        if category_name not in categories:
            categories[category_name] = []
        categories[category_name].append(book)

    return render(request, 'library/book_list.html', {
        'categories': categories,
        'query': query if query else '',
    })


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'library/book_detail.html', {'book': book})


def book_unavailable(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'library/book_unavailable.html', {'book': book})


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


def desenvolvimento(request):
    return render(request, 'library/desenvolvimento.html')


def logistica(request):
    return render(request, 'library/logistica.html')


def vendas(request):
    return render(request, 'library/vendas.html')


def formacao_geral(request):
    return render(request, 'library/formacao_geral.html')


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
        # Adjust to your actual book list view name
        return redirect('book_list')
    return render(request, 'library/book_confirm_delete.html', {'book': book})


@login_required
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    # Check available copies
    available_copies = book.copies - \
        Borrow.objects.filter(book=book, return_date__isnull=True).count()

    if available_copies <= 0:
        return render(request, 'library/book_unavailable.html', {'book': book})

    if request.method == 'POST':
        form = BorrowForm(request.POST)
        if form.is_valid():
            borrow = form.save(commit=False)
            borrow.book = book
            borrow.user = request.user
            borrow.save()

            # Decrease available copies
            book.copies -= 1
            book.save()

            return redirect('library:book_detail', pk=book.pk)
    else:
        form = BorrowForm()

    return render(request, 'library/borrow_book.html', {'form': form, 'book': book})


@login_required
def return_book(request, pk):
    borrow = get_object_or_404(Borrow, pk=pk)

    if request.method == "POST":
        borrow.return_book()  # Calls the method to update return_date and increase copies
        return redirect("library:borrow_book_list")

    return redirect("library:borrow_book_list")


logger = logging.getLogger(__name__)


@login_required
def borrow_book_list(request):
    # Busca apenas os empréstimos do usuário logado
    borrows = Borrow.objects.filter(user=request.user).order_by('-id')

    # Paginação - 10 por página
    paginator = Paginator(borrows, 10)  # 10 por página
    page_number = request.GET.get('page')
    borrows = paginator.get_page(page_number)

    return render(request, 'library/borrow_book_list.html', {'borrows': borrows})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', '/')
            # Redirect to the page the user was trying to access
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'library/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('library:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'library/register.html', {'form': form})


def create_book(request):
    if request.method == 'POST':
        try:
            data = request.POST
            category_name = data.get('category')
            author_name = data.get('author')
            publisher_name = data.get('publisher')
            # Get the uploaded file if available
            cover = request.FILES.get('cover')

            # Handle Category
            category, created = CategoryBook.objects.get_or_create(
                category_name=category_name)

            # Handle Author (you may need to add fields for photo and bio depending on your form)
            author, created = Author.objects.get_or_create(name=author_name)

            # Handle Publisher
            publisher, created = Publisher.objects.get_or_create(
                name=publisher_name)

            # Create the Book
            book = Book.objects.create(
                title=data.get('title'),
                description=data.get('description', ''),
                category=category,
                author=author,
                isbn=data.get('isbn'),
                copies=int(data.get('copies')),
                publisher=publisher,
            )

            # Check if cover image is uploaded, if not, use a default cover
            if cover:
                book.photo = cover
            else:
                # Set a default cover image
                default_cover_path = "https://www.vecteezy.com/vector-art/27497398-creative-annual-book-cover-design-template-for-your-business"
                book.photo = default_cover_path

            # Save the book with the cover (either uploaded or default)
            book.save()

            return JsonResponse({'message': 'Book created successfully', 'book_id': book.id}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            # Adjust to your actual book list view name
            return redirect('book_list')
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


@csrf_exempt
def isbn_lookup_view(request):
    if request.method == 'GET':
        # 👉 When the user opens the page, render the HTML template
        return render(request, 'library/isbn_lookup.html')

    elif request.method == 'POST':
        try:
            if not request.body:
                return JsonResponse({'error': 'Empty request body'}, status=400)

            print("Request Body:", request.body.decode('utf-8'))

            data = json.loads(request.body.decode('utf-8'))
            isbn = data.get('isbn')

            if not isbn:
                return JsonResponse({'error': 'No ISBN provided'}, status=400)

            url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
            response = requests.get(url)

            if response.status_code != 200:
                return JsonResponse({'error': 'Failed to fetch book data from API'}, status=500)

            book_data = response.json()

            if 'items' not in book_data:
                return JsonResponse({'error': 'Book not found'}, status=404)

            book_info = book_data['items'][0]['volumeInfo']

            title = book_info.get('title', 'No title')
            author = ', '.join(book_info.get('authors', []))
            description = book_info.get(
                'description', 'No description available')
            categories = ', '.join(book_info.get(
                'categories', ['No category available']))
            publisher = book_info.get('publisher', 'Unknown Publisher')
            cover = book_info.get('imageLinks', {}).get(
                'thumbnail',
                'https://via.placeholder.com/150x220.png?text=No+Cover'
            )

            return JsonResponse({
                'title': title,
                'author': author,
                'isbn': isbn,
                'category': categories,
                'publisher': publisher,
                'description': description,
                'cover': cover,
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error occurred: {str(e)}'}, status=500)

    else:
        # If the method is not GET or POST
        return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def register_book_view(request):
    if request.method == "POST":
        title = request.POST.get("title")
        author_name = request.POST.get("author")  # author name from form
        isbn = request.POST.get("isbn")
        category_name = request.POST.get("category")  # category name from form
        publisher_name = request.POST.get(
            "publisher")  # publisher name from form
        description = request.POST.get("description")
        copies = request.POST.get("copies")

        # Handle file upload (if present)
        cover_file = request.FILES.get("cover")
        cover_url = request.POST.get("cover_url")

        # Get or create the related models (CategoryBook, Author, Publisher)
        category, created = CategoryBook.objects.get_or_create(
            name=category_name)
        author, created = Author.objects.get_or_create(name=author_name)
        publisher, created = Publisher.objects.get_or_create(
            name=publisher_name)

        # Create the book
        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            category=category,
            publisher=publisher,
            description=description,
            copies=copies
        )

        # Set cover field based on availability of file or URL
        if cover_file:
            book.photo = cover_file
        elif cover_url:
            book.photo_url = cover_url

        book.save()

        return JsonResponse({"message": "Book registered successfully!"})

    return JsonResponse({"error": "Invalid request."})
