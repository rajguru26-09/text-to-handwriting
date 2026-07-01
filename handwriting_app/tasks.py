import os
import time
from PIL import Image
from django.conf import settings
from django.utils import timezone
from .models import Conversion, OutputFormat
from .services.synthesis import HandwritingConfig, create_handwriting_synthesizer

def process_conversion_task(conversion_id):
    conversion = Conversion.objects.get(id=conversion_id)
    conversion.status = 'processing'
    conversion.save()
    
    try:
        start_time = time.time()
        
        page_width, page_height = conversion.get_page_size_mm()
        config = HandwritingConfig(
            language=conversion.language,
            page_width_mm=page_width,
            page_height_mm=page_height,
            margin_top_mm=conversion.margin_top,
            margin_bottom_mm=conversion.margin_bottom,
            margin_left_mm=conversion.margin_left,
            margin_right_mm=conversion.margin_right,
            line_spacing=conversion.line_spacing,
            font_size_pt=conversion.font_size,
            ink_color=conversion.ink_color,
            paper_color=conversion.paper_color,
            line_variance=conversion.line_variance,
            word_spacing=conversion.word_spacing,
            char_spacing=conversion.char_spacing,
            slant_deg=conversion.slant,
            pressure_variance=conversion.pressure_variance,
            page_size=conversion.page_size,
            custom_width_mm=conversion.custom_width,
            custom_height_mm=conversion.custom_height,
        )
        
        models_dir = getattr(settings, 'HANDWRITING_MODELS_DIR', os.path.join(settings.BASE_DIR, 'models'))
        synth = create_handwriting_synthesizer(models_dir)
        images = synth.synthesize(conversion.text, config)
        
        output_dir = getattr(settings, 'HANDWRITING_OUTPUT_DIR', settings.MEDIA_ROOT / 'handwritten')
        os.makedirs(output_dir, exist_ok=True)
        
        base_filename = f'{conversion.id}_{int(time.time())}'
        
        if conversion.output_format in [OutputFormat.PNG, OutputFormat.BOTH]:
            if len(images) == 1:
                filename = f'{base_filename}.png'
                filepath = os.path.join(output_dir, filename)
                images[0].save(filepath, 'PNG')
                png_path = filepath
            else:
                for i, img in enumerate(images):
                    page_filename = f'{base_filename}_page_{i+1}.png'
                    page_filepath = os.path.join(output_dir, page_filename)
                    img.save(page_filepath, 'PNG')
                # Point output_png to the first page for the preview
                png_path = os.path.join(output_dir, f'{base_filename}_page_1.png')
                
            conversion.output_png = os.path.relpath(png_path, settings.MEDIA_ROOT).replace('\\', '/')
        
        if conversion.output_format in [OutputFormat.PDF, OutputFormat.BOTH]:
            filename = f'{base_filename}.pdf'
            filepath = os.path.join(output_dir, filename)
            synth.save_as_pdf(images, filepath, config)
            conversion.output_pdf = os.path.relpath(filepath, settings.MEDIA_ROOT).replace('\\', '/')
        
        conversion.status = 'completed'
        conversion.completed_at = timezone.now()
        conversion.processing_time = time.time() - start_time
        conversion.save()
        
    except Exception as e:
        conversion.status = 'failed'
        conversion.error_message = str(e)
        conversion.save()
