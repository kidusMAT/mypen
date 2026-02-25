from django.contrib import admin
from django import forms

from .models import AuthorProfile, Book, Chapter, Contest, Script, Poem

admin.site.register(AuthorProfile)
admin.site.register(Book)
admin.site.register(Chapter)

class ContestAdminForm(forms.ModelForm):
    class Meta:
        model = Contest
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing an existing contest, filter winner choices to only show entries
        if self.instance and self.instance.pk:
            # Filter winning_book to only show books that are in entry_books
            self.fields['winning_book'].queryset = self.instance.entry_books.all()
            
            # Filter winning_script to only show scripts that are in entry_scripts
            self.fields['winning_script'].queryset = self.instance.entry_scripts.all()
            
            # Filter winning_poem to only show poems that are in entry_poems
            self.fields['winning_poem'].queryset = self.instance.entry_poems.all()

@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    form = ContestAdminForm
    list_display = ('title', 'contest_type', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'contest_type', 'created_at')
    search_fields = ('title', 'description')
    filter_horizontal = ('entry_books', 'entry_scripts', 'entry_poems')

@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'status', 'handpicked', 'created_at')
    list_filter = ('status', 'handpicked', 'genre', 'created_at')
    search_fields = ('title', 'author__username', 'genre')

@admin.register(Poem)
class PoemAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'handpicked', 'created_at')
    list_filter = ('status', 'handpicked', 'created_at')
    search_fields = ('title', 'author__username')


# Register your models here.