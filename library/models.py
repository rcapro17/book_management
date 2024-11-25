# library/models.py

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

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
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255)

    def __str__(self):
        return self.category_name

class Author(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='authors/')
    bio = models.TextField()

    def __str__(self):
        return self.name

class Publisher(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(CategoryBook, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    isbn = models.CharField(max_length=13, unique=True)
    copies = models.IntegerField()
    reserved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reserved_books')
    photo = models.ImageField(upload_to='books/')
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Borrow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    scheduled_return_date = models.DateTimeField()

    def __str__(self):
        return f"{self.user.name} borrowed {self.book.title}"

class Reserve(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    reserved_at = models.DateTimeField()  # Ensure this field exists and is a valid DateTimeField

    def __str__(self):
        return f"Reserve for {self.book} by {self.user}"
    
    # em andamento

