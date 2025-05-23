#!/usr/bin/env python3
"""
Industrial-grade Markdown to PDF converter with enhanced features:
- Robust error handling
- Configuration management
- Advanced styling options
- PDF metadata support
- Performance optimizations
- Comprehensive logging
- Input validation
- Dependency checks
"""

import markdown
import pdfkit
import logging
import sys
import os
import argparse
import tempfile
import shutil
import time
from typing import Optional, Dict, Any
from pathlib import Path
import yaml  # pyyaml package

# Configure logging before other imports to catch all events
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
DEFAULT_CONFIG = {
    'pdf_options': {
        'page-size': 'A4',
        'margin-top': '20mm',
        'margin-right': '20mm',
        'margin-bottom': '20mm',
        'margin-left': '20mm',
        'encoding': 'UTF-8',
        'quiet': ''
    },
    'css_styles': {
        'base': """
            body {
                font-family: 'Arial', sans-serif;
                line-height: 1.6;
                color: #333;
                font-size: 11pt;
            }
            h1 { font-size: 24pt; color: #000; }
            h2 { font-size: 18pt; color: #222; }
            h3 { font-size: 14pt; color: #444; }
            p { margin: 0 0 10px 0; }
            ul, ol { margin: 0 0 10px 20px; padding: 0; }
            li { margin: 0 0 5px 0; }
            a { color: #0066cc; text-decoration: none; }
            code { font-family: 'Courier New', monospace; background: #f5f5f5; padding: 2px 4px; }
            pre { background: #f5f5f5; padding: 10px; border-radius: 3px; overflow: auto; }
            blockquote { border-left: 4px solid #ddd; padding-left: 15px; color: #666; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        """,
        'header': """
            header { padding-bottom: 10mm; border-bottom: 1px solid #eee; margin-bottom: 10mm; }
        """,
        'footer': """
            footer { 
                position: fixed; 
                bottom: 0; 
                left: 0; 
                right: 0; 
                height: 10mm; 
                text-align: center; 
                font-size: 8pt; 
                color: #666;
                border-top: 1px solid #eee;
            }
        """
    },
    'metadata': {
        'creator': 'Markdown to PDF Converter',
        'producer': 'Python pdfkit/wkhtmltopdf'
    }
}

