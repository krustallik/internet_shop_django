from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    fields = ('avatar','bio','birth_date','location','website','created_at','updated_at')
    readonly_fields = ('created_at','updated_at')
    extra = 0
    classes = ('collapse',)

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username','email','get_location','is_staff','is_active','date_joined')
    search_fields = ('username','email','profile__location')
    def get_location(self, obj):
        return getattr(obj.profile, 'location', '')
    get_location.short_description = 'Місто'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','location','birth_date','has_avatar','created_at')
    list_filter = ('created_at','updated_at')
    search_fields = ('user__username','user__email','location','bio')
    fieldsets = (
        ('Користувач', {'fields': ('user',)}),
        ('Основна інформація', {'fields': ('avatar','bio','birth_date','location','website')}),
        ('Системна інформація', {'fields': ('created_at','updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at','updated_at')
    def has_avatar(self, obj): return bool(obj.avatar)
    has_avatar.boolean = True
    has_avatar.short_description = 'Аватар'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
