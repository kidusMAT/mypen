from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import json

from .models import Contest, ContestParticipant, AuthorProfile, Book, Script, Poem


class ContestViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='contestauthor', password='password123')
        self.profile = AuthorProfile.objects.create(user=self.user, phone_number='+251911223344')
        
        now = timezone.now()
        self.book_contest = Contest.objects.create(
            title='Epic Novel Contest',
            description='Write an epic novel',
            contest_type='BOOK',
            status='ACTIVE',
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=10),
            prize='$1,000'
        )

        self.script_contest = Contest.objects.create(
            title='Short Film Contest',
            description='Write a screenplay',
            contest_type='SCRIPT',
            status='ACTIVE',
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=10),
            prize='$500'
        )

        self.book = Book.objects.create(
            title='My Contest Book',
            author=self.user,
            status='PUBLISHED'
        )
        self.script = Script.objects.create(
            title='My Contest Script',
            author=self.user,
            status='PUBLISHED'
        )

    def test_contest_list_view(self):
        self.client.login(username='contestauthor', password='password123')
        response = self.client.get(reverse('contest_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Epic Novel Contest')
        self.assertContains(response, 'Short Film Contest')
        # Check context has user works
        user_books = response.context['user_books']
        self.assertTrue(any(b['title'] == 'My Contest Book' for b in user_books))

    def test_contest_detail_view(self):
        response = self.client.get(reverse('contest_detail', args=[self.book_contest.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Epic Novel Contest')

    def test_join_contest_requires_phone(self):
        self.profile.phone_number = ''
        self.profile.save()
        self.client.login(username='contestauthor', password='password123')
        
        response = self.client.get(reverse('join_contest', args=[self.book_contest.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('profile/edit/me', response.url)
        self.assertIn('next=join_contest', response.url)

    def test_join_contest_post_success(self):
        self.client.login(username='contestauthor', password='password123')
        response = self.client.post(reverse('join_contest', args=[self.book_contest.id]), {
            'entry_type': 'BOOK',
            'entry_id': self.book.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContestParticipant.objects.filter(contest=self.book_contest, user=self.user).count(), 1)

    def test_join_contest_rejects_type_mismatch(self):
        self.client.login(username='contestauthor', password='password123')
        response = self.client.post(reverse('join_contest', args=[self.book_contest.id]), {
            'entry_type': 'SCRIPT',
            'entry_id': self.script.id
        })
        self.assertEqual(response.status_code, 302)
        # Should not create participant
        self.assertEqual(ContestParticipant.objects.filter(contest=self.book_contest, user=self.user).count(), 0)

    def test_submit_contest_entry_ajax_success(self):
        self.client.login(username='contestauthor', password='password123')
        payload = json.dumps({
            'contest_id': self.book_contest.id,
            'work_id': self.book.id,
            'work_type': 'BOOK'
        })
        response = self.client.post(
            reverse('submit_contest_entry'),
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertTrue(ContestParticipant.objects.filter(contest=self.book_contest, user=self.user).exists())

    def test_submit_contest_entry_ajax_rejects_duplicate(self):
        ContestParticipant.objects.create(
            contest=self.book_contest,
            user=self.user,
            entry_type='BOOK',
            entry_id=self.book.id
        )
        self.client.login(username='contestauthor', password='password123')
        payload = json.dumps({
            'contest_id': self.book_contest.id,
            'work_id': self.book.id,
            'work_type': 'BOOK'
        })
        response = self.client.post(
            reverse('submit_contest_entry'),
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('already joined', data['message'])
