"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from newapp.views import index, scripts , books , poems, write, write_chapter , create_content, discover, dashboard, manage_book, add_chapter, save_chapter_ajax, add_chapter_ajax, update_book_metadata_ajax, view_book_public, delete_book, read_chapter, about, contact, privacy, terms, toggle_like_chapter, toggle_bookmark_book, toggle_like_book, writing_tips, contests, write_script, save_script_ajax, create_script_ajax, read_script, read_poem, coming_soon, write_poem, create_poem_ajax, save_poem_ajax, toggle_like_script, toggle_bookmark_script, toggle_like_poem, toggle_bookmark_poem, delete_book_ajax, submit_contest_entry, update_phone_number, reviews_page, movie_detail_page, ajax_add_movie, ajax_add_movie_comment, ajax_rate_movie, ajax_delete_movie_comment, book_review_detail_page, ajax_add_book_review, ajax_add_book_comment, ajax_rate_book_review, ajax_delete_book_comment, ajax_delete_profile_comment, profile_view, edit_profile, add_profile_comment, get_profile_comments_ajax, authors_list, confessions_page, get_confessions_ajax, add_confession_ajax, toggle_like_confession, add_confession_comment_ajax


urlpatterns = [
    path('coming-soon/', coming_soon, name='coming_soon'),
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('discover/', discover, name='discover'),
    path('dashboard/', dashboard, name='dashboard'),
    path('book/<int:book_id>/manage/', manage_book, name='manage_book'),
    path('book/<int:book_id>/add-chapter/', add_chapter, name='add_chapter'),
    path('ajax/save-chapter/<int:chapter_id>/', save_chapter_ajax, name='save_chapter_ajax'),
    path('ajax/add-chapter/<int:book_id>/', add_chapter_ajax, name='add_chapter_ajax'),
    path('ajax/update-book-metadata/<int:book_id>/', update_book_metadata_ajax, name='update_book_metadata_ajax'),
    path('book/<int:book_id>/view/', view_book_public, name='view_book_public'),
    path('ajax/delete-book/<int:book_id>/', delete_book, name='delete_book'),
    path('chapter/<int:chapter_id>/read/', read_chapter, name='read_chapter'),

    path('poems/', poems, name='poems'),
    path('scripts/', scripts, name='scripts'),
    path('books/', books, name='books'),
    path('write/', write, name='write'),
    path('accounts/', include('allauth.urls')), 
    path('write/new/', create_content, name='create_content'),
    path('chapter/write/<int:chapter_id>/', write_chapter, name='write_chapter'),# This handles everything
    path('script/write/<int:script_id>/', write_script, name='write_script'),
    path('script/read/<int:script_id>/', read_script, name='read_script'),
    path('poem/read/<int:poem_id>/', read_poem, name='read_poem'),
    path('ajax/create-script/', create_script_ajax, name='create_script_ajax'),
    path('ajax/save-script/<int:script_id>/', save_script_ajax, name='save_script_ajax'),
    path('poem/write/<int:poem_id>/', write_poem, name='write_poem'),
    path('ajax/create-poem/', create_poem_ajax, name='create_poem_ajax'),
    path('ajax/save-poem/<int:poem_id>/', save_poem_ajax, name='save_poem_ajax'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('privacy/', privacy, name='privacy'),
    path('terms/', terms, name='terms'),
    path('writing-tips/', writing_tips, name='writing_tips'),

    path('contests/', contests, name='contests'),
    path('ajax/toggle-like-chapter/<int:chapter_id>/', toggle_like_chapter, name='toggle_like_chapter'),
    path('ajax/toggle-bookmark-book/<int:book_id>/', toggle_bookmark_book, name='toggle_bookmark_book'),
    path('ajax/toggle-like-book/<int:book_id>/', toggle_like_book, name='toggle_like_book'),
    path('ajax/toggle-like-script/<int:script_id>/', toggle_like_script, name='toggle_like_script'),
    path('ajax/toggle-bookmark-script/<int:script_id>/', toggle_bookmark_script, name='toggle_bookmark_script'),
    path('ajax/toggle-like-poem/<int:poem_id>/', toggle_like_poem, name='toggle_like_poem'),
    path('ajax/toggle-bookmark-poem/<int:poem_id>/', toggle_bookmark_poem, name='toggle_bookmark_poem'),
    path('ajax/delete-book/<int:book_id>/', delete_book_ajax, name='delete_book_ajax'),
    path('ajax/submit-contest-entry/', submit_contest_entry, name='submit_contest_entry'),
    path('ajax/update-phone-number/', update_phone_number, name='update_phone_number'),
    
    # Profile & Authors
    path('profile/<str:username>/', profile_view, name='profile_view'),
    path('profile/edit/me/', edit_profile, name='edit_profile'),
    path('profile/<str:username>/comment/', add_profile_comment, name='add_profile_comment'),
    path('ajax/profile/<str:username>/comments/', get_profile_comments_ajax, name='get_profile_comments_ajax'),
    path('authors/', authors_list, name='authors_list'),
    
    # Confessions
    path('confessions/', confessions_page, name='confessions'),
    path('ajax/confessions/', get_confessions_ajax, name='get_confessions_ajax'),
    path('ajax/confessions/add/', add_confession_ajax, name='add_confession_ajax'),
    path('ajax/confessions/<int:confession_id>/like/', toggle_like_confession, name='toggle_like_confession'),
    path('ajax/confessions/<int:confession_id>/comment/', add_confession_comment_ajax, name='add_confession_comment_ajax'),
    
    # Movie & Book Reviews
    path('reviews/', reviews_page, name='movie_reviews'),
    path('reviews/movie/<int:movie_id>/', movie_detail_page, name='movie_detail'),
    path('reviews/book/<int:book_review_id>/', book_review_detail_page, name='book_review_detail'),
    path('ajax/reviews/movie/add/', ajax_add_movie, name='ajax_add_movie'),
    path('ajax/reviews/book/add/', ajax_add_book_review, name='ajax_add_book_review'),
    path('ajax/reviews/movie/<int:movie_id>/comment/', ajax_add_movie_comment, name='ajax_add_movie_comment'),
    path('ajax/reviews/book/<int:book_review_id>/comment/', ajax_add_book_comment, name='ajax_add_book_comment'),
    path('ajax/reviews/movie/<int:movie_id>/rate/', ajax_rate_movie, name='ajax_rate_movie'),
    path('ajax/reviews/book/<int:book_review_id>/rate/', ajax_rate_book_review, name='ajax_rate_book_review'),
    path('ajax/reviews/movie/comment/<int:comment_id>/delete/', ajax_delete_movie_comment, name='ajax_delete_movie_comment'),
    path('ajax/reviews/book/comment/<int:comment_id>/delete/', ajax_delete_book_comment, name='ajax_delete_book_comment'),
    path('ajax/profile/comment/<int:comment_id>/delete/', ajax_delete_profile_comment, name='ajax_delete_profile_comment'),
]



from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
