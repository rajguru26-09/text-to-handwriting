from django.contrib import admin
from .models import Conversion


@admin.register(Conversion)
class ConversionAdmin(admin.ModelAdmin):
    list_display = ['id', 'language', 'status', 'output_format', 'created_at', 'completed_at']
    list_filter = ['status', 'language', 'output_format', 'page_size']
    search_fields = ['text', 'id']
    readonly_fields = ['id', 'created_at', 'completed_at', 'processing_time', 'output_png', 'output_pdf', 'error_message']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'text', 'language', 'style', 'status', 'error_message')
        }),
        ('Output Settings', {
            'fields': ('output_format', 'output_png', 'output_pdf')
        }),
        ('Page Settings', {
            'fields': ('page_size', 'custom_width', 'custom_height', 'margin_top', 'margin_bottom', 'margin_left', 'margin_right')
        }),
        ('Typography', {
            'fields': ('font_size', 'line_spacing', 'word_spacing', 'char_spacing', 'slant')
        }),
        ('Style Variations', {
            'fields': ('ink_color', 'paper_color', 'line_variance', 'pressure_variance')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at', 'processing_time')
        }),
    )