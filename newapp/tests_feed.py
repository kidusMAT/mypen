from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import AuthorProfile, Book, Script, Poem


class FeedViewTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="pass12345")
        self.bob = User.objects.create_user(username="bob", password="pass12345")
        AuthorProfile.objects.get_or_create(user=self.alice)
        AuthorProfile.objects.get_or_create(user=self.bob)

    def test_feed_guest_renders(self):
        Book.objects.create(title="Guest Book", author=self.bob, status="PUBLISHED", views=5, genre="Fiction")
        resp = self.client.get(reverse("feed"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Guest Book")

    def test_feed_for_you_excludes_own_and_seen(self):
        Book.objects.create(title="My Own Book", author=self.alice, status="PUBLISHED", views=0, genre="Fiction")
        seen_book = Book.objects.create(title="Seen Book", author=self.bob, status="PUBLISHED", views=50, genre="Fantasy")
        unseen_script = Script.objects.create(
            title="Unseen Script", author=self.bob, status="PUBLISHED", views=3, genre="Drama"
        )
        seen_poem = Poem.objects.create(title="Seen Poem", author=self.bob, status="PUBLISHED", views=2)

        seen_book.likes.add(self.alice)
        seen_poem.bookmarks.add(self.alice)

        self.client.login(username="alice", password="pass12345")
        resp = self.client.get(reverse("feed"), {"sort": "for_you"})
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, "My Own Book")
        self.assertNotContains(resp, "Seen Book")
        self.assertNotContains(resp, "Seen Poem")
        self.assertContains(resp, "Unseen Script")

    def test_feed_ajax_pagination_headers(self):
        for i in range(13):
            Book.objects.create(title=f"Book {i}", author=self.bob, status="PUBLISHED", views=i, genre="Fiction")

        resp = self.client.get(reverse("feed"), {"ajax": "1", "page": "2", "type": "book", "sort": "new"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get("X-Has-Next"), "false")
        self.assertContains(resp, "feed-card")

