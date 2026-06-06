from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.conf import settings
from pathlib import Path
import os
import mimetypes


def serve_frontend_file(request, file_path=''):
    frontend_dir = Path(__file__).resolve().parent.parent / 'frontend'
    requested_path = frontend_dir / file_path if file_path else frontend_dir / 'index.html'
    
    # If no file specified, serve index.html
    if not file_path or file_path == '':
        requested_path = frontend_dir / 'index.html'
    
    # Check if the requested file exists
    if requested_path.exists() and requested_path.is_file():
        # Determine content type
        content_type, encoding = mimetypes.guess_type(str(requested_path))
        
        # Serve HTML files
        if content_type and 'text/html' in content_type:
            with open(requested_path, 'r', encoding='utf-8') as f:
                return HttpResponse(f.read(), content_type='text/html')
        # Serve CSS files
        elif content_type and 'text/css' in content_type:
            with open(requested_path, 'r', encoding='utf-8') as f:
                return HttpResponse(f.read(), content_type='text/css')
        # Serve JS files
        elif content_type and 'javascript' in content_type:
            with open(requested_path, 'r', encoding='utf-8') as f:
                return HttpResponse(f.read(), content_type='application/javascript')
        # Serve other files (images, etc.)
        else:
            return FileResponse(open(requested_path, 'rb'), content_type=content_type or 'application/octet-stream')
    
    # If file not found, try to serve as HTML with .html extension
    if not requested_path.suffix:
        html_path = requested_path.with_suffix('.html')
        if html_path.exists():
            with open(html_path, 'r', encoding='utf-8') as f:
                return HttpResponse(f.read(), content_type='text/html')
    
    return HttpResponse(f"File not found: {file_path}", status=404)
