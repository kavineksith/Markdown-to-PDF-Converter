# Markdown to PDF Converter

A **Markdown to PDF converter** built in Python. This utility transforms Markdown files into well-styled PDF documents with enhanced features like:

- Robust error handling  
- YAML-based configuration support  
- Advanced styling and CSS customization  
- PDF metadata and page formatting  
- Comprehensive logging system  
- Smart Markdown parsing with rich extensions  
- Dependency checks for external tools

Ideal for generating printable reports, documentation, or technical papers directly from Markdown sources.

## 📦 Features

- **YAML Configuration**: Customize PDF rendering options, metadata, margins, and styles.
- **Syntax Highlighting & TOC**: Supports `codehilite`, `toc`, and more via the `markdown` library.
- **Advanced CSS Styling**: Define global typography, page layout, headers/footers, and responsive styles.
- **Error Resilience**: Built-in exceptions for configuration, input, and dependency issues.
- **Extensive Logging**: Log to console or file with configurable verbosity.
- **Metadata Embedding**: Set producer, creator, and document title in the resulting PDF.

## 🚀 Installation

1. **Install dependencies**:

```bash
pip install markdown pdfkit pyyaml
````

2. **Install `wkhtmltopdf`** (required for PDF generation):

* **Ubuntu/Debian**:

  ```bash
  sudo apt install wkhtmltopdf
  ```
* **macOS**:

  ```bash
  brew install wkhtmltopdf
  ```
* **Windows**:
  Download and install from [https://wkhtmltopdf.org/downloads.html](https://wkhtmltopdf.org/downloads.html).
  Ensure `wkhtmltopdf` is in your system PATH.

## ⚙️ Usage

### Basic

```bash
python markdown_to_pdf.py input.md output.pdf
```

### With Configuration

```bash
python markdown_to_pdf.py input.md output.pdf --config config.yaml
```

### Full Example with Logging

```bash
python markdown_to_pdf.py README.md README.pdf --config settings.yaml --verbose --log conversion.log
```

## 📝 Configuration (`config.yaml`)

Example YAML configuration file:

```yaml
pdf_options:
  page-size: A4
  margin-top: 20mm
  margin-bottom: 20mm
  encoding: UTF-8

metadata:
  creator: "John Doe"
  producer: "Markdown to PDF"

css_styles:
  base: |
    body {
      font-family: 'Georgia', serif;
      font-size: 12pt;
    }
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🛡 Disclaimer

This tool wraps `pdfkit` and `wkhtmltopdf`, which use a headless browser to render HTML. As such:

* Output rendering may vary by system.
* Ensure `wkhtmltopdf` is installed and compatible with your OS.
* Not all CSS or HTML features may render identically to a modern browser.

Use at your own discretion and test thoroughly before production usage.

This software is provided "as is" without warranty of any kind, express or implied. The authors are not responsible for any legal implications of generated license files or repository management actions.  **This is a personal project intended for educational purposes. The developer makes no guarantees about the reliability or security of this software. Use at your own risk.**
