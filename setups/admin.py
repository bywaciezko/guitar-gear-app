from django.contrib import admin
from .models import Genre, Band, Song, Setup, SignalChainItem

admin.site.register(Genre)
admin.site.register(Band)
admin.site.register(Song)


@admin.register(Setup)
class SetupAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "user",
        "genre",
        "band",
        "is_public",
        "is_favorite",
        "views",
    ]
    list_filter = ["is_public", "is_favorite", "genre"]
    search_fields = ["name", "user__username"]


@admin.register(SignalChainItem)
class SignalChainItemAdmin(admin.ModelAdmin):
    list_display = ["setup", "owned_gear", "order"]
    ordering = ["setup", "order"]
