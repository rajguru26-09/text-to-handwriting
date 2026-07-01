import os
import time
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings
from django.utils import timezone

from .models import Conversion, Language, OutputFormat, PageSize
from .forms import ConversionForm, TextFileUploadForm
from .services.synthesis import HandwritingConfig, create_handwriting_synthesizer
from .tasks import process_conversion_task


synthesizer = None

def get_synthesizer():
    global synthesizer
    if synthesizer is None:
        models_dir = getattr(settings, 'HANDWRITING_MODELS_DIR', '/mnt/d/Openccode/Projects/P1_text_to_handwritten/handwriting_project/models')
        os.makedirs(models_dir, exist_ok=True)
        synthesizer = create_handwriting_synthesizer(models_dir)
    return synthesizer


def index(request):
    if request.method == 'POST':
        form = ConversionForm(request.POST)
        if form.is_valid():
            conversion = form.save(commit=False)
            conversion.status = 'pending'
            conversion.save()
            return redirect('handwriting:process_conversion', conversion_id=conversion.id)
    else:
        form = ConversionForm()
    
    recent_conversions = Conversion.objects.all()[:10]
    
    return render(request, 'index.html', {
        'form': form,
        'recent_conversions': recent_conversions,
    })


def process_conversion(request, conversion_id):
    conversion = get_object_or_404(Conversion, id=conversion_id)
    
    if request.method == 'POST':
        return _process_conversion_async(conversion)
    
    return render(request, 'processing.html', {'conversion': conversion})


import threading
from django.db import connection

def _process_conversion_async(conversion):
    conversion.status = 'pending'
    conversion.save()
    
    def run_task(conv_id):
        try:
            process_conversion_task(conv_id)
        finally:
            connection.close()
            
    threading.Thread(target=run_task, args=(conversion.id,)).start()
    
    return JsonResponse({'status': 'processing', 'redirect_url': f'/result/{conversion.id}/'})


@require_http_methods(['GET'])
def conversion_status(request, conversion_id):
    conversion = get_object_or_404(Conversion, id=conversion_id)
    data = {
        'status': conversion.status,
        'processing_time': conversion.processing_time,
        'error_message': conversion.error_message,
    }
    if conversion.status == 'completed':
        data['redirect_url'] = f'/result/{conversion.id}/'
    return JsonResponse(data)


def conversion_result(request, conversion_id):
    conversion = get_object_or_404(Conversion, id=conversion_id)
    
    png_pages = []
    if conversion.output_png:
        import os
        from django.conf import settings
        base_filename = os.path.basename(conversion.output_png.name)
        
        if '_page_1.png' in base_filename:
            prefix = base_filename.replace('_page_1.png', '')
            i = 1
            while True:
                page_name = f"{prefix}_page_{i}.png"
                page_path = os.path.join(settings.MEDIA_ROOT, 'handwritten', page_name)
                if os.path.exists(page_path):
                    url = f"{settings.MEDIA_URL}handwritten/{page_name}"
                    png_pages.append({'url': url, 'page': i})
                    i += 1
                else:
                    break
        else:
            png_pages.append({'url': conversion.output_png.url, 'page': 1})
    
    pdf_pages = 1
    if conversion.output_pdf:
        pdf_pages = 1
    
    return render(request, 'result.html', {
        'conversion': conversion,
        'png_pages': png_pages,
        'pdf_pages': pdf_pages,
    })


def conversion_list(request):
    conversions = Conversion.objects.all()
    return render(request, 'list.html', {'conversions': conversions})


def download_file(request, conversion_id, file_type):
    conversion = get_object_or_404(Conversion, id=conversion_id)
    
    if file_type == 'png' and conversion.output_png:
        return FileResponse(conversion.output_png.open(), as_attachment=True, filename=f'handwriting_{conversion.id}.png')
    elif file_type == 'pdf' and conversion.output_pdf:
        return FileResponse(conversion.output_pdf.open(), as_attachment=True, filename=f'handwriting_{conversion.id}.pdf')
    
    raise Http404('File not found')


def upload_text_file(request):
    if request.method == 'POST':
        form = TextFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            text_file = request.FILES['file']
            text_content = text_file.read().decode('utf-8')
            
            conversion = form.save(commit=False)
            conversion.text = text_content
            conversion.status = 'pending'
            conversion.save()
            return redirect('handwriting:process_conversion', conversion_id=conversion.id)
    else:
        form = TextFileUploadForm()
    
    return render(request, 'upload.html', {'form': form})




