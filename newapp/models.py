from django.contrib.postgres.fields import ArrayField
from django.db import models

from django.contrib.auth.models import User

# Extends the User with Author details

from django.core.validators import RegexValidator

class AuthorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pen_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"

class ProfileComment(models.Model):
    profile = models.ForeignKey(AuthorProfile, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.profile.user.username}"

class Book(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('FINISHED', 'Finished'),
    )

    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    handpicked = models.BooleanField(default=False)
    cover_image = models.ImageField(upload_to='images/', blank=True, null=True)
    genre = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_books', blank=True)
    bookmarks = models.ManyToManyField(User, related_name='bookmarked_books', blank=True)
    read_time = models.CharField(max_length=10, blank=True)

    # Properties to get counts for template usage
    @property
    def like_count(self):
        return self.likes.count()
    @property
    def view_count(self):
        return self.views
    @property
    def chapter_count(self):
        return self.chapters.count()

    def __str__(self):
        return self.title

class Chapter(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
    )

    book = models.ForeignKey(Book, related_name='chapters', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    
    # Metrics
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_chapters', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_saved = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.book.title} - {self.title}"

    @property
    def is_updated(self):
        # Updated if last_saved is more than 2 minutes after created_at
        # (Allows small buffer for initial creation/publishing)
        from datetime import timedelta
        return self.last_saved > self.created_at + timedelta(minutes=2)

# Create your models here.



class Contest(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
    )

    TYPE_CHOICES = (
        ('Book', 'Book'),
        ('Script', 'Script'),
        ('Poem', 'Poem'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    prize = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)
    
    contest_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='Book')
    entry_books = models.ManyToManyField('Book', related_name='contest_entries', blank=True)
    entry_scripts = models.ManyToManyField('Script', related_name='contest_entries', blank=True)
    entry_poems = models.ManyToManyField('Poem', related_name='contest_entries', blank=True)
    
    # Winner fields
    winning_book = models.ForeignKey('Book', related_name='won_contests', on_delete=models.SET_NULL, null=True, blank=True)
    winning_script = models.ForeignKey('Script', related_name='won_contests', on_delete=models.SET_NULL, null=True, blank=True)
    winning_poem = models.ForeignKey('Poem', related_name='won_contests', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

class Script(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
    )

    title = models.CharField(max_length=200, default="Untitled Script")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='script_covers/', blank=True, null=True)
    genre = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_saved = models.DateTimeField(auto_now=True)
    handpicked = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    page_count = models.PositiveIntegerField(default=0)
    script_file = models.FileField(upload_to='scripts/', blank=True, null=True)

    # Metrics
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_scripts', blank=True)
    bookmarks = models.ManyToManyField(User, related_name='bookmarked_scripts', blank=True)

    def __str__(self):
        return self.title

class Poem(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('FINISHED', 'Finished'),
    )

    title = models.CharField(max_length=200, default="Untitled Poem")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='poem_covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_saved = models.DateTimeField(auto_now=True)
    handpicked = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')

    # Metrics
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_poems', blank=True)
    bookmarks = models.ManyToManyField(User, related_name='bookmarked_poems', blank=True)

    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"

class Confession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_confessions', blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Confession {self.id} (Anonymous)"

class ConfessionComment(models.Model):
    confession = models.ForeignKey(Confession, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment on Confession {self.confession.id}"

class Movie(models.Model):
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100, blank=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='added_movies')
    cover_image = models.ImageField(upload_to='movie_covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(r.rating for r in ratings) / len(ratings)
        return 0

    @property
    def rating_count(self):
        return self.ratings.count()

    @property
    def comment_count(self):
        return self.comments.count()

class MovieComment(models.Model):
    movie = models.ForeignKey(Movie, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.movie.title}"

class MovieRating(models.Model):
    movie = models.ForeignKey(Movie, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])

    class Meta:
        unique_together = ('movie', 'user')

    def __str__(self):
        return f"{self.user.username} rated {self.movie.title} {self.rating}"

class BookReview(models.Model):
    title = models.CharField(max_length=200)
    author_name = models.CharField(max_length=200, blank=True)
    genre = models.CharField(max_length=100, blank=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='added_book_reviews')
    cover_image = models.ImageField(upload_to='book_review_covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings:
            return sum(r.rating for r in ratings) / len(ratings)
        return 0

    @property
    def rating_count(self):
        return self.ratings.count()

    @property
    def comment_count(self):
        return self.comments.count()

class BookReviewComment(models.Model):
    book_review = models.ForeignKey(BookReview, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.book_review.title}"

class BookReviewRating(models.Model):
    book_review = models.ForeignKey(BookReview, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])

    class Meta:
        unique_together = ('book_review', 'user')

    def __str__(self):
        return f"{self.user.username} rated {self.book_review.title} {self.rating}"