class ConversionError(Exception):
    """Base exception for conversion-related errors."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class ConfigurationError(ConversionError):
    """Exception for configuration-related issues."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class DependencyError(ConversionError):
    """Exception for missing dependencies."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class InputValidationError(ConversionError):
    """Exception for input validation failures."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class MarkdownToPDFConverter:
    """
    Industrial-grade Markdown to PDF converter with enhanced features.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the converter with optional configuration.
        
        :param config_path: Path to a YAML configuration file
        """
        self.config = self._load_config(config_path)
        self._validate_dependencies()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults.
        
        :param config_path: Path to YAML config file
        :return: Configuration dictionary
        """
        config = DEFAULT_CONFIG.copy()
        
        if config_path:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
                    config = self._deep_merge(config, user_config)
            except Exception as e:
                raise ConfigurationError(f"Failed to load config file: {str(e)}")
                
        return config
    
    @staticmethod
    def _deep_merge(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        :param base: Base dictionary
        :param update: Dictionary with updates
        :return: Merged dictionary
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = MarkdownToPDFConverter._deep_merge(base[key], value)
            else:
                base[key] = value
        return base
    
    def _validate_dependencies(self):
        """
        Validate that required dependencies are installed and available.
        """
        try:
            # Check if pdfkit can find wkhtmltopdf
            pdfkit.from_string('<html></html>', '/dev/null' if os.name == 'posix' else 'nul')
        except OSError as e:
            raise DependencyError(
                "wkhtmltopdf not found. Please install it and ensure it's in your PATH.\n"
                "On Ubuntu/Debian: sudo apt-get install wkhtmltopdf\n"
                "On macOS: brew install wkhtmltopdf\n"
                "Windows: Download from https://wkhtmltopdf.org/"
            )
    
    def _validate_inputs(self, markdown_file: str, output_pdf: str):
        """
        Validate input and output file paths.
        
        :param markdown_file: Path to input Markdown file
        :param output_pdf: Path to output PDF file
        """
        if not os.path.isfile(markdown_file):
            raise InputValidationError(f"Input file does not exist: {markdown_file}")
            
        output_dir = os.path.dirname(output_pdf) or '.'
        if not os.path.isdir(output_dir):
            raise InputValidationError(f"Output directory does not exist: {output_dir}")
            
        if not markdown_file.lower().endswith(('.md', '.markdown')):
            logger.warning(f"Input file '{markdown_file}' does not have a standard Markdown extension")
    
    def _read_markdown(self, markdown_file: str) -> str:
        """
        Read Markdown content from file with error handling.
        
        :param markdown_file: Path to Markdown file
        :return: File content as string
        """
        try:
            with open(markdown_file, 'r', encoding='utf-8') as f:
                logger.info(f"Reading Markdown file: {markdown_file}")
                return f.read()
        except UnicodeDecodeError:
            # Try with different encodings if UTF-8 fails
            try:
                with open(markdown_file, 'r', encoding='latin-1') as f:
                    logger.warning(f"Read with UTF-8 failed, falling back to latin-1 for {markdown_file}")
                    return f.read()
            except Exception as e:
                raise ConversionError(f"Failed to read file '{markdown_file}': {str(e)}")
        except Exception as e:
            raise ConversionError(f"Failed to read file '{markdown_file}': {str(e)}")
    
    def _convert_to_html(self, markdown_text: str) -> str:
        """
        Convert Markdown text to HTML with extensions for better formatting.
        
        :param markdown_text: Markdown content
        :return: HTML content
        """
        extensions = [
            'extra',  # Adds support for tables, footnotes, etc.
            'codehilite',  # Syntax highlighting
            'toc',  # Table of contents
            'meta',  # Document metadata
            'admonition',  # Notes/warnings
            'sane_lists',  # Better list handling
            'smarty',  # Smart quotes/dashes
            'wikilinks'  # Wiki-style links
        ]
        
        try:
            logger.info("Converting Markdown to HTML")
            return markdown.markdown(markdown_text, extensions=extensions, output_format='html5')
        except Exception as e:
            raise ConversionError(f"Markdown to HTML conversion failed: {str(e)}")
    
    def _generate_html_document(self, html_content: str, title: Optional[str] = None) -> str:
        """
        Generate complete HTML document with styling and metadata.
        
        :param html_content: Main HTML content
        :param title: Document title
        :return: Complete HTML document
        """
        title = title or "Document"
        css = self.config['css_styles']
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        {css['base']}
        {css.get('header', '')}
        {css.get('footer', '')}
        @page {{
            size: {self.config['pdf_options'].get('page-size', 'A4')};
            margin: 0;
        }}
        .page-content {{
            padding: {self.config['pdf_options'].get('margin-top', '20mm')} 
                     {self.config['pdf_options'].get('margin-right', '20mm')} 
                     {self.config['pdf_options'].get('margin-bottom', '20mm')} 
                     {self.config['pdf_options'].get('margin-left', '20mm')};
        }}
    </style>
</head>
<body>
    <header>
        <h1>{title}</h1>
    </header>
    <div class="page-content">
        {html_content}
    </div>
    <footer>
        Page <span class="page-number"></span> | Generated on {time.strftime('%Y-%m-%d %H:%M')}
    </footer>
    <script>
        // Add page numbers
        document.addEventListener('DOMContentLoaded', function() {{
            var pageCount = 1;
            var elements = document.querySelectorAll('.page-number');
            elements.forEach(function(el) {{
                el.textContent = pageCount++;
            }});
        }});
    </script>
</body>
</html>
        """
    
    def _convert_to_pdf(self, html_content: str, output_pdf: str):
        """
        Convert HTML content to PDF with error handling and retries.
        
        :param html_content: HTML to convert
        :param output_pdf: Output PDF path
        """
        options = self.config['pdf_options'].copy()
        options.update(self.config['metadata'])
        
        # Create temporary directory for working files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_html = os.path.join(temp_dir, 'temp.html')
            
            try:
                # Write HTML to temporary file
                with open(temp_html, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                logger.info(f"Generating PDF: {output_pdf}")
                
                # First try with standard options
                try:
                    pdfkit.from_file(temp_html, output_pdf, options=options)
                    return
                except Exception as first_error:
                    logger.warning(f"First PDF generation attempt failed: {str(first_error)}")
                    logger.info("Retrying with simplified options...")
                    
                    # Retry with simplified options
                    retry_options = {
                        'quiet': '',
                        'page-size': options.get('page-size', 'A4'),
                        'encoding': 'UTF-8'
                    }
                    pdfkit.from_file(temp_html, output_pdf, options=retry_options)
                    
            except Exception as e:
                raise ConversionError(f"PDF generation failed: {str(e)}")
    
    def convert(self, markdown_file: str, output_pdf: str):
        """
        Convert a Markdown file to PDF with full processing pipeline.
        
        :param markdown_file: Path to input Markdown file
        :param output_pdf: Path to output PDF file
        """
        try:
            # Validate inputs
            self._validate_inputs(markdown_file, output_pdf)
            
            # Read and process content
            markdown_content = self._read_markdown(markdown_file)
            html_content = self._convert_to_html(markdown_content)
            
            # Extract title from first h1 or filename
            title = os.path.splitext(os.path.basename(markdown_file))[0]
            if '<h1>' in html_content:
                # Simple extraction of first h1 content
                h1_start = html_content.find('<h1>') + 4
                h1_end = html_content.find('</h1>', h1_start)
                if h1_start > 3 and h1_end > h1_start:
                    title = html_content[h1_start:h1_end].strip()
            
            # Generate complete document
            full_html = self._generate_html_document(html_content, title)
            
            # Convert to PDF
            self._convert_to_pdf(full_html, output_pdf)
            
            logger.info(f"Successfully created PDF: {output_pdf}")
            return True
            
        except ConversionError as e:
            logger.error(f"Conversion failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during conversion: {str(e)}")
            raise ConversionError(f"Unexpected error: {str(e)}")

def setup_logging(verbose: bool = False, log_file: Optional[str] = None):
    """
    Configure logging system.
    
    :param verbose: Enable debug logging if True
    :param log_file: Optional file to write logs to
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

def parse_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description='Convert Markdown files to PDF with advanced formatting options.',
        epilog='Example: markdown_to_pdf.py input.md output.pdf --config config.yaml --verbose'
    )
    
    parser.add_argument('input', help='Input Markdown file path')
    parser.add_argument('output', help='Output PDF file path')
    parser.add_argument('-c', '--config', help='Path to YAML configuration file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-l', '--log', help='Log file path')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    
    return parser.parse_args()

def main():
    """
    Main entry point for command-line execution.
    """
    try:
        args = parse_args()
        setup_logging(args.verbose, args.log)
        
        logger.info(f"Starting conversion: {args.input} -> {args.output}")
        
        converter = MarkdownToPDFConverter(args.config)
        converter.convert(args.input, args.output)
        
        logger.info("Conversion completed successfully")
        return 0
        
    except ConversionError:
        return 1
    except KeyboardInterrupt:
        logger.info("Conversion cancelled by user")
        return 2
    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
        return 3

if __name__ == '__main__':
    sys.exit(main())
