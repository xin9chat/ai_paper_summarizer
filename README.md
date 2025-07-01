# AI Paper Deconstructor

This project is a powerful Python command-line tool that deconstructs a research paper from a PDF, using a local Hugging Face transformer model to generate structured, section-by-section analyses.

Instead of just a single summary, this tool can identify key sections of a paper (like the introduction, method, and conclusion) and summarize each one individually. This allows you to create custom reports tailored to your specific research needs.

## Features

- **Intelligent Section Parsing**: Automatically identifies and extracts distinct sections from a research paper (e.g., Abstract, Introduction, Method, Results, Conclusion).
- **Targeted AI Summarization**: Uses the `sshleifer/distilbart-cnn-12-6` model to summarize either the entire paper or specific sections you choose.
- **Custom Report Generation**: You decide what goes into the final report. Mix and match sections to get the analysis you need.
- **Adjustable Summary Length**: Control the verbosity of each AI-generated summary with `--max-length` and `--min-length` parameters.
- **Structured Markdown Output**: Saves the analysis into a clean, well-formatted, and readable Markdown file.

## Requirements

- Python 3.7+
- `pip`

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd ai_paper_summarizer
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The tool is controlled via command-line arguments. The `--section` argument is the most important, as it tells the tool what to include in the final report.

### Command-Line Arguments

*   `--input` (required): The path to the input PDF file.
*   `--output` (required): The path for the output `.md` report.
*   `--section` (required): The section to include. **This can be used multiple times.**
    *   **Available Choices**: `title`, `abstract`, `summary`, `introduction`, `method`, `results`, `conclusion`, `contribution`, `literature_review`, `references`, `all`.
*   `--max-length` (optional): The maximum number of tokens for each AI-generated summary. Default: `150`.
*   `--min-length` (optional): The minimum number of tokens for each AI-generated summary. Default: `40`.

### Examples

**1. Get a quick, high-level summary:**
```bash
python main.py --input paper.pdf --output summary.md --section summary
```

**2. Deconstruct the methodology and results:**
```bash
python main.py --input paper.pdf --output analysis.md --section title --section method --section results
```

**3. Create a short summary of the paper's key contribution:**
```bash
python main.py --input paper.pdf --output contrib.md --section contribution --max-length 80
```

**4. Generate a comprehensive report of the entire paper:**
```bash
python main.py --input paper.pdf --output full_report.md --section all
```

---
*This project was built with the assistance of an AI agent.*