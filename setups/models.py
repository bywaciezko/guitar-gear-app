from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from equipment.models import OwnedGear


class Genre(models.Model):
    """Musical genres"""

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Band(models.Model):
    """Musical bands/artists"""

    name = models.CharField(max_length=200)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Song(models.Model):
    """Songs"""

    title = models.CharField(max_length=200)
    band = models.ForeignKey(Band, on_delete=models.CASCADE, related_name="songs")

    @property
    def genre(self):
        """Auto-derived from band"""
        return self.band.genre if self.band else None

    def __str__(self):
        return f"{self.band.name} - {self.title}"

    class Meta:
        ordering = ["band__name", "title"]


class Setup(models.Model):
    """
    A complete gear setup with signal chain.
    Example: "My Metallica Tone" using your LP + Marshall + Tubescreamer
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="setups"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Tags for categorization
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    band = models.ForeignKey(Band, on_delete=models.SET_NULL, null=True, blank=True)
    song = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True, blank=True)

    # Visibility
    is_public = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False) # owner's favorite
    saved_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name="saved_setups", 
        blank=True
    )
    # Stats
    views = models.IntegerField(default=0)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_setups", blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self) -> None:
        """
        Check data before saving
        """
        if self.song and self.band:
            if self.song.band != self.band:
                raise ValidationError(
                    {"band": f"incorrect band. Should be '{self.song.band}'"}
                )
        if self.band and self.genre:
            if self.band.genre != self.genre:
                raise ValidationError(
                    {"genre": f"incorrect genre. Should be '{self.band.genre}'"}
                )
        if self.song and self.genre:
            if self.song.genre != self.genre:
                raise ValidationError(
                    {"genre": f"Incorrect genre. Should be '{self.song.genre}'"}
                )

    """Domain Model pattern - auto-tagging logic"""
    def save(self, *args, **kwargs):
        # Auto-tag from song → band → genre
        if self.song:
            self.band = self.song.band
            self.genre = self.song.band.genre
        elif self.band and not self.genre:
            self.genre = self.band.genre

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s {self.name}"

    class Meta:
        ordering = ["-is_favorite", "-created_at"]


class SignalChainItem(models.Model):
    """
    Single item in the signal chain with its settings.
    Example: Tubescreamer pedal with Gain=75, Tone=60, Level=80
    """

    setup = models.ForeignKey(
        Setup, on_delete=models.CASCADE, related_name="signal_chain"
    )
    owned_gear = models.ForeignKey(OwnedGear, on_delete=models.CASCADE)

    order = models.PositiveIntegerField()

    # Value Object pattern - settings for THIS usage
    settings = models.JSONField(default=dict, blank=True)
    # e.g. {"Gain": 75, "Tone": 60, "Level": 80}

    notes = models.TextField(
        blank=True, help_text="Notes about this gear in this setup"
    )

    class Meta:
        ordering = ["order"]
        unique_together = ["setup", "owned_gear"]  # Can't add same gear twice

    def __str__(self):
        return f"{self.owned_gear} in {self.setup.name}"
