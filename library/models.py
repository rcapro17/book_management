# library/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, ra, name, email, phone, password=None):
        if not ra:
            raise ValueError("The RA field must be set")
        email = self.normalize_email(email)
        user = self.model(ra=ra, name=name, email=email, phone=phone)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, ra, name, email, phone, password=None):
        user = self.create_user(ra, name, email, phone, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ra = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'ra'
    REQUIRED_FIELDS = ['name', 'email', 'phone']

    def __str__(self):
        return self.name


class CategoryBook(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(CategoryBook, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    isbn = models.CharField(max_length=13, unique=True)
    copies = models.IntegerField(default=1)
    reserved_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reserved_books'
    )
    photo = models.ImageField(
        upload_to='books/', null=True, blank=True)  # Allow image upload
    # Allow URL as an alternative
    photo_url = models.URLField(blank=True, null=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Aviso(models.Model):
    titulo = models.CharField(max_length=200)
    resumo = models.TextField()
    conteudo = models.TextField()
    data_publicacao = models.DateTimeField(auto_now_add=True)
    imagem = models.ImageField(upload_to='avisos/', blank=True, null=True)

    class Meta:
        ordering = ['-data_publicacao']

    def __str__(self):
        return self.titulo


class Borrow(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(auto_now_add=True)
    scheduled_return_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)

    def return_book(self):
        """Handles returning the book and updating availability."""
        if not self.return_date:
            self.return_date = timezone.now()
            self.save()
            # Increase available copies
            self.book.copies += 1
            self.book.save()

    def __str__(self):
        return f"{self.user} borrowed {self.book}"


class Reserve(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    # Ensure this field exists and is a valid DateTimeField
    reserved_at = models.DateTimeField()

    def __str__(self):
        return f"Reserve for {self.book} by {self.user}"

    # em andamento


class EventoCalendario(models.Model):
    data = models.DateField()
    titulo = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.titulo} em {self.data}"

    @property
    def dia(self):
        return self.data.day

    @property
    def dia_semana(self):
        return self.data.strftime('%A').upper()[:3]  # e.g., MON

    @property
    def mes(self):
        return self.data.strftime('%b').upper()  # e.g., JUL
