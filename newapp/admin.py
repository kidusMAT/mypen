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
    list_display = ('title', 'contest_type', 'status', 'participant_count', 'start_date', 'end_date', 'winner', 'winner_phone')
    list_filter = ('status', 'contest_type', 'created_at')
    search_fields = ('title', 'description', 'winner__username')
    readonly_fields = ('participant_count', 'created_at', 'winner_phone')

    def winner_phone(self, obj):
        if obj.winner:
            return getattr(getattr(obj.winner, 'authorprofile', None), 'phone_number', None) or '-'
        return '-'
    winner_phone.short_description = 'Winner Phone'

@admin.register(ContestParticipant)
class ContestParticipantAdmin(admin.ModelAdmin):
    list_display = ('contest', 'user', 'user_phone', 'user_email', 'entry_type', 'joined_at')
    list_filter = ('contest', 'entry_type', 'joined_at')
    search_fields = ('user__username', 'contest__title', 'user__authorprofile__phone_number')
    readonly_fields = ('joined_at',)

    def user_phone(self, obj):
        return getattr(getattr(obj.user, 'authorprofile', None), 'phone_number', None) or '-'
    user_phone.short_description = 'Phone Number'

    def user_email(self, obj):
        return obj.user.email or '-'
    user_email.short_description = 'Email' 

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