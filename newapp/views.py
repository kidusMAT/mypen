from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
import json
from django.core.paginator import Paginator
from django.db.models import Count, Q, F
from .models import Book, Chapter, Contest, Script, ScriptEpisode, Poem, ContactMessage
from .forms import ContactForm
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

def coming_soon(request):
    feature = request.GET.get('feature', 'This feature')
    return render(request, 'newapp/coming_soon.html', {'feature': feature})


@login_required
def create_content(request):
    if request.method == 'POST':
        print(f"DEBUG: create_content POST: {request.POST}")
        contest_id = request.POST.get('contest_id')
        content_type = request.POST.get('type')
        
        if content_type == 'script':
            title = request.POST.get('Booktitle')
            script_file = request.FILES.get('script_file')
            
            if not title and script_file:
                title = script_file.name
            
            if not title:
                title = 'Untitled Script'
                
            genre = request.POST.get('genre', '')
            script_format = request.POST.get('script_format', 'FEATURE_FILM')

            script = Script.objects.create(
                title=title, 
                author=request.user, 
                status='PUBLISHED' if script_file else 'DRAFT',
                script_file=script_file,
                genre=genre,
                script_format=script_format
            )

            if script_format == 'EPISODIC' and not script_file:
                ScriptEpisode.objects.create(
                    script=script,
                    title="Episode 1",
                    content="",
                    status='DRAFT'
                )
            
            if contest_id:
                try:
                    contest = Contest.objects.get(id=contest_id)
                    contest.entry_scripts.add(script)
                except Contest.DoesNotExist:
                    pass
                    
            if script_file:
                return redirect('dashboard')
            return redirect('write_script', script_id=script.id)

        if content_type == 'poem':
            title = request.POST.get('Booktitle', 'Untitled Poem')
            poem = Poem.objects.create(title=title, author=request.user, status='DRAFT')
            
            if contest_id:
                try:
                    contest = Contest.objects.get(id=contest_id)
                    contest.entry_poems.add(poem)
                except Contest.DoesNotExist:
                    pass
                    
            return redirect('write_poem', poem_id=poem.id)

        # Match names from write.html form for standard stories (Book/Chapter)
        title = request.POST.get('Booktitle')
        chapter_title = request.POST.get('chaptername')
        content = request.POST.get('thestory')
        genre_type = request.POST.get('type', 'story').capitalize()
        
        # Create Book first
        genre = request.POST.get('genre') or genre_type
        description = request.POST.get('description', '')
        cover_image = request.FILES.get('cover_image')
        
        book = Book.objects.create(
            title=title, 
            author=request.user, 
            genre=genre,
            description=description,
            cover_image=cover_image,
            status='PUBLISHED' if 'publish' in request.POST else 'DRAFT'
        )
        
        if contest_id:
            try:
                contest = Contest.objects.get(id=contest_id)
                contest.entry_books.add(book)
            except Contest.DoesNotExist:
                pass
        
        # Create the first Chapter
        if not chapter_title:
            chapter_title = "Chapter 1"
        
        status = 'PUBLISHED' if 'publish' in request.POST else 'DRAFT'
        
        
        chapter = Chapter.objects.create(
            book=book,
            title=chapter_title,
            content=content,
            status=status
        )
        
        return redirect('write_chapter', chapter_id=chapter.id)

    return render(request, 'newapp/write.html')


@login_required
@require_POST
def delete_book_ajax(request, book_id):
    try:
        book = Book.objects.get(id=book_id, author=request.user)
        book.delete()
        return JsonResponse({'status': 'success', 'message': 'Story deleted successfully.'})
    except Book.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Story not found or access denied.'})




@login_required
def write_chapter(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id, book__author=request.user)
    
    if request.method == 'POST':
        print(f"DEBUG: write_chapter POST: {request.POST}")
        # Match names from write.html form
        book_title = request.POST.get('Booktitle')
        chapter_title = request.POST.get('chaptername')
        content = request.POST.get('thestory')

        # Update fields
        if book_title:
            chapter.book.title = book_title
            chapter.book.save()
            
        if chapter_title:
            chapter.title = chapter_title
            
        if content is not None:
             chapter.content = content
        
        if 'publish' in request.POST:
            chapter.status = 'PUBLISHED'
            chapter.book.status = 'PUBLISHED'
            chapter.book.save()
        elif 'save_draft' in request.POST or 'end_chapter' in request.POST or 'next_chapter' in request.POST:
            chapter.status = 'DRAFT'
            
        chapter.save()
        
        if 'next_chapter' in request.POST:
            return redirect('add_chapter', book_id=chapter.book.id)
        
        if 'end_chapter' in request.POST:
            return redirect('manage_book', book_id=chapter.book.id)
            
        return redirect('write_chapter', chapter_id=chapter.id)

    return render(request, 'newapp/write.html', {'chapter': chapter})

def view_chapter(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    
    # Only count views for published content
    if chapter.status == 'PUBLISHED':
        chapter.views += 1
        chapter.save()
        
    return render(request, 'newapp/view.html', {'chapter': chapter})
# Create your views here.

from django.contrib.auth.models import User
from django.db.models import Sum

def index(request):
    handpicked_books = Book.objects.filter(handpicked=True, status__in=['PUBLISHED', 'FINISHED']).annotate(
        total_likes=Count('likes', distinct=True),
        total_chapters=Count('chapters', filter=Q(chapters__status='PUBLISHED'), distinct=True)
    ).prefetch_related('likes', 'bookmarks').order_by('-created_at', '-id')[:8]
    
    # Calculate statistics
    writers_count = User.objects.filter(
        Q(book__isnull=False) | Q(script__isnull=False) | Q(poem__isnull=False)
    ).distinct().count()
    
    books_count = Book.objects.filter(status__in=['PUBLISHED', 'FINISHED']).count()
    scripts_count = Script.objects.filter(status='PUBLISHED').count()
    poems_count = Poem.objects.filter(status__in=['PUBLISHED', 'FINISHED']).count()
    stories_count = books_count + scripts_count + poems_count
    
    book_views = Book.objects.aggregate(Sum('views'))['views__sum'] or 0
    script_views = Script.objects.aggregate(Sum('views'))['views__sum'] or 0
    poem_views = Poem.objects.aggregate(Sum('views'))['views__sum'] or 0
    readers_count = book_views + script_views + poem_views
    
    # Genre counts
    genre_counts = {
        'Fiction': Book.objects.filter(genre__iexact='Fiction', status__in=['PUBLISHED', 'FINISHED']).count(),
        'Scripts': Script.objects.filter(status='PUBLISHED').count(),
        'Poetry': Book.objects.filter(genre__iexact='Poetry', status__in=['PUBLISHED', 'FINISHED']).count() + \
                  Poem.objects.filter(status__in=['PUBLISHED', 'FINISHED']).count(),
        'Fantasy': Book.objects.filter(genre__iexact='Fantasy', status__in=['PUBLISHED', 'FINISHED']).count(),
        'Romance': Book.objects.filter(genre__iexact='Romance', status__in=['PUBLISHED', 'FINISHED']).count(),
        'Adventure': Book.objects.filter(genre__iexact='Adventure', status__in=['PUBLISHED', 'FINISHED']).count(),
    }
    
    context = {
        'handpicked_books': handpicked_books,
        'writers_count': writers_count,
        'stories_count': stories_count,
        'readers_count': readers_count,
        'genre_counts': genre_counts,
    }
    return render(request, 'newapp/index.html', context)

from django.contrib.auth.decorators import login_required
from django.db.models import Sum

@login_required
def dashboard(request):
    user_books = Book.objects.filter(author=request.user).annotate(
        total_likes=Count('likes', distinct=True),
        total_chapters=Count('chapters', filter=Q(chapters__status='PUBLISHED'), distinct=True)
    )
    user_scripts = Script.objects.filter(author=request.user).annotate(
        total_likes=Count('likes', distinct=True),
        episode_count_attr=Count('episodes', filter=Q(episodes__status='PUBLISHED'), distinct=True)
    )
    user_poems = Poem.objects.filter(author=request.user).annotate(
        total_likes=Count('likes')
    )
    
    # Calculate aggregate stats
    book_views = user_books.aggregate(Sum('views'))['views__sum'] or 0
    script_views = user_scripts.aggregate(Sum('views'))['views__sum'] or 0
    poem_views = user_poems.aggregate(Sum('views'))['views__sum'] or 0
    total_views = book_views + script_views + poem_views
    
    book_likes = sum(book.total_likes for book in user_books)
    script_likes = sum(script.total_likes for script in user_scripts)
    poem_likes = sum(poem.total_likes for poem in user_poems)
    total_likes_sum = book_likes + script_likes + poem_likes
    
    total_stories = user_books.count() + user_scripts.count() + user_poems.count()
    
    context = {
        'user_books': user_books,
        'user_scripts': user_scripts,
        'user_poems': user_poems,
        'total_views': total_views,
        'total_likes': total_likes_sum,
        'total_stories': total_stories,
    }
    return render(request, 'newapp/dashboard.html', context)

@login_required
def manage_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, author=request.user)
    chapters = book.chapters.all().order_by('order')
    return render(request, 'newapp/manage_chapters.html', {'book': book, 'chapters': chapters})

@login_required
def manage_script(request, script_id):
    script = get_object_or_404(Script, id=script_id, author=request.user)
    episodes = script.episodes.all().order_by('order')
    return render(request, 'newapp/manage_episodes.html', {'script': script, 'episodes': episodes})

@login_required
def add_chapter(request, book_id):
    book = get_object_or_404(Book, id=book_id, author=request.user)
    # Find the next order number
    last_chapter = book.chapters.all().order_by('-order').first()
    next_order = (last_chapter.order + 1) if last_chapter else 1
    
    new_chapter = Chapter.objects.create(
        book=book,
        title=f"Chapter {next_order}",
        content="",
        order=next_order,
        status='DRAFT'
    )
    return redirect('write_chapter', chapter_id=new_chapter.id)

from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

@login_required
@require_POST
def save_chapter_ajax(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id, book__author=request.user)
    try:
        data = json.loads(request.body)
        content = data.get('content')
        title = data.get('title')
        status = data.get('status', 'DRAFT')
        
        if content is not None:
            chapter.content = content
        if title is not None:
            chapter.title = title

        # Only change status if explicitly publishing, OR if the chapter is still a draft.
        # Never downgrade a PUBLISHED chapter back to DRAFT on a plain save.
        if status == 'PUBLISHED':
            chapter.status = 'PUBLISHED'
            chapter.book.status = 'PUBLISHED'
            chapter.book.save()
        elif chapter.status != 'PUBLISHED':
            chapter.status = status
        
        chapter.save()
        return JsonResponse({'status': 'success', 'message': 'Chapter saved'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def add_chapter_ajax(request, book_id):
    book = get_object_or_404(Book, id=book_id, author=request.user)
    try:
        last_chapter = book.chapters.all().order_by('-order').first()
        next_order = (last_chapter.order + 1) if last_chapter else 1
        
        new_chapter = Chapter.objects.create(
            book=book,
            title=f"Chapter {next_order}",
            content="",
            order=next_order,
            status='DRAFT'
        )
        return JsonResponse({
            'status': 'success',
            'chapter_id': new_chapter.id,
            'title': new_chapter.title,
            'order': new_chapter.order
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def update_book_metadata_ajax(request, book_id):
    book = get_object_or_404(Book, id=book_id, author=request.user)
    try:
        genre = request.POST.get('genre')
        description = request.POST.get('description')
        cover_image = request.FILES.get('cover_image')
        status = request.POST.get('status')
        
        if genre:
            book.genre = genre
        if description:
            book.description = description
        if cover_image:
            book.cover_image = cover_image
        if status:
            book.status = status
            
        book.save()
        return JsonResponse({'status': 'success', 'message': 'Book details updated'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)



def poems(request):
    page_number = request.GET.get('page', 1)
    poems_list = Poem.objects.filter(status__in=['PUBLISHED', 'FINISHED']).order_by('-created_at', '-id')
    
    paginator = Paginator(poems_list, 9)
    page_obj = paginator.get_page(page_number)
    
    if request.GET.get('ajax'):
        if not page_obj.object_list:
            return HttpResponse("", status=200)
        response = render(request, 'newapp/partials/_poem_cards.html', {'poems': page_obj})
        response['X-Has-Next'] = 'true' if page_obj.has_next() else 'false'
        return response
        
    return render(request, 'newapp/poems.html', {
        'poems': page_obj,
        'has_next': page_obj.has_next(),
    })

def read_poem(request, poem_id):
    poem = get_object_or_404(Poem, id=poem_id, status='PUBLISHED')
    poem.views += 1
    poem.save()
    
    context = {
        'poem': poem,
        'liked': request.user.is_authenticated and request.user in poem.likes.all(),
        'bookmarked': request.user.is_authenticated and request.user in poem.bookmarks.all(),
    }
    return render(request, 'newapp/read_poem.html', context)

def toggle_like_poem(request, poem_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Log in required'}, status=403)
    poem = get_object_or_404(Poem, id=poem_id)
    if request.user in poem.likes.all():
        poem.likes.remove(request.user)
        liked = False
    else:
        poem.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': poem.likes.count()})

def toggle_bookmark_poem(request, poem_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Log in required'}, status=403)
    poem = get_object_or_404(Poem, id=poem_id)
    if request.user in poem.bookmarks.all():
        poem.bookmarks.remove(request.user)
        bookmarked = False
    else:
        poem.bookmarks.add(request.user)
        bookmarked = True
    return JsonResponse({'bookmarked': bookmarked})


def scripts(request):
    page_number = request.GET.get('page', 1)
    
    # Show ALL published scripts, prioritizing Handpicked.
    scripts_list = Script.objects.filter(status='PUBLISHED').annotate(
        total_likes=Count('likes', distinct=True),
        episode_count_attr=Count('episodes', filter=Q(episodes__status='PUBLISHED'), distinct=True)
    ).order_by('-handpicked', '-created_at')
        
    paginator = Paginator(scripts_list, 6)
    page_obj = paginator.get_page(page_number)
    
    if request.GET.get('ajax'):
        if not page_obj.object_list:
            return HttpResponse("", status=200)
        # We reuse 'books' context variable for compatibility with partials/_script_cards.html
        response = render(request, 'newapp/partials/_script_cards.html', {'books': page_obj})
        response['X-Has-Next'] = 'true' if page_obj.has_next() else 'false'
        return response
        
    return render(request, 'newapp/scripts.html', {
        'books': page_obj,
        'has_next': page_obj.has_next()
    })

def books(request):
    active_genre = request.GET.get('genre')
    page_number = request.GET.get('page', 1)
    
    # Filter for Published and Finished books (exclude Drafts)
    base_query = Book.objects.filter(status__in=['PUBLISHED', 'FINISHED'])

    if active_genre:
        books_list = base_query.filter(genre__iexact=active_genre).annotate(
            total_likes=Count('likes', distinct=True),
            total_chapters=Count('chapters', filter=Q(chapters__status='PUBLISHED'), distinct=True)
        ).prefetch_related('likes', 'bookmarks').order_by('-created_at', '-id')
    else:
        books_list = base_query.annotate(
            total_likes=Count('likes', distinct=True),
            total_chapters=Count('chapters', filter=Q(chapters__status='PUBLISHED'), distinct=True)
        ).prefetch_related('likes', 'bookmarks').order_by('-created_at', '-id')
        
    paginator = Paginator(books_list, 6)
    page_obj = paginator.get_page(page_number)
    
    if request.GET.get('ajax'):
        if not page_obj.object_list:
            return HttpResponse("", status=200)
        response = render(request, 'newapp/partials/_book_cards.html', {'books': page_obj})
        response['X-Has-Next'] = 'true' if page_obj.has_next() else 'false'
        return response

    new_releases = Book.objects.filter(status__in=['PUBLISHED', 'FINISHED']).distinct().annotate(
        total_likes=Count('likes', distinct=True),
        total_chapters=Count('chapters', filter=Q(chapters__status='PUBLISHED'), distinct=True)
    ).prefetch_related('likes', 'bookmarks').order_by('-created_at')[:4]
    
    return render(request, 'newapp/books.html', {
        'books': page_obj, 
        'active_genre': active_genre,
        'has_next': page_obj.has_next(),
        'new_releases': new_releases,
    })

def write(request):
    return  render(request,'newapp/write.html',{})

def discover(request):
    query = request.GET.get('q')
    if query:
        trending_books = Book.objects.filter(
            Q(status__in=['PUBLISHED', 'FINISHED']) & (
                Q(title__icontains=query) | 
                Q(author__username__icontains=query) |
                Q(genre__icontains=query)
            )
        ).annotate(total_likes=Count('likes', distinct=True)).order_by('-views', '-total_likes', '-id')
    else:
        # Get top 4 trending books
        trending_books = Book.objects.filter(status__in=['PUBLISHED', 'FINISHED']).annotate(
            total_likes=Count('likes', distinct=True)
        ).order_by('-views', '-total_likes', '-id')[:4]
    
    context = {
        'trending_books': trending_books,
        'search_query': query,
    }
    return render(request, 'newapp/discover.html', context)

def view_book_public(request, book_id):
    """Public view of a book showing all published chapters"""
    book = get_object_or_404(Book, id=book_id)
    
    # Get chapters: Author sees all (Draft + Published), others see only Published
    if request.user == book.author:
        chapters = book.chapters.all().order_by('order')
    else:
        chapters = book.chapters.filter(status='PUBLISHED').order_by('order')
    
    # Increment views count
    book.views += 1
    book.save()
    
    context = {
        'book': book,
        'chapters': chapters,
        'total_likes': book.likes.count(),
        'total_bookmarks': book.bookmarks.count(),
    }
    return render(request, 'newapp/book_view.html', context)

@login_required
@require_POST
def delete_book(request, book_id):
    """Delete a book (AJAX endpoint)"""
    try:
        book = get_object_or_404(Book, id=book_id, author=request.user)
        book_title = book.title
        book.delete()  # Cascades to chapters automatically
        return JsonResponse({
            'status': 'success',
            'message': f'"{book_title}" has been deleted successfully.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def delete_script(request, script_id):
    """Delete a script (AJAX endpoint)"""
    try:
        script = get_object_or_404(Script, id=script_id, author=request.user)
        script_title = script.title
        script.delete()
        return JsonResponse({
            'status': 'success',
            'message': f'"{script_title}" has been deleted successfully.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@require_POST
def delete_poem(request, poem_id):
    """Delete a poem (AJAX endpoint)"""
    try:
        poem = get_object_or_404(Poem, id=poem_id, author=request.user)
        poem_title = poem.title
        poem.delete()
        return JsonResponse({
            'status': 'success',
            'message': f'"{poem_title}" has been deleted successfully.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

def read_chapter(request, chapter_id):
    """Public chapter reading view"""
    chapter = get_object_or_404(Chapter, id=chapter_id)
    
    # Only show published chapters to public
    if chapter.status != 'PUBLISHED':
        # Allow author to preview their own drafts
        if not request.user.is_authenticated or chapter.book.author != request.user:
            return HttpResponse("This chapter is not published yet.", status=403)
    
    # Increment chapter views
    chapter.views += 1
    chapter.save()
    
    # Get all published chapters for navigation
    all_chapters = chapter.book.chapters.filter(status='PUBLISHED').order_by('order')
    
    # Find current chapter index for prev/next
    chapter_list = list(all_chapters)
    try:
        current_index = chapter_list.index(chapter)
        prev_chapter = chapter_list[current_index - 1] if current_index > 0 else None
        next_chapter = chapter_list[current_index + 1] if current_index < len(chapter_list) - 1 else None
    except ValueError:
        prev_chapter = None
        next_chapter = None
    
    context = {
        'chapter': chapter,
        'book': chapter.book,
        'prev_chapter': prev_chapter,
        'next_chapter': next_chapter,
        'all_chapters': all_chapters,
        'current_sequence': current_index + 1,
        'total_sequence': len(chapter_list),
        'progress_percent': int(((current_index + 1) / len(chapter_list)) * 100) if len(chapter_list) > 0 else 0,
        'liked': request.user.is_authenticated and request.user in chapter.likes.all(),
        'bookmarked': request.user.is_authenticated and request.user in chapter.book.bookmarks.all(),
    }
    return render(request, 'newapp/chapter_read.html', context)


# Static Pages
def about(request):
    """About page"""
    return render(request, 'newapp/about.html')

def contact(request):
    """Contact page"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            # Send email (console based on settings)
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message_content = form.cleaned_data['message']
            
            try:
                send_mail(
                    f"New Contact Message from {name}",
                    f"Name: {name}\nEmail: {email}\n\nMessage:\n{message_content}",
                    settings.DEFAULT_FROM_EMAIL,
                    ['kidusmezgebe2@gmail.com'],
                    reply_to=[email],
                    fail_silently=True,
                )
            except:
                pass
                
            messages.success(request, "Message sent! We will get back to you soon.")
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'newapp/contact.html', {'form': form})

def privacy(request):
    """Privacy Policy page"""
    return render(request, 'newapp/privacy.html')

def terms(request):
    """Terms of Service page"""
    return render(request, 'newapp/terms.html')

def writing_tips(request):
    return render(request, 'newapp/writing_tips.html')



def contests(request):
    return render(request, 'newapp/coming_soon.html', {'feature': 'Contests'})


@login_required
@require_POST
def submit_contest_entry(request):
    try:
        data = json.loads(request.body)
        contest_id = data.get('contest_id')
        work_id = data.get('work_id')
        work_type = data.get('work_type')
        
        # Check if user has phone number
        from newapp.models import AuthorProfile
        profile, created = AuthorProfile.objects.get_or_create(user=request.user)
        
        if not profile.phone_number:
            return JsonResponse({
                'status': 'error', 
                'message': 'Phone number required', 
                'phone_required': True
            }, status=400)
        
        contest = get_object_or_404(Contest, id=contest_id)
        
        # Verify the work belongs to the user AND is published
        if work_type == 'Book':
            work = get_object_or_404(Book, id=work_id, author=request.user, status__in=['PUBLISHED', 'FINISHED'])
            contest.entry_books.add(work)
        elif work_type == 'Script':
            work = get_object_or_404(Script, id=work_id, author=request.user, status='PUBLISHED')
            contest.entry_scripts.add(work)
        elif work_type == 'Poem':
            work = get_object_or_404(Poem, id=work_id, author=request.user, status='PUBLISHED')
            contest.entry_poems.add(work)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid work type'}, status=400)
            
        return JsonResponse({'status': 'success', 'message': 'Entry submitted successfully!'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def update_phone_number(request):
    try:
        data = json.loads(request.body)
        phone_number = data.get('phone_number', '').strip()
        
        if not phone_number:
            return JsonResponse({'status': 'error', 'message': 'Phone number is required'}, status=400)
        
        # Validate phone number format
        import re
        if not re.match(r'^\+?1?\d{9,15}$', phone_number):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid phone number format. Use format: +999999999 (9-15 digits)'
            }, status=400)
        
        # Get or create profile
        from newapp.models import AuthorProfile
        profile, created = AuthorProfile.objects.get_or_create(user=request.user)
        profile.phone_number = phone_number
        profile.save()
        
        return JsonResponse({'status': 'success', 'message': 'Phone number saved successfully!'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def toggle_like_chapter(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    if request.user in chapter.likes.all():
        chapter.likes.remove(request.user)
        liked = False
    else:
        chapter.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': chapter.likes.count()})

@login_required
@require_POST
def toggle_bookmark_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.user in book.bookmarks.all():
        book.bookmarks.remove(request.user)
        bookmarked = False
    else:
        book.bookmarks.add(request.user)
        bookmarked = True
    return JsonResponse({'bookmarked': bookmarked, 'count': book.bookmarks.count()})

@login_required
@require_POST
def toggle_like_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.user in book.likes.all():
        book.likes.remove(request.user)
        liked = False
    else:
        book.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': book.likes.count()})

@login_required
@require_POST
def toggle_like_script(request, script_id):
    script = get_object_or_404(Script, id=script_id)
    if request.user in script.likes.all():
        script.likes.remove(request.user)
        liked = False
    else:
        script.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': script.likes.count()})

@login_required
@require_POST
def toggle_bookmark_script(request, script_id):
    script = get_object_or_404(Script, id=script_id)
    if request.user in script.bookmarks.all():
        script.bookmarks.remove(request.user)
        bookmarked = False
    else:
        script.bookmarks.add(request.user)
        bookmarked = True
    return JsonResponse({'bookmarked': bookmarked, 'count': script.bookmarks.count()})

@login_required
def write_script(request, script_id):
    script = get_object_or_404(Script, id=script_id, author=request.user)
    return render(request, 'newapp/write.html', {'script': script})

@login_required
@require_POST
def create_script_ajax(request):
    try:
        if request.content_type.split(';')[0] == 'application/json':
            data = json.loads(request.body)
            content = data.get('content', '')
            title = data.get('title', 'Untitled Script')
            status = data.get('status', 'DRAFT')
            contest_id = data.get('contest_id')
            script_format = data.get('script_format', 'FEATURE_FILM')
            
            script = Script.objects.create(
                author=request.user,
                title=title,
                content=content if script_format == 'FEATURE_FILM' else '',
                status=status,
                script_format=script_format
            )

            if script_format == 'EPISODIC':
                ScriptEpisode.objects.create(
                    script=script,
                    title="Episode 1",
                    content=content,
                    status=status
                )
            
            if contest_id:
                try:
                    contest = Contest.objects.get(id=contest_id)
                    contest.entry_scripts.add(script)
                except Contest.DoesNotExist:
                    pass

            return JsonResponse({'status': 'success', 'script_id': script.id, 'message': 'Script created'})
        
        return JsonResponse({'status': 'error', 'message': 'Invalid content type'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def read_script(request, script_id):
    from django.shortcuts import redirect as django_redirect
    script = get_object_or_404(Script, id=script_id)

    # For EPISODIC scripts, redirect to the first published episode
    if script.script_format == 'EPISODIC':
        is_author = request.user.is_authenticated and script.author == request.user
        if is_author:
            # Authors see the first episode (published or draft)
            first_episode = script.episodes.all().order_by('order').first()
        else:
            # Regular visitors only see the first published episode
            first_episode = script.episodes.filter(status='PUBLISHED').order_by('order').first()
        
        if first_episode:
            from django.urls import reverse
            return django_redirect(reverse('read_episode', args=[first_episode.id]))
        else:
            # No episodes available - show a placeholder page rather than raw script
            return HttpResponse("No published episodes yet.", status=404)

    # Increment views (for non-episodic scripts only)
    Script.objects.filter(id=script_id).update(views=F('views') + 1)
    script.refresh_from_db()
    
    context = {
        'script': script,
        'liked': request.user.is_authenticated and request.user in script.likes.all(),
        'bookmarked': request.user.is_authenticated and request.user in script.bookmarks.all(),
    }
    
    return render(request, 'newapp/read_script.html', context)

@login_required
@require_POST
def save_script_ajax(request, script_id):
    script = get_object_or_404(Script, id=script_id, author=request.user)
    try:
        # Check if multipart form data (for cover image) or json
        if request.content_type.split(';')[0] == 'application/json':
            data = json.loads(request.body)
            content = data.get('content')
            page_count = data.get('page_count')
            status = data.get('status') # DRAFT or PUBLISHED
            title = data.get('title')
            description = data.get('description')
            
            if content is not None:
                script.content = content
            if page_count is not None:
                script.page_count = page_count
            if status:
                script.status = status
            if title:
                script.title = title
            if description:
                script.description = description
                
            script.save()
            return JsonResponse({'status': 'success', 'message': 'Script saved'})
        else:
            # Multipart form (e.g. for cover image + data)
            title = request.POST.get('title')
            description = request.POST.get('description')
            content = request.POST.get('content')
            page_count = request.POST.get('page_count')
            status = request.POST.get('status')
            cover = request.FILES.get('cover_image')

            if title: script.title = title
            if description: script.description = description
            if content: script.content = content
            if page_count: script.page_count = page_count
            if status: script.status = status
            if cover: script.cover_image = cover
            
            script.save()
            return JsonResponse({'status': 'success', 'message': 'Script published/updated'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
@login_required
def write_episode(request, episode_id):
    episode = get_object_or_404(ScriptEpisode, id=episode_id, script__author=request.user)
    return render(request, 'newapp/write.html', {'episode': episode, 'script': episode.script})

def read_episode(request, episode_id):
    episode = get_object_or_404(ScriptEpisode, id=episode_id)
    
    # Security check: Only author can view drafts
    if episode.status != 'PUBLISHED':
        if not request.user.is_authenticated or episode.script.author != request.user:
            return HttpResponse("This episode is not published yet.", status=403)
            
    if episode.status == 'PUBLISHED':
        episode.views += 1
        episode.save()
        
    next_episode = ScriptEpisode.objects.filter(script=episode.script, order__gt=episode.order, status='PUBLISHED').order_by('order').first()
    prev_episode = ScriptEpisode.objects.filter(script=episode.script, order__lt=episode.order, status='PUBLISHED').order_by('-order').first()
    published_episodes = ScriptEpisode.objects.filter(script=episode.script, status='PUBLISHED').order_by('order')
    
    return render(request, 'newapp/read_script.html', {
        'episode': episode, 
        'script': episode.script,
        'next_episode': next_episode,
        'prev_episode': prev_episode,
        'published_episodes': published_episodes
    })

@login_required
@require_POST
def save_episode_ajax(request, episode_id):
    episode = get_object_or_404(ScriptEpisode, id=episode_id, script__author=request.user)
    try:
        data = json.loads(request.body)
        content = data.get('content')
        title = data.get('title')
        status = data.get('status', 'DRAFT')
        
        if content is not None:
            episode.content = content
        if title is not None:
            episode.title = title

        if status == 'PUBLISHED':
            episode.status = 'PUBLISHED'
            episode.script.status = 'PUBLISHED'
            episode.script.save()
        elif episode.status != 'PUBLISHED':
            episode.status = status
            
        episode.save()
        return JsonResponse({'status': 'success', 'message': 'Episode saved'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def add_episode_ajax(request, script_id):
    script = get_object_or_404(Script, id=script_id, author=request.user)
    try:
        last_epi = script.episodes.all().order_by('-order').first()
        next_order = (last_epi.order + 1) if last_epi else 1
        
        new_epi = ScriptEpisode.objects.create(
            script=script,
            title=f"Episode {next_order}",
            content="",
            order=next_order,
            status='DRAFT'
        )
        return JsonResponse({
            'status': 'success',
            'episode_id': new_epi.id,
            'title': new_epi.title,
            'order': new_epi.order
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
def write_poem(request, poem_id):
    poem = get_object_or_404(Poem, id=poem_id, author=request.user)
    return render(request, 'newapp/write.html', {'poem': poem})

@login_required
@require_POST
def create_poem_ajax(request):
    try:
        if request.content_type.split(';')[0] == 'application/json':
            data = json.loads(request.body)
            content = data.get('content', '')
            title = data.get('title', 'Untitled Poem')
            description = data.get('description', '')
            contest_id = data.get('contest_id')
            
            status = data.get('status', 'DRAFT')
            poem = Poem.objects.create(
                author=request.user,
                title=title,
                content=content,
                status=status,
                description=description
            )
            
            if contest_id:
                try:
                    contest = Contest.objects.get(id=contest_id)
                    contest.entry_poems.add(poem)
                except Contest.DoesNotExist:
                    pass

            return JsonResponse({'status': 'success', 'poem_id': poem.id, 'message': 'Poem created'})
        return JsonResponse({'status': 'error', 'message': 'Invalid content type'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def save_poem_ajax(request, poem_id):
    poem = get_object_or_404(Poem, id=poem_id, author=request.user)
    try:
        if request.content_type.split(';')[0] == 'application/json':
            data = json.loads(request.body)
            content = data.get('content')
            status = data.get('status')
            title = data.get('title')
            description = data.get('description')
            
            if content is not None: poem.content = content
            if status: poem.status = status
            if title: poem.title = title
            if description: poem.description = description
                
            poem.save()
            return JsonResponse({'status': 'success', 'message': 'Poem saved'})
        else:
            title = request.POST.get('title')
            description = request.POST.get('description')
            content = request.POST.get('content')
            status = request.POST.get('status')
            cover = request.FILES.get('cover_image')

            if title: poem.title = title
            if description: poem.description = description
            if content: poem.content = content
            if status: poem.status = status
            if cover: poem.cover_image = cover
            
            poem.save()
            return JsonResponse({'status': 'success', 'message': 'Poem updated'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def reviews_page(request):
    from .models import Movie, BookReview
    query = request.GET.get('q', '')
    movie_page = request.GET.get('movie_page', 1)
    book_page = request.GET.get('book_page', 1)
    
    movies_qs = Movie.objects.all().order_by('-created_at')
    books_qs = BookReview.objects.all().order_by('-created_at')
    
    if query:
        movies_qs = movies_qs.filter(Q(title__icontains=query) | Q(genre__icontains=query))
        books_qs = books_qs.filter(Q(title__icontains=query) | Q(genre__icontains=query) | Q(author_name__icontains=query))
    
    movie_paginator = Paginator(movies_qs, 8)
    movie_obj = movie_paginator.get_page(movie_page)
    
    book_paginator = Paginator(books_qs, 8)
    book_obj = book_paginator.get_page(book_page)

    if request.GET.get('ajax'):
        target = request.GET.get('target', 'movie')
        if target == 'movie':
            if not movie_obj.object_list: return HttpResponse("", status=200)
            response = render(request, 'newapp/partials/_movie_card_list.html', {'movies': movie_obj})
            response['X-Has-Next'] = 'true' if movie_obj.has_next() else 'false'
            return response
        else:
            if not book_obj.object_list: return HttpResponse("", status=200)
            response = render(request, 'newapp/partials/_book_review_card_list.html', {'books': book_obj})
            response['X-Has-Next'] = 'true' if book_obj.has_next() else 'false'
            return response
    
    return render(request, 'newapp/movie_reviews.html', {
        'movies': movie_obj,
        'books': book_obj,
        'movie_has_next': movie_obj.has_next(),
        'book_has_next': book_obj.has_next(),
        'query': query
    })

def movie_detail_page(request, movie_id):
    from .models import Movie
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'newapp/movie_detail.html', {'movie': movie})


@login_required
def ajax_add_movie(request):
    if request.method == 'POST':
        from .models import Movie
        title = request.POST.get('title')
        genre = request.POST.get('genre')
        year = request.POST.get('year')
        cover_image = request.FILES.get('cover_image')
        
        if title:
            # Handle year conversion safely
            try:
                year_int = int(year) if year else None
            except ValueError:
                year_int = None
                
            movie = Movie.objects.create(
                title=title,
                genre=genre,
                year=year_int,
                added_by=request.user,
                cover_image=cover_image
            )
            html = render_to_string('newapp/partials/_movie_card.html', {'movie': movie}, request=request)
            return JsonResponse({'success': True, 'html': html})
    return JsonResponse({'success': False})

@login_required
def ajax_add_movie_comment(request, movie_id):
    if request.method == 'POST':
        from .models import Movie, MovieComment
        movie = get_object_or_404(Movie, id=movie_id)
        content = request.POST.get('content')
        if content:
            comment = MovieComment.objects.create(
                movie=movie,
                user=request.user,
                content=content
            )
            html = render_to_string('newapp/partials/_movie_comment.html', {'comment': comment}, request=request)
            return JsonResponse({'success': True, 'html': html, 'comment_count': movie.comments.count()})
    return JsonResponse({'success': False})

@login_required
def ajax_rate_movie(request, movie_id):
    if request.method == 'POST':
        from .models import Movie, MovieRating
        movie = get_object_or_404(Movie, id=movie_id)
        rating_val = request.POST.get('rating')
        try:
            rating_val = int(rating_val)
            if 1 <= rating_val <= 5:
                rating, created = MovieRating.objects.update_or_create(
                    movie=movie,
                    user=request.user,
                    defaults={'rating': rating_val}
                )
                return JsonResponse({
                    'success': True, 
                    'average_rating': round(movie.average_rating, 1),
                    'rating_count': movie.ratings.count()
                })
        except ValueError:
            pass
    return JsonResponse({'success': False})

def book_review_detail_page(request, book_review_id):
    from .models import BookReview
    book_review = get_object_or_404(BookReview, id=book_review_id)
    return render(request, 'newapp/book_review_detail.html', {'book_review': book_review})

@login_required
def ajax_add_book_review(request):
    if request.method == 'POST':
        from .models import BookReview
        title = request.POST.get('title')
        author_name = request.POST.get('author_name')
        genre = request.POST.get('genre')
        year = request.POST.get('year')
        cover_image = request.FILES.get('cover_image')
        
        if title:
            try:
                year_int = int(year) if year else None
            except ValueError:
                year_int = None
                
            book_review = BookReview.objects.create(
                title=title,
                author_name=author_name,
                genre=genre,
                year=year_int,
                added_by=request.user,
                cover_image=cover_image
            )
            html = render_to_string('newapp/partials/_book_review_card.html', {'book_review': book_review}, request=request)
            return JsonResponse({'success': True, 'html': html})
    return JsonResponse({'success': False})

@login_required
def ajax_add_book_comment(request, book_review_id):
    if request.method == 'POST':
        from .models import BookReview, BookReviewComment
        book_review = get_object_or_404(BookReview, id=book_review_id)
        content = request.POST.get('content')
        if content:
            comment = BookReviewComment.objects.create(
                book_review=book_review,
                user=request.user,
                content=content
            )
            html = render_to_string('newapp/partials/_book_comment.html', {'comment': comment}, request=request)
            return JsonResponse({'success': True, 'html': html, 'comment_count': book_review.comments.count()})
    return JsonResponse({'success': False})

@login_required
def ajax_rate_book_review(request, book_review_id):
    if request.method == 'POST':
        from .models import BookReview, BookReviewRating
        book_review = get_object_or_404(BookReview, id=book_review_id)
        rating_val = request.POST.get('rating')
        try:
            rating_val = int(rating_val)
            if 1 <= rating_val <= 5:
                rating, created = BookReviewRating.objects.update_or_create(
                    book_review=book_review,
                    user=request.user,
                    defaults={'rating': rating_val}
                )
                return JsonResponse({
                    'success': True, 
                    'average_rating': round(book_review.average_rating, 1),
                    'rating_count': book_review.ratings.count()
                })
        except ValueError:
            pass
    return JsonResponse({'success': False})

# --- RECOVERED PROFILE VIEWS ---
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from .models import AuthorProfile, ProfileComment, Confession, ConfessionComment

def profile_view(request, username):
    from .models import AuthorProfile, ProfileComment
    user_prof = get_object_or_404(User, username=username)
    profile, _ = AuthorProfile.objects.get_or_create(user=user_prof)
    
    # Get works
    books = list(user_prof.book_set.filter(status='PUBLISHED'))
    scripts = list(user_prof.script_set.filter(status='PUBLISHED'))
    poems = list(user_prof.poem_set.filter(status='PUBLISHED'))
    works = sorted(books + scripts + poems, key=lambda x: x.created_at, reverse=True)
    
    # Get profile comments (only top-level threads for the initial load)
    comments = profile.comments.filter(parent=None).all()
    
    return render(request, 'newapp/profile.html', {
        'profile': profile,
        'profile_user': user_prof,
        'works': works,
        'comments': comments
    })

@login_required
def edit_profile(request):
    from .forms import AuthorProfileForm
    profile, _ = AuthorProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = AuthorProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            # Update the username on the User model
            new_username = form.cleaned_data['username']
            if request.user.username != new_username:
                request.user.username = new_username
                request.user.save(update_fields=['username'])
            return redirect('profile_view', username=request.user.username)
    else:
        form = AuthorProfileForm(instance=profile, user=request.user)

    return render(request, 'newapp/edit_profile.html', {
        'form': form,
        'profile': profile
    })

@login_required
@require_POST
def add_profile_comment(request, username):
    user_prof = get_object_or_404(User, username=username)
    profile = get_object_or_404(AuthorProfile, user=user_prof)
    content = request.POST.get('content')
    parent_id = request.POST.get('parent_id')
    
    if content:
        parent = None
        if parent_id:
            try:
                parent = ProfileComment.objects.get(id=parent_id)
            except ProfileComment.DoesNotExist:
                pass
        
        # Enforce: Only profile owner can start a new thread. Visitors MUST reply.
        if not parent and request.user != profile.user:
            return JsonResponse({'success': False, 'message': 'Visitors can only reply to existing comments.'}, status=403)
            
        ProfileComment.objects.create(
            profile=profile, 
            author=request.user, 
            content=content,
            parent=parent
        )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        comments = profile.comments.filter(parent=None).all()
        html = render_to_string('newapp/partials/_profile_comments.html', {'comments': comments, 'profile': profile}, request=request)
        return JsonResponse({'success': True, 'html': html, 'comment_count': profile.comments.count()})
        
    return redirect('profile_view', username=username)

def get_profile_comments_ajax(request, username):
    user_prof = get_object_or_404(User, username=username)
    profile = get_object_or_404(AuthorProfile, user=user_prof)
    comments = profile.comments.filter(parent=None).all()
    html = render_to_string('newapp/partials/_profile_comments.html', {'comments': comments, 'profile': profile}, request=request)
    return JsonResponse({'success': True, 'html': html})

def authors_list(request):
    profiles = AuthorProfile.objects.all()
    
    author_list = []
    for profile in profiles:
        user = profile.user
        
        books = list(user.book_set.filter(status='PUBLISHED'))
        scripts = list(user.script_set.filter(status='PUBLISHED'))
        poems = list(user.poem_set.filter(status='PUBLISHED'))
        
        all_works = sorted(books + scripts + poems, key=lambda x: x.created_at, reverse=True)
        
        if not all_works:
            continue
            
        profile.works_count = len(all_works)
        profile.latest_works = all_works[:3]
        author_list.append(profile)

    paginator = Paginator(author_list, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.GET.get('ajax'):
        if not page_obj.object_list:
            return HttpResponse("", status=200)
        response = render(request, 'newapp/partials/_author_cards.html', {'page_obj': page_obj})
        response['X-Has-Next'] = 'true' if page_obj.has_next() else 'false'
        return response

    return render(request, 'newapp/authors.html', {
        'page_obj': page_obj,
        'has_next': page_obj.has_next()
    })

# --- RECOVERED CONFESSION VIEWS ---

def confessions_page(request):
    return render(request, 'newapp/confessions.html')

def get_confessions_ajax(request):
    confessions_list = Confession.objects.all().order_by('-created_at')
    
    # Add Paginator for infinite scroll
    paginator = Paginator(confessions_list, 10) # Load 10 at a time
    page_number = request.GET.get('page', 1)
    
    try:
        confessions = paginator.page(page_number)
    except Exception:
        # If page is out of range, return empty HTML to signal end of feed
        return JsonResponse({'html': ''})

    # Adding is_liked attr for the template
    if request.user.is_authenticated:
        user_likes = request.user.liked_confessions.values_list('id', flat=True)
        for conf in confessions:
            conf.is_liked = conf.id in user_likes
            
    html = render_to_string('newapp/partials/_confession_list.html', {'confessions': confessions}, request=request)
    return JsonResponse({'html': html})

@require_POST
def add_confession_ajax(request):
    content = request.POST.get('content')
    if content:
        user = request.user if request.user.is_authenticated else None
        confession = Confession.objects.create(content=content, user=user)
        if request.user.is_authenticated:
            confession.is_liked = False
        html = render_to_string('newapp/partials/_confession_list.html', {'confessions': [confession]}, request=request)
        return JsonResponse({'success': True, 'html': html})
    return JsonResponse({'success': False})

@login_required
@require_POST
def toggle_like_confession(request, confession_id):
    confession = get_object_or_404(Confession, id=confession_id)
    if request.user in confession.likes.all():
        confession.likes.remove(request.user)
        liked = False
    else:
        confession.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': confession.likes.count()})

@login_required
@require_POST
def add_confession_comment_ajax(request, confession_id):
    confession = get_object_or_404(Confession, id=confession_id)
    content = request.POST.get('content')
    if content:
        comment = ConfessionComment.objects.create(
            confession=confession, 
            content=content,
            user=request.user
        )
        html = render_to_string('newapp/partials/_confession_list.html', {'confessions': [confession]}, request=request)
        return JsonResponse({'success': True, 'html': html})
    return JsonResponse({'success': False})

@login_required
@require_POST
def ajax_delete_movie_comment(request, comment_id):
    from .models import MovieComment
    comment = get_object_or_404(MovieComment, id=comment_id)
    if comment.user != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Permission denied.'}, status=403)
    movie = comment.movie
    movie_id = movie.id
    comment.delete()
    return JsonResponse({'success': True, 'comment_count': movie.comments.count(), 'movie_id': movie_id})

@login_required
@require_POST
def ajax_delete_book_comment(request, comment_id):
    from .models import BookReviewComment
    comment = get_object_or_404(BookReviewComment, id=comment_id)
    if comment.user != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Permission denied.'}, status=403)
    book_review = comment.book_review
    book_review_id = book_review.id
    comment.delete()
    return JsonResponse({'success': True, 'comment_count': book_review.comments.count(), 'book_review_id': book_review_id})

@login_required
@require_POST
def ajax_delete_profile_comment(request, comment_id):
    from .models import ProfileComment
    comment = get_object_or_404(ProfileComment, id=comment_id)
    if comment.author != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Permission denied.'}, status=403)
    profile = comment.profile
    username = profile.user.username
    comment.delete()
    
    # We need to re-fetch comments to render partial correctly
    comments = profile.comments.filter(parent=None).all()
    html = render_to_string('newapp/partials/_profile_comments.html', {'comments': comments, 'profile': profile}, request=request)
    return JsonResponse({'success': True, 'html': html, 'comment_count': profile.comments.count(), 'username': username})

@login_required
@require_POST
def ajax_delete_confession(request, confession_id):
    confession = get_object_or_404(Confession, id=confession_id)
    if confession.user != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Permission denied.'}, status=403)
    confession.delete()
    return JsonResponse({'success': True})

@login_required
@require_POST
def ajax_delete_confession_comment(request, comment_id):
    comment = get_object_or_404(ConfessionComment, id=comment_id)
    if comment.user != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Permission denied.'}, status=403)
    confession_id = comment.confession.id
    comment.delete()
    return JsonResponse({'success': True, 'confession_id': confession_id})

@login_required
@require_POST
def ajax_delete_movie(request, movie_id):
    from .models import Movie
    movie = get_object_or_404(Movie, id=movie_id)
    if movie.added_by != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Permission denied.'}, status=403)
    movie.delete()
    return JsonResponse({'success': True})

@login_required
@require_POST
def ajax_delete_book_review(request, review_id):
    from .models import BookReview
    review = get_object_or_404(BookReview, id=review_id)
    if review.added_by != request.user and not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Permission denied.'}, status=403)
    review.delete()
    return JsonResponse({'success': True})

@login_required
@require_POST
def ajax_upload_cover(request, item_type, item_id):
    from .models import Book, Script, Poem
    cover_image = request.FILES.get('cover_image')
    if not cover_image:
        return JsonResponse({'success': False, 'message': 'No image provided'})

    try:
        if item_type == 'book':
            item = get_object_or_404(Book, id=item_id, author=request.user)
        elif item_type == 'script':
            item = get_object_or_404(Script, id=item_id, author=request.user)
        elif item_type == 'poem':
            item = get_object_or_404(Poem, id=item_id, author=request.user)
        else:
            return JsonResponse({'success': False, 'message': 'Invalid item type'})

        item.cover_image = cover_image
        item.save()
        return JsonResponse({'success': True, 'url': item.cover_image.url})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_POST
def ajax_remove_cover(request, item_type, item_id):
    from .models import Book, Script, Poem
    try:
        if item_type == 'book':
            item = get_object_or_404(Book, id=item_id, author=request.user)
        elif item_type == 'script':
            item = get_object_or_404(Script, id=item_id, author=request.user)
        elif item_type == 'poem':
            item = get_object_or_404(Poem, id=item_id, author=request.user)
        else:
            return JsonResponse({'success': False, 'message': 'Invalid item type'})

        if item.cover_image:
            item.cover_image.delete(save=False)
            item.cover_image = None
            item.save()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_POST
def ajax_update_status(request, item_type, item_id):
    from .models import Book, Script, Poem
    import json
    try:
        data = json.loads(request.body)
        status = data.get('status')
        if not status:
            return JsonResponse({'success': False, 'message': 'Status not provided'})

        if item_type == 'book':
            item = get_object_or_404(Book, id=item_id, author=request.user)
            valid_statuses = dict(Book.STATUS_CHOICES).keys()
        elif item_type == 'script':
            item = get_object_or_404(Script, id=item_id, author=request.user)
            valid_statuses = dict(Script.STATUS_CHOICES).keys()
        elif item_type == 'poem':
            item = get_object_or_404(Poem, id=item_id, author=request.user)
            valid_statuses = dict(Poem.STATUS_CHOICES).keys()
        else:
            return JsonResponse({'success': False, 'message': 'Invalid item type'})

        if status not in valid_statuses:
            return JsonResponse({'success': False, 'message': 'Invalid status'})

        item.status = status
        item.save()

        # When an EPISODIC series is published, also publish the first episode
        if item_type == 'script' and status == 'PUBLISHED' and item.script_format == 'EPISODIC':
            first_episode = item.episodes.order_by('order').first()
            if first_episode and first_episode.status != 'PUBLISHED':
                first_episode.status = 'PUBLISHED'
                first_episode.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
