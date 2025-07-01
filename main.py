import fitz  # PyMuPDF
import argparse
import re
from transformers import pipeline

# --- Core Extraction and Summarization Logic ---

def extract_sections(text: str) -> dict:
    """
    Identifies and extracts key sections of a research paper using regex.
    """
    print("Identifying paper sections...")
    # Regex to find section headings (e.g., 1. Introduction, II. Method)
    # This pattern looks for a number, optional dot, optional space, and then a capitalized word.
    pattern = re.compile(r"^\s*(\d{1,2}|[IVXLCDM]+)\.?\s+([A-Z][a-zA-Z\s]+)", re.MULTILINE)
    
    sections = {'raw_text': text}
    last_match_end = 0
    
    # Simple title and abstract extraction (heuristic)
    lines = text.split('\n')
    sections['title'] = lines[0].strip()
    
    abstract_match = re.search(r"Abstract\n([\s\S]*?)(1\.?\s+Introduction)", text, re.IGNORECASE)
    if abstract_match:
        sections['abstract'] = abstract_match.group(1).strip()

    # Find all section headings
    matches = list(pattern.finditer(text))
    
    for i, match in enumerate(matches):
        section_title = match.group(2).strip().lower().replace(" ", "_")
        start_index = match.end()
        
        end_index = matches[i+1].start() if i + 1 < len(matches) else len(text)
        
        section_content = text[start_index:end_index].strip()
        
        # Common section name normalization
        if 'introduction' in section_title:
            sections['introduction'] = section_content
        elif 'method' in section_title or 'methodology' in section_title:
            sections['method'] = section_content
        elif 'result' in section_title or 'experiment' in section_title:
            sections['results'] = section_content
        elif 'conclusion' in section_title or 'discussion' in section_title:
            sections['conclusion'] = section_content
        elif 'related_work' in section_title or 'literature_review' in section_title:
            sections['literature_review'] = section_content
        elif 'reference' in section_title:
            sections['references'] = section_content

    print(f"Found sections: {list(sections.keys())}")
    return sections

def summarize_text(text: str, min_length: int, max_length: int, max_chunk_length: int = 1024) -> str:
    """
    Summarizes a given text using a Hugging Face model, with length controls.
    """
    try:
        summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", revision="a4f8f3e")
    except Exception as e:
        return f"Failed to load model. Error: {e}"

    text_chunks = [text[i:i+max_chunk_length] for i in range(0, len(text), max_chunk_length)]
    summary_parts = []
    print(f"  - Summarizing {len(text_chunks)} chunks...")
    
    for chunk in text_chunks:
        summary = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
        summary_parts.append(summary[0]['summary_text'])
        
    return " ".join(summary_parts)

# --- File I/O ---

def save_to_markdown(content: str, output_path: str):
    """
    Saves the final report to a Markdown file.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\nSuccessfully saved report to {output_path}")
    except IOError as e:
        print(f"Error writing to file {output_path}: {e}")

# --- Main Orchestration ---

def main():
    parser = argparse.ArgumentParser(description="Deconstruct a research paper into a structured Markdown file.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input PDF file.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output Markdown file.")
    parser.add_argument("--section", type=str, action='append', required=True, 
                        choices=['title', 'abstract', 'summary', 'introduction', 'method', 'results', 
                                 'conclusion', 'contribution', 'literature_review', 'references', 'all'],
                        help="Section to include in the report. Can be specified multiple times.")
    parser.add_argument("--max-length", type=int, default=150, help="Max token length for each summary section.")
    parser.add_argument("--min-length", type=int, default=40, help="Min token length for each summary section.")

    args = parser.parse_args()

    # --- 1. Extraction ---
    print(f"Processing {args.input}...")
    try:
        doc = fitz.open(args.input)
        full_text = "".join(page.get_text() for page in doc)
        doc.close()
    except Exception as e:
        print(f"Failed to read PDF: {e}")
        return

    sections = extract_sections(full_text)
    report_content = ""

    # --- 2. Processing Requested Sections ---
    requested_sections = args.section
    if 'all' in requested_sections:
        requested_sections = ['title', 'abstract', 'summary', 'introduction', 'method', 'results', 'conclusion', 'contribution', 'literature_review']

    print(f"\nGenerating report for sections: {', '.join(requested_sections)}")

    for section_name in requested_sections:
        print(f"Processing section: {section_name.capitalize()}...")
        content = sections.get(section_name)
        
        if not content and section_name not in ['summary', 'contribution']:
            print(f"  - Section not found or extracted.")
            continue

        report_content += f"## {section_name.replace('_', ' ').capitalize()}\n"

        # --- 3. Summarization or Direct Extraction ---
        if section_name in ['title', 'abstract', 'references']:
            report_content += f"{content}\n\n"
        elif section_name == 'summary':
            summary = summarize_text(sections['raw_text'], args.min_length, args.max_length)
            report_content += f"{summary}\n\n"
        elif section_name == 'contribution':
            contrib_text = sections.get('abstract', '') + " " + sections.get('conclusion', '')
            if contrib_text.strip():
                contribution = summarize_text(contrib_text, args.min_length, args.max_length)
                report_content += f"{contribution}\n\n"
            else:
                report_content += "Could not determine contribution (abstract or conclusion not found).\n\n"
        else: # All other sections that need summarization
            summary = summarize_text(content, args.min_length, args.max_length)
            report_content += f"{summary}\n\n"

    # --- 4. Final Output ---
    final_report = f"# Analysis of {sections.get('title', 'Unknown Paper')}\n\n{report_content}"
    final_report += "---\n*Report generated by the AI Paper Deconstructor.*"
    
    save_to_markdown(final_report, args.output)

if __name__ == "__main__":
    main()
