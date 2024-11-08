from django.test import TestCase
from django.urls import reverse

class URLTests(TestCase):
    def test_home_url(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_url(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_register_url(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
    
    def test_book_list_url(self):
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_author_list_url(self):
        response = self.client.get(reverse('author_list'))
        self.assertEqual(response.status_code, 200)
