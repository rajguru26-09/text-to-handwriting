from django import forms
from .models import Conversion, Language, OutputFormat, PageSize


class ConversionForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 8,
            'class': 'form-control',
            'placeholder': 'Enter text to convert to handwriting...',
        }),
        label='Text Content',
    )
    
    language = forms.ChoiceField(
        choices=Language.choices,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_language'}),
        initial=Language.ENGLISH,
    )
    

    output_format = forms.ChoiceField(
        choices=OutputFormat.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial=OutputFormat.BOTH,
    )
    
    page_size = forms.ChoiceField(
        choices=PageSize.choices,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_page_size'}),
        initial=PageSize.A4,
    )
    
    custom_width = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Width in mm',
            'step': '0.1',
            'min': '50',
            'max': '1000',
        }),
        label='Custom Width (mm)',
    )
    
    custom_height = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Height in mm',
            'step': '0.1',
            'min': '50',
            'max': '1000',
        }),
        label='Custom Height (mm)',
    )
    
    margin_top = forms.FloatField(
        initial=20,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'min': '0',
            'max': '100',
        }),
    )
    
    margin_bottom = forms.FloatField(
        initial=20,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'min': '0',
            'max': '100',
        }),
    )
    
    margin_left = forms.FloatField(
        initial=20,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'min': '0',
            'max': '100',
        }),
    )
    
    margin_right = forms.FloatField(
        initial=20,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'min': '0',
            'max': '100',
        }),
    )
    
    line_spacing = forms.FloatField(
        initial=1.5,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'min': '0.5',
            'max': '5.0',
        }),
    )
    
    font_size = forms.FloatField(
        initial=14,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.5',
            'min': '6',
            'max': '72',
        }),
    )
    
    ink_color = forms.CharField(
        initial='#000000',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-color',
            'type': 'color',
        }),
    )
    
    paper_color = forms.CharField(
        initial='#FFFFFF',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-color',
            'type': 'color',
        }),
    )
    
    line_variance = forms.FloatField(
        initial=0.3,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.05',
            'min': '0',
            'max': '1',
        }),
    )
    
    word_spacing = forms.FloatField(
        initial=1.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.05',
            'min': '0.1',
            'max': '3.0',
        }),
    )
    
    char_spacing = forms.FloatField(
        initial=1.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.05',
            'min': '0.1',
            'max': '3.0',
        }),
    )
    
    slant = forms.FloatField(
        initial=0.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.5',
            'min': '-30',
            'max': '30',
        }),
    )
    
    pressure_variance = forms.FloatField(
        initial=0.3,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.05',
            'min': '0',
            'max': '1',
        }),
    )

    class Meta:
        model = Conversion
        fields = [
            'text', 'language', 'output_format', 'page_size',
            'custom_width', 'custom_height', 'margin_top', 'margin_bottom',
            'margin_left', 'margin_right', 'line_spacing', 'font_size',
            'ink_color', 'paper_color', 'line_variance', 'word_spacing',
            'char_spacing', 'slant', 'pressure_variance',
        ]

    def clean(self):
        cleaned_data = super().clean()
        page_size = cleaned_data.get('page_size')
        custom_width = cleaned_data.get('custom_width')
        custom_height = cleaned_data.get('custom_height')
        
        if page_size == PageSize.CUSTOM:
            if not custom_width or not custom_height:
                raise forms.ValidationError(
                    'Custom width and height are required when page size is Custom.'
                )
        
        return cleaned_data


class TextFileUploadForm(ConversionForm):
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.txt,.text',
        }),
        label='Text File (.txt)',
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('text', None)