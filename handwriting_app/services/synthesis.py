import os
import torch
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, LETTER, A5
from reportlab.lib.units import mm
import tempfile
import time
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class HandwritingConfig:
    language: str
    page_width_mm: float
    page_height_mm: float
    margin_top_mm: float
    margin_bottom_mm: float
    margin_left_mm: float
    margin_right_mm: float
    line_spacing: float
    font_size_pt: float
    ink_color: str
    paper_color: str
    line_variance: float
    word_spacing: float
    char_spacing: float
    slant_deg: float
    pressure_variance: float
    page_size: str = 'A4'
    custom_width_mm: float = None
    custom_height_mm: float = None


class HandwritingSynthesizer:
    def __init__(self, models_dir: str):
        self.models_dir = models_dir
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.models = {}
        self._load_models()

    def _load_models(self):
        model_configs = {
            'en_casual': {'type': 'rnn', 'alphabet': 'latin', 'style': 'casual'},
            'en_formal': {'type': 'rnn', 'alphabet': 'latin', 'style': 'formal'},
            'en_cursive': {'type': 'rnn', 'alphabet': 'latin', 'style': 'cursive'},
            'hi_devanagari': {'type': 'rnn', 'alphabet': 'devanagari', 'style': 'standard'},
            'hi_cursive': {'type': 'rnn', 'alphabet': 'devanagari', 'style': 'cursive'},
            'sa_devanagari': {'type': 'rnn', 'alphabet': 'devanagari', 'style': 'standard'},
            'sa_vedic': {'type': 'rnn', 'alphabet': 'devanagari', 'style': 'vedic'},
        }
        
        for style, config in model_configs.items():
            model_path = os.path.join(self.models_dir, f'{style}.pt')
            if os.path.exists(model_path):
                self.models[style] = self._load_model(model_path, config)
            else:
                self.models[style] = self._create_fallback_model(config)

    def _load_model(self, path: str, config: dict):
        try:
            model = torch.load(path, map_location=self.device, weights_only=False)
            model.eval()
            return model
        except Exception:
            return self._create_fallback_model(config)

    def _create_fallback_model(self, config: dict):
        return {'config': config, 'type': 'fallback'}

    def synthesize(self, text: str, config: HandwritingConfig) -> List[Image.Image]:
        return self._synthesize_fallback(text, config)

    def _synthesize_with_model(self, text: str, config: HandwritingConfig, model: dict) -> List[Image.Image]:
        lines = self._wrap_text(text, config)
        pages = self._layout_pages(lines, config)
        images = []
        
        for page_lines in pages:
            img = self._render_page_with_model(page_lines, config, model)
            images.append(img)
        
        return images

    def _synthesize_fallback(self, text: str, config: HandwritingConfig) -> List[Image.Image]:
        lines = self._wrap_text(text, config)
        pages = self._layout_pages(lines, config)
        images = []
        
        for page_lines in pages:
            img = self._render_page_fallback(page_lines, config)
            images.append(img)
        
        return images

    def _wrap_text(self, text: str, config: HandwritingConfig) -> List[str]:
        max_width_px = (config.page_width_mm - config.margin_left_mm - config.margin_right_mm) * 3.78
        font_size_px = config.font_size_pt * 1.33
        
        paragraphs = text.split('\n')
        lines = []
        
        for p in paragraphs:
            # Preserve empty lines
            if not p.strip():
                lines.append('')
                continue
                
            words = [w for w in p.split(' ') if w]
            current_line = []
            current_width = 0
            
            for word in words:
                word_width = len(word) * font_size_px * 0.6 * config.char_spacing
                space_width = font_size_px * 0.3 * config.word_spacing
                
                if current_width + word_width > max_width_px and current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_width = word_width
                else:
                    if current_line:
                        current_width += space_width
                    current_line.append(word)
                    current_width += word_width
            
            if current_line:
                lines.append(' '.join(current_line))
                
        return lines

    def _layout_pages(self, lines: List[str], config: HandwritingConfig) -> List[List[str]]:
        line_height_mm = config.font_size_pt * 0.353 * config.line_spacing
        available_height_mm = config.page_height_mm - config.margin_top_mm - config.margin_bottom_mm
        lines_per_page = max(1, int(available_height_mm / line_height_mm))
        
        pages = []
        for i in range(0, len(lines), lines_per_page):
            pages.append(lines[i:i + lines_per_page])
        
        return pages

    def _render_page_with_model(self, lines: List[str], config: HandwritingConfig, model: dict) -> Image.Image:
        width_px = int(config.page_width_mm * 3.78)
        height_px = int(config.page_height_mm * 3.78)
        
        img = Image.new('RGB', (width_px, height_px), config.paper_color)
        draw = ImageDraw.Draw(img)
        
        y_start = int(config.margin_top_mm * 3.78)
        x_start = int(config.margin_left_mm * 3.78)
        line_height = int(config.font_size_pt * 1.33 * config.line_spacing)
        
        for i, line in enumerate(lines):
            y = y_start + i * line_height
            y += int(np.random.normal(0, config.line_variance * 5))
            
            self._draw_handwritten_line(draw, line, x_start, y, config)
        
        return img

    def _render_page_fallback(self, lines: List[str], config: HandwritingConfig) -> Image.Image:
        width_px = int(config.page_width_mm * 3.78)
        height_px = int(config.page_height_mm * 3.78)
        
        img = Image.new('RGB', (width_px, height_px), config.paper_color)
        draw = ImageDraw.Draw(img)
        
        font_path = self._get_font_path(config.language)
        try:
            font = ImageFont.truetype(font_path, int(config.font_size_pt * 1.33))
        except:
            font = ImageFont.load_default()
        
        y_start = int(config.margin_top_mm * 3.78)
        x_start = int(config.margin_left_mm * 3.78)
        line_height = int(config.font_size_pt * 1.33 * config.line_spacing)
        
        for i, line in enumerate(lines):
            y = y_start + i * line_height
            y += int(np.random.normal(0, config.line_variance * 3))
            
            draw.text((x_start, y), line, fill=config.ink_color, font=font)
        
        return img

    def _draw_handwritten_line(self, draw: ImageDraw.Draw, text: str, x: int, y: int, config: HandwritingConfig):
        font_path = self._get_font_path(config.language)
        try:
            font = ImageFont.truetype(font_path, int(config.font_size_pt * 1.33))
        except:
            font = ImageFont.load_default()
        
        x_pos = x
        for char in text:
            char_x = x_pos + int(np.random.normal(0, config.char_spacing * 2))
            char_y = y + int(np.random.normal(0, config.line_variance * 3))
            
            color = self._vary_color(config.ink_color, config.pressure_variance)
            draw.text((char_x, char_y), char, fill=color, font=font)
            
            bbox = draw.textbbox((0, 0), char, font=font)
            char_width = bbox[2] - bbox[0]
            x_pos += int(char_width * config.char_spacing)
            
            if char == ' ':
                x_pos += int(config.font_size_pt * 1.33 * 0.3 * config.word_spacing)

    def _vary_color(self, base_color: str, variance: float) -> str:
        r = int(base_color[1:3], 16)
        g = int(base_color[3:5], 16)
        b = int(base_color[5:7], 16)
        
        factor = 1.0 + np.random.normal(0, variance * 0.3)
        r = int(max(0, min(255, r * factor)))
        g = int(max(0, min(255, g * factor)))
        b = int(max(0, min(255, b * factor)))
        
        return f'#{r:02x}{g:02x}{b:02x}'

    def _get_font_path(self, language: str) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        local_fonts_dir = os.path.join(base_dir, 'fonts')
        
        font_dirs = [
            local_fonts_dir,
            '/usr/share/fonts/truetype/',
            '/usr/share/fonts/',
            '/System/Library/Fonts/',
            'C:/Windows/Fonts/',
        ]
        
        font_map = {
            'en': ['DancingScript-VariableFont_wght.ttf', 'DejaVuSans.ttf', 'Arial.ttf', 'LiberationSans-Regular.ttf'],
            'hi': ['Hindi/Kalam-Regular.ttf', 'NotoSansDevanagari-Regular.ttf', 'Lohit-Devanagari.ttf', 'DejaVuSans.ttf'],
            'sa': ['Sanskrit/PlaypenSansDeva-VariableFont_wght.ttf', 'NotoSansDevanagari-Regular.ttf', 'Lohit-Devanagari.ttf', 'DejaVuSans.ttf'],
        }
        
        for font_dir in font_dirs:
            for font_name in font_map.get(language, font_map['en']):
                path = os.path.join(font_dir, font_name)
                if os.path.exists(path):
                    return path
        
        return ''

    def save_as_pdf(self, images: List[Image.Image], output_path: str, config: HandwritingConfig):
        page_sizes = {
            'A4': A4,
            'LETTER': LETTER,
            'A5': A5,
        }
        page_size = page_sizes.get(config.page_size, A4)
        
        if config.page_size == 'CUSTOM' and config.custom_width_mm and config.custom_height_mm:
            page_size = (config.custom_width_mm * mm, config.custom_height_mm * mm)
        
        c = canvas.Canvas(output_path, pagesize=page_size)
        
        for img in images:
            img_width, img_height = img.size
            img_aspect = img_width / img_height
            page_width, page_height = page_size
            page_aspect = page_width / page_height
            
            if img_aspect > page_aspect:
                draw_width = page_width
                draw_height = page_width / img_aspect
            else:
                draw_height = page_height
                draw_width = page_height * img_aspect
            
            x = (page_width - draw_width) / 2
            y = (page_height - draw_height) / 2
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_name = tmp.name
            img.save(tmp_name, 'PNG')
            c.drawImage(tmp_name, x, y, draw_width, draw_height)
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            
            c.showPage()
        
        c.save()


def create_handwriting_synthesizer(models_dir: str) -> HandwritingSynthesizer:
    return HandwritingSynthesizer(models_dir)