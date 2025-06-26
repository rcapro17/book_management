# library/views.py

from uuid import uuid4
import uuid
from .models import Book, Author, Publisher, CategoryBook
from django.http import JsonResponse
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from .models import Book, Author, Publisher, Borrow, Reserve, CategoryBook, Aviso, EventoCalendario

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
from PIL import Image, ImageDraw, ImageFont
import io
from django.core.files.base import ContentFile


def index(request):
    return render(request, 'library/home.html')


def agrupar_em_grupos(lista, tamanho):
    return [lista[i:i + tamanho] for i in range(0, len(lista), tamanho)]


avisos_queryset = Aviso.objects.all().order_by('-id')
avisos = agrupar_em_grupos(list(avisos_queryset), 3)


def home(request):
    avisos_queryset = Aviso.objects.all().order_by('-id')
    avisos = agrupar_em_grupos(list(avisos_queryset), 3)

    eventos_queryset = EventoCalendario.objects.order_by('data')
    eventos_calendario = agrupar_em_grupos(list(eventos_queryset), 3)

    return render(request, 'library/home.html', {
        'avisos': avisos,
        'eventos_calendario': eventos_calendario,
        'eventos_upcoming': [],  # pode popular depois
    })


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


logger = logging.getLogger(__name__)


def clean_isbn(isbn):
    return isbn.replace('-', '').replace(' ', '')


def convert_isbn_10_to_13(isbn10):
    prefix = '978' + isbn10[:-1]
    total = sum((int(num) * (1 if i % 2 == 0 else 3))
                for i, num in enumerate(prefix))
    check_digit = (10 - (total % 10)) % 10
    return prefix + str(check_digit)


def fetch_book_by_isbn(isbn_code):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn_code}"
    return requests.get(url)


def fetch_book_by_title(title):
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title}"
    return requests.get(url)


@csrf_exempt
def isbn_lookup_view(request):
    if request.method == 'GET':
        return render(request, 'library/isbn_lookup.html')

    elif request.method == 'POST':
        try:
            if not request.body:
                return JsonResponse({'error': 'Empty request body'}, status=400)

            data = json.loads(request.body.decode('utf-8'))
            raw_isbn = data.get('isbn', '').strip()
            title_query = data.get('title', '').strip()

            if not raw_isbn and not title_query:
                return JsonResponse({'error': 'No ISBN or title provided'}, status=400)

            isbn = None

            if raw_isbn:
                isbn = clean_isbn(raw_isbn)
                response = fetch_book_by_isbn(isbn)

                if response.status_code == 200 and 'items' not in response.json() and len(isbn) == 10:
                    isbn13 = convert_isbn_10_to_13(isbn)
                    response = fetch_book_by_isbn(isbn13)
                    isbn = isbn13
            else:
                response = fetch_book_by_title(title_query)
                isbn = 'N/A'

            if response.status_code != 200:
                return JsonResponse({'error': 'Failed to fetch book data from API'}, status=500)

            book_data = response.json()

            if 'items' not in book_data:
                return JsonResponse({'error': 'Book not found'}, status=404)

            books = []
            for item in book_data['items'][:5]:
                info = item['volumeInfo']
                title = info.get('title', 'No title')
                authors = ', '.join(info.get('authors', []))
                category = ', '.join(
                    info.get('categories', ['No category available']))
                publisher = info.get('publisher', 'Unknown Publisher')
                description = info.get(
                    'description', 'No description available')
                image_url = info.get('imageLinks', {}).get('thumbnail')

                if not image_url:
                    image_file = generate_default_cover(title)
                    path = default_storage.save(
                        f'temp_covers/{image_file.name}', image_file)
                    image_url = default_storage.url(path)

                books.append({
                    'title': title,
                    'author': authors,
                    'isbn': isbn,
                    'category': category,
                    'publisher': publisher,
                    'description': description,
                    'cover': image_url,
                })

            return JsonResponse({'multiple_books': books})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error occurred: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def generate_default_cover(title):
    width, height = 300, 450
    background_color = (50, 50, 50)  # Dark gray
    text_color = (255, 255, 255)     # White

    img = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except IOError:
        font = ImageFont.load_default()

    text = title[:35] + '...' if len(title) > 35 else title
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) / 2
    y = (height - text_height) / 2

    draw.text((x, y), text, font=font, fill=text_color)

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    filename = f"{title[:10].replace(' ', '_')}_default_{uuid.uuid4().hex[:6]}.png"
    return ContentFile(buffer.getvalue(), name=filename)


@csrf_exempt
def register_book_view(request):
    if request.method == "POST":
        try:
            logger.info("POST: %s", request.POST)
            logger.info("FILES: %s", request.FILES)

            title = request.POST.get("title")
            author_name = request.POST.get("author")
            raw_isbn = request.POST.get("isbn", "").strip()
            category_name = request.POST.get("category")
            publisher_name = request.POST.get("publisher")
            description = request.POST.get("description")
            copies = request.POST.get("copies")
            cover_file = request.FILES.get("cover")

            cover_urls = request.POST.getlist("cover_url")
            cover_url = cover_urls[-1] if cover_urls else None

            if not title:
                return JsonResponse({"error": "Title is required."}, status=400)

            # Se ISBN for vazio ou "N/A", gera um identificador alternativo único
            if not raw_isbn or raw_isbn.upper() == "N/A":
                isbn = f"fake-isbn-{uuid4().hex[:8]}"
            else:
                isbn = raw_isbn

            # Evita duplicatas (exceto para fake-isbn, que são únicos)
            if Book.objects.filter(isbn=isbn).exists():
                return JsonResponse({"error": "A book with this ISBN already exists."}, status=400)

            try:
                copies = int(copies)
            except (ValueError, TypeError):
                copies = 1

            category, _ = CategoryBook.objects.get_or_create(
                name=category_name or "General")
            author, _ = Author.objects.get_or_create(
                name=author_name or "Unknown")
            publisher, _ = Publisher.objects.get_or_create(
                name=publisher_name or "Unknown")

            book = Book(
                title=title,
                author=author,
                isbn=isbn,
                category=category,
                publisher=publisher,
                description=description,
                copies=copies,
            )

            if cover_file:
                book.photo = cover_file
            elif cover_url:
                book.photo_url = cover_url
            else:
                book.photo = generate_default_cover(title)

            book.save()
            return JsonResponse({"message": "Book registered successfully!"})

        except Exception as e:
            logger.exception("Book registration failed")
            return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)


def whats_happening_view(request):
    avisos = Aviso.objects.all().order_by('-id')  # se você já usa
    eventos = EventoCalendario.objects.order_by('data')

    # Agrupa os eventos em grupos de 3
    def agrupar_em_grupos(lista, tamanho):
        return [lista[i:i+tamanho] for i in range(0, len(lista), tamanho)]

    eventos_calendario = agrupar_em_grupos(list(eventos), 3)

    return render(request, 'library/whats_happening.html', {
        'avisos': avisos,
        'eventos_calendario': eventos_calendario,
        'eventos_upcoming': [],  # substitua depois se necessário
    })
