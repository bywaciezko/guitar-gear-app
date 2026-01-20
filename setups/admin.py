from django.contrib import admin
from .models import Setup, SignalChainItem, Genre, Band, Song


class SignalChainItemInline(admin.TabularInline):
    model = SignalChainItem
    extra = 1
    autocomplete_fields = ["owned_gear"]


@admin.register(Setup)
class SetupAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "genre", "is_public", "is_favorite", "created_at"]
    list_filter = ["genre", "is_public", "created_at"]
    search_fields = ["name", "user__username", "description"]

    # effects table
    inlines = [SignalChainItemInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Band)
class BandAdmin(admin.ModelAdmin):
    list_display = ["name", "genre"]
    list_filter = ["genre"]


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ["title", "band", "genre"]
    search_fields = ["title", "band__name"]
