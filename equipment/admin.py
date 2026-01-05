from django.contrib import admin
from .models import Brand, Guitar, Amplifier, Pedal, OwnedGear


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "is_unknown"]
    search_fields = ["name"]


@admin.register(Guitar)
class GuitarAdmin(admin.ModelAdmin):
    list_display = ["name", "brand", "guitar_type", "num_strings"]
    list_filter = ["guitar_type", "brand"]
    search_fields = ["name", "brand__name"]


@admin.register(Amplifier)
class AmplifierAdmin(admin.ModelAdmin):
    list_display = ["name", "brand", "amp_type", "wattage"]
    list_filter = ["amp_type"]


@admin.register(Pedal)
class PedalAdmin(admin.ModelAdmin):
    list_display = ["name", "brand", "pedal_type"]
    list_filter = ["pedal_type"]


@admin.register(OwnedGear)
class OwnedGearAdmin(admin.ModelAdmin):
    list_display = ["user", "gear_item", "nickname", "is_favorite"]
    list_filter = ["is_favorite", "user"]
