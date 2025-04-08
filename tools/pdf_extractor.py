#!/usr/bin/env python3
"""
PDF Text Extractor for Resume Processing

This script extracts text from PDF files for resume processing.
It handles different PDF formats and attempts to maintain document structure.

Usage:
    python pdf_extractor.py resume.pdf
"""

import os
import sys
import traceback
from typing import List, Optional

import PyPDF2
from pdfminer.high_level import extract_text as pdfminer_extract_text

def extract_text_with_pypdf2(pdf_path: str) -> str:
    """
    Extract text from PDF using PyPDF2.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text
    """
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
    except Exception as e:
        print(f"Error extracting text with PyPDF2: {str(e)}", file=sys.stderr)
    
    return text

def extract_text_with_pdfminer(pdf_path: str) -> str:
    """
    Extract text from PDF using pdfminer.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text
    """
    try:
        return pdfminer_extract_text(pdf_path)
    except Exception as e:
        print(f"Error extracting text with pdfminer: {str(e)}", file=sys.stderr)
        return ""

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF using multiple methods for better results.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text
    """
    # Try PyPDF2 first
    text = extract_text_with_pypdf2(pdf_path)
    
    # If PyPDF2 failed or returned very little text, try pdfminer
    if not text or len(text.strip()) < 100:
        text = extract_text_with_pdfminer(pdf_path)
    
    # Clean up the text
    text = clean_text(text)
    
    return text

def clean_text(text: str) -> str:
    """
    Clean extracted text to improve quality and readability.
    
    Args:
        text: Extracted text from PDF
        
    Returns:
        Cleaned text
    """
    # Replace multiple newlines with a single newline
    import re
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove odd characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    # Fix common PDF extraction issues
    text = text.replace('•', '- ')  # Replace bullets with dashes
    
    return text

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide PDF file path", file=sys.stderr)
        sys.exit(1)
        
    pdf_file = sys.argv[1]
    if not os.path.exists(pdf_file):
        print(f"File not found: {pdf_file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        text = extract_text_from_pdf(pdf_file)
        print(text)
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1) 