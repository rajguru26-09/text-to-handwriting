import argparse
import textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def render_handwriting(
    text_file: str,
    font_path: str,
    output_prefix: str,
    page_width_mm: float = 210,
    page_height_mm: float = 297,
    margin_mm: float = 20,
    font_size_pt: float = 14,
    line_spacing: float = 1.5,
    ink_color: str = "#000000",
    paper_color: str = "#FFFFFF",
    line_variance: float = 0.3
):
    print(f"Reading text from {text_file}...")
    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Convert mm to pixels (assuming ~96 DPI, so 1mm ~ 3.78px)
    width_px = int(page_width_mm * 3.78)
    height_px = int(page_height_mm * 3.78)
    margin_px = int(margin_mm * 3.78)
    
    usable_width = width_px - (2 * margin_px)
    font_size_px = int(font_size_pt * 1.33)
    
    print(f"Loading font {font_path}...")
    try:
        font = ImageFont.truetype(font_path, font_size_px)
    except Exception as e:
        print(f"Error loading font: {e}")
        return

    # Estimate average character width for wrapping
    avg_char_width = font_size_px * 0.5
    chars_per_line = int(usable_width / avg_char_width)
    
    paragraphs = text.split('\n')
    lines = []
    for p in paragraphs:
        if p.strip() == '':
            lines.append('')
        else:
            wrapped = textwrap.wrap(p, width=chars_per_line)
            lines.extend(wrapped)

    line_height = int(font_size_px * line_spacing)
    usable_height = height_px - (2 * margin_px)
    lines_per_page = int(usable_height / line_height)

    pages = []
    current_page = []
    for line in lines:
        current_page.append(line)
        if len(current_page) >= lines_per_page:
            pages.append(current_page)
            current_page = []
    if current_page:
        pages.append(current_page)

    images = []
    for page_idx, page_lines in enumerate(pages):
        print(f"Rendering page {page_idx + 1}/{len(pages)}...")
        img = Image.new('RGB', (width_px, height_px), paper_color)
        draw = ImageDraw.Draw(img)
        
        y = margin_px
        for i, line in enumerate(page_lines):
            # Apply slight line variance for realism
            y_offset = y + int(np.random.normal(0, line_variance * 3))
            draw.text((margin_px, y_offset), line, fill=ink_color, font=font)
            y += line_height
            
        images.append(img)
        
    print(f"Saving outputs...")
    # Save as PNG
    for i, img in enumerate(images):
        png_path = f"{output_prefix}_page_{i+1}.png"
        img.save(png_path, "PNG")
        print(f"Saved {png_path}")
        
    # Save as PDF
    pdf_path = f"{output_prefix}.pdf"
    if len(images) > 0:
        images[0].save(
            pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
        )
        print(f"Saved {pdf_path}")
    
    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate handwriting using a custom .ttf font")
    parser.add_argument("text_file", help="Path to the input text file")
    parser.add_argument("font_file", help="Path to the custom .ttf font file")
    parser.add_argument("--output", "-o", default="custom_handwriting", help="Prefix for output files (default: custom_handwriting)")
    parser.add_argument("--font-size", type=float, default=16, help="Font size in pt")
    parser.add_argument("--line-variance", type=float, default=0.5, help="Variance of the line to simulate messy handwriting")
    
    args = parser.parse_args()
    
    render_handwriting(
        text_file=args.text_file,
        font_path=args.font_file,
        output_prefix=args.output,
        font_size_pt=args.font_size,
        line_variance=args.line_variance
    )
