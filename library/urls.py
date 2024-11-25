# library/urls.py
from django.contrib import admin
from django.urls import path
from . import views

app_name = 'library'

# em andamento

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),  # Changed from 'library/login/'
    path('register/', views.register_view, name='register'),
    path('books/', views.book_list, name='book_list'),
    path('borrow_book/<int:pk>', views.borrow_book, name='borrow_book'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/create/', views.book_create, name='book_create'),
    path('books/<int:pk>/update/', views.book_update, name='book_update'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('authors/', views.author_list, name='author_list'),
    path('authors/<int:pk>/', views.author_detail, name='author_detail'),
    path('authors/create/', views.author_create, name='author_create'),
    path('authors/<int:pk>/update/', views.author_update, name='author_update'),
    path('authors/<int:pk>/delete/', views.author_delete, name='author_delete'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('publishers/', views.publisher_list, name='publisher_list'),
    path('publishers/<int:pk>/', views.publisher_detail, name='publisher_detail'),
    path('publishers/create/', views.publisher_create, name='publisher_create'),
    path('publishers/<int:pk>/update/', views.publisher_update, name='publisher_update'),
    path('publishers/<int:pk>/delete/', views.publisher_delete, name='publisher_delete'),
    path('return_book/', views.return_book, name='return_book'),
]
