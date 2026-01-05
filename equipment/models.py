from django.db import models
from django.conf import settings


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # Special Case pattern (Unknown for custom gear)
    is_unknown = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

    @classmethod
    def get_unknown_brand(cls):
        """Returns 'Unknown' brand for custom gear"""
        brand, _ = cls.objects.get_or_create(
            name="Unknown", defaults={"is_unknown": True}
        )
        return brand


class Gear(models.Model):
    """Base class for all gear (Abstract base class)"""

    name = models.CharField(max_length=200)
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name="%(class)s_set"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # Doesn't create a table for gear

    def __str__(self):
        return f"{self.brand.name} {self.name}"


# Single Table Inheritance pattern
class Guitar(Gear):
    GUITAR_TYPE_CHOICES = [
        ("STRAT", "Stratocaster"),
        ("TELE", "Telecaster"),
        ("LES_PAUL", "Les Paul"),
        ("SG", "SG"),
        ("OTHER", "Other"),
    ]

    guitar_type = models.CharField(choices=GUITAR_TYPE_CHOICES, max_length=20)
    num_strings = models.IntegerField(default=6)
    pickup_config = models.CharField(max_length=20, blank=True)  # SSS, HSH, etc.


# Single Table Inheritance pattern
class Amplifier(Gear):
    AMP_TYPE_CHOICES = [
        ("TUBE", "Tube"),
        ("SOLID_STATE", "Solid State"),
        ("MODELING", "Modeling"),
        ("HYBRID", "Hybrid"),
    ]

    amp_type = models.CharField(choices=AMP_TYPE_CHOICES, max_length=20)
    wattage = models.IntegerField(help_text="Power in watts")
    has_effects_loop = models.BooleanField(default=False)

    # Value Object pattern
    available_controls = models.JSONField(default=list, blank=True)
    # e.g. ["Gain", "Bass", "Mid", "Treble", "Presence", "Master"]


# Single Table Inheritance pattern
class Pedal(Gear):
    PEDAL_TYPE_CHOICES = [
        ("DISTORTION", "Distortion"),
        ("OVERDRIVE", "Overdrive"),
        ("FUZZ", "Fuzz"),
        ("DELAY", "Delay"),
        ("REVERB", "Reverb"),
        ("CHORUS", "Chorus"),
        ("OTHER", "Other"),
    ]

    pedal_type = models.CharField(choices=PEDAL_TYPE_CHOICES, max_length=20)

    # Value Object pattern
    available_controls = models.JSONField(default=list, blank=True)
    # e.g. ["Gain", "Tone", "Level"]

    # Value Object pattern
    default_settings = models.JSONField(default=dict, blank=True)
    # e.g. {"Gain": 50, "Tone": 70, "Level": 80}


# Association Table pattern
class OwnedGear(models.Model):
    """User's owned gear"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_gear"
    )

    guitar = models.ForeignKey(Guitar, on_delete=models.PROTECT, null=True, blank=True)
    amplifier = models.ForeignKey(
        Amplifier, on_delete=models.PROTECT, null=True, blank=True
    )
    pedal = models.ForeignKey(Pedal, on_delete=models.PROTECT, null=True, blank=True)

    nickname = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    is_favorite = models.BooleanField(default=False)

    acquired_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.nickname:
            return self.nickname
        # Return whichever gear is set
        gear = self.guitar or self.amplifier or self.pedal
        return str(gear) if gear else "Unnamed Gear"

    @property
    def gear_item(self):
        """Returns the actual gear object"""
        return self.guitar or self.amplifier or self.pedal

    class Meta:
        ordering = ["-is_favorite", "-created_at"]
