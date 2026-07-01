from django.db import models
from django.conf import settings
import uuid
import os


class Language(models.TextChoices):
    ENGLISH = 'en', 'English (Latin)'
    HINDI = 'hi', 'Hindi (Devanagari)'
    SANSKRIT = 'sa', 'Sanskrit (Devanagari)'


class OutputFormat(models.TextChoices):
    PNG = 'png', 'PNG'
    PDF = 'pdf', 'PDF'
    BOTH = 'both', 'Both PNG & PDF'


class PageSize(models.TextChoices):
    A4 = 'A4', 'A4 (210 x 297 mm)'
    LETTER = 'LETTER', 'Letter (8.5 x 11 in)'
    A5 = 'A5', 'A5 (148 x 210 mm)'
    CUSTOM = 'CUSTOM', 'Custom'





class Conversion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    language = models.CharField(max_length=2, choices=Language.choices, default=Language.ENGLISH)
    output_format = models.CharField(max_length=4, choices=OutputFormat.choices, default=OutputFormat.BOTH)
    page_size = models.CharField(max_length=10, choices=PageSize.choices, default=PageSize.A4)
    custom_width = models.FloatField(null=True, blank=True, help_text='Custom width in mm')
    custom_height = models.FloatField(null=True, blank=True, help_text='Custom height in mm')
    margin_top = models.FloatField(default=20, help_text='Top margin in mm')
    margin_bottom = models.FloatField(default=20, help_text='Bottom margin in mm')
    margin_left = models.FloatField(default=20, help_text='Left margin in mm')
    margin_right = models.FloatField(default=20, help_text='Right margin in mm')
    line_spacing = models.FloatField(default=1.5, help_text='Line spacing multiplier')
    font_size = models.FloatField(default=14, help_text='Font size in pt')
    ink_color = models.CharField(max_length=7, default='#000000', help_text='Hex color code')
    paper_color = models.CharField(max_length=7, default='#FFFFFF', help_text='Hex color code')
    line_variance = models.FloatField(default=0.3, help_text='Line position variance (0-1)')
    word_spacing = models.FloatField(default=1.0, help_text='Word spacing multiplier')
    char_spacing = models.FloatField(default=1.0, help_text='Character spacing multiplier')
    slant = models.FloatField(default=0.0, help_text='Slant angle in degrees')
    pressure_variance = models.FloatField(default=0.3, help_text='Pressure variance (0-1)')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    output_png = models.FileField(upload_to='handwritten/', null=True, blank=True)
    output_pdf = models.FileField(upload_to='handwritten/', null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True, help_text='Processing time in seconds')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.language} - {self.text[:50]}..."

    def get_page_size_mm(self):
        sizes = {
            PageSize.A4: (210, 297),
            PageSize.LETTER: (215.9, 279.4),
            PageSize.A5: (148, 210),
        }
        if self.page_size == PageSize.CUSTOM and self.custom_width and self.custom_height:
            return (self.custom_width, self.custom_height)
        return sizes.get(self.page_size, (210, 297))