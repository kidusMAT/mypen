from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import AuthorProfile, Book, ProfileComment
from django.urls import reverse
from .views import profile_view, authors_list, add_profile_comment

class ProfileAuthorsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testauthor', password='password123')
        self.profile = AuthorProfile.objects.get_or_create(user=self.user)[0]
        self.client.login(username='testauthor', password='password123')

    def test_dashboard_link_exists(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'dashboard-profile-link')
        self.assertContains(response, reverse('profile_view', args=['testauthor']))

    def test_profile_view(self):
        response = self.client.get(reverse('profile_view', args=['testauthor']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testauthor')

    def test_authors_list_view(self):
        response = self.client.get(reverse('authors_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testauthor')

    def test_add_comment(self):
        response = self.client.post(reverse('add_profile_comment', args=['testauthor']), {
            'content': 'Great work!'
        })
        self.assertEqual(ProfileComment.objects.count(), 1)
        self.assertEqual(ProfileComment.objects.first().content, 'Great work!')
