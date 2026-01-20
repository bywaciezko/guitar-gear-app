from django import forms
from equipment.models import OwnedGear
from setups.models import Setup, SignalChainItem


class SetupForm(forms.ModelForm):
    class Meta:
        model = Setup
        fields = ['name', 'description', 'genre', 'band', 'song', 'is_public']
        
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'placeholder': 'Describe the tone (e.g., "Crunchy rhythm for 80s rock")'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., "My Metallica Tone"'
            }),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'band': forms.Select(attrs={'class': 'form-select'}),
            'song': forms.Select(attrs={'class': 'form-select'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        labels = {
            'is_public': 'Make Public?',
            'band': 'Artist / Band (Optional)',
        }
        
        help_texts = {
            'is_public': 'Public setups can be seen by other users in Community.',
            'song': 'Selecting a song auto-fills band and genre',
        }


class AddGearToSetupForm(forms.ModelForm):
    class Meta:
        model = SignalChainItem
        fields = ['owned_gear', 'order', 'notes', 'settings']
        
        widgets = {
            'owned_gear': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto',
                'min': 0
            }),
            'settings': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2, 
                'placeholder': '{"Gain": 75, "Tone": 60, "Level": 80}'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'e.g., "Bridge pickup, high gain"'
            }),
        }
        
        labels = {
            'owned_gear': 'Select Gear from Your Collection',
            'order': 'Position in Chain',
            'settings': 'Knob Settings (JSON)',
            'notes': 'Notes',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter to user's gear only
            self.fields['owned_gear'].queryset = OwnedGear.objects.filter(
                user=user
            ).select_related(
                'guitar', 'guitar__brand',
                'amplifier', 'amplifier__brand',
                'pedal', 'pedal__brand'
            )
            
            # Custom label showing brand + name + nickname
            self.fields['owned_gear'].label_from_instance = lambda obj: (
                f"{obj.gear_item.brand.name} {obj.gear_item.name}"
                f"{' (' + obj.nickname + ')' if obj.nickname else ''}"
            )
        
        # Order is optional
        self.fields['order'].required = False
