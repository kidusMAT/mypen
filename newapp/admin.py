from django.contrib import admin
from django import forms

from .models import AuthorProfile, Book, Chapter, Contest, ContestParticipant, Script, Poem

admin.site.register(AuthorProfile)
admin.site.register(Book)
admin.site.register(Chapter)

class ContestAdminForm(forms.ModelForm):
    class Meta:
        model = Contest
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing an existing contest, filter winner choices to only show participants
        if self.instance and self.instance.pk:
            participant_users = self.instance.participants.values_list('user', flat=True)
            self.fields['winner'].queryset = self.fields['winner'].queryset.filter(id__in=participant_users)

@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    form = ContestAdminForm
    list_display = ('title', 'contest_type', 'status', 'participant_count', 'start_date', 'end_date', 'winner')
    list_filter = ('status', 'contest_type', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('participant_count', 'created_at')

@admin.register(ContestParticipant)
class ContestParticipantAdmin(admin.ModelAdmin):
    list_display = ('contest', 'user', 'entry_type', 'joined_at')
    list_filter = ('contest', 'entry_type', 'joined_at')
    search_fields = ('user__username', 'contest__title')
    readonly_fields = ('joined_at',)

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