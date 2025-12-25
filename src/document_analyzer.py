"""Document analysis and text processing utilities."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


class DocumentAnalyzer:
    """Analyze and process Google Docs content."""

    def __init__(self):
        """Initialize the document analyzer."""
        pass

    def analyze_document(
        self,
        text_content: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive document analysis.
        
        Args:
            text_content: Plain text content from document
            options: Analysis options (extractKeywords, summarize, etc.)
            
        Returns:
            Dictionary containing analysis results
        """
        if options is None:
            options = {}

        results = {}

        # Word count (always included)
        if options.get('wordCount', True):
            results['statistics'] = self._calculate_statistics(text_content)

        # Extract keywords
        if options.get('extractKeywords', False):
            results['keywords'] = self._extract_keywords(text_content)

        # Generate summary
        if options.get('summarize', False):
            results['summary'] = self._generate_summary(text_content)

        # Extract links
        if options.get('extractLinks', False):
            results['links'] = self._extract_links(text_content)

        # Detect language
        if options.get('detectLanguage', False):
            results['language'] = self._detect_language(text_content)

        # Extract structure
        results['structure'] = self._analyze_structure(text_content)

        return results

    def _calculate_statistics(self, text: str) -> Dict[str, Any]:
        """Calculate document statistics.
        
        Args:
            text: Document text
            
        Returns:
            Statistics dictionary
        """
        # Clean text
        clean_text = text.strip()
        
        # Count characters
        char_count = len(clean_text)
        char_count_no_spaces = len(clean_text.replace(' ', '').replace('\n', ''))
        
        # Count words
        words = clean_text.split()
        word_count = len(words)
        
        # Count lines and paragraphs
        lines = clean_text.split('\n')
        line_count = len(lines)
        paragraphs = [p for p in clean_text.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)
        
        # Count sentences (approximate)
        sentences = re.split(r'[.!?]+', clean_text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        # Average sentence length
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0

        return {
            'characterCount': char_count,
            'characterCountNoSpaces': char_count_no_spaces,
            'wordCount': word_count,
            'lineCount': line_count,
            'paragraphCount': paragraph_count,
            'sentenceCount': sentence_count,
            'averageWordLength': round(avg_word_length, 2),
            'averageSentenceLength': round(avg_sentence_length, 2),
            'readingTime': round(word_count / 200, 1)  # Assuming 200 words per minute
        }

    def _extract_keywords(self, text: str, top_n: int = 20) -> List[Dict[str, Any]]:
        """Extract keywords and key phrases from text.
        
        Args:
            text: Document text
            top_n: Number of top keywords to return
            
        Returns:
            List of keywords with frequency
        """
        # Convert to lowercase and remove punctuation
        clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Common English stop words
        stop_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
            'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
            'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
            'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
            'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
            'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work',
            'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
            'give', 'day', 'most', 'us', 'is', 'was', 'are', 'been', 'has', 'had',
            'were', 'said', 'did', 'having', 'may', 'should'
        }
        
        # Extract words
        words = clean_text.split()
        
        # Filter out stop words and short words
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Count frequency
        word_freq = Counter(keywords)
        
        # Get top keywords
        top_keywords = word_freq.most_common(top_n)
        
        return [
            {'keyword': word, 'frequency': count, 'relevance': round(count / len(keywords) * 100, 2)}
            for word, count in top_keywords
        ]

    def _generate_summary(self, text: str, max_sentences: int = 5) -> str:
        """Generate a simple extractive summary.
        
        Args:
            text: Document text
            max_sentences: Maximum number of sentences in summary
            
        Returns:
            Summary text
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if len(sentences) <= max_sentences:
            return '. '.join(sentences) + '.'
        
        # Simple scoring: prefer sentences with more words and near the beginning
        scored_sentences = []
        for i, sentence in enumerate(sentences[:min(len(sentences), 50)]):  # Only consider first 50 sentences
            words = sentence.split()
            score = len(words) * (1 - i / len(sentences) * 0.5)  # Length + position bias
            scored_sentences.append((score, sentence))
        
        # Sort by score and get top sentences
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        top_sentences = [s for _, s in scored_sentences[:max_sentences]]
        
        # Return in original order
        summary_sentences = []
        for sentence in sentences:
            if sentence in top_sentences:
                summary_sentences.append(sentence)
                if len(summary_sentences) >= max_sentences:
                    break
        
        return '. '.join(summary_sentences) + '.'

    def _extract_links(self, text: str) -> List[Dict[str, Any]]:
        """Extract URLs from text.
        
        Args:
            text: Document text
            
        Returns:
            List of extracted URLs with metadata
        """
        # URL pattern
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        
        urls = re.findall(url_pattern, text)
        
        # Remove duplicates and parse
        unique_urls = list(set(urls))
        
        link_data = []
        for url in unique_urls:
            parsed = urlparse(url)
            link_data.append({
                'url': url,
                'domain': parsed.netloc,
                'scheme': parsed.scheme,
                'count': text.count(url)
            })
        
        return link_data

    def _detect_language(self, text: str) -> str:
        """Detect document language (simple heuristic-based).
        
        Args:
            text: Document text
            
        Returns:
            Detected language code
        """
        # This is a simple heuristic - for production, use a proper language detection library
        # Count common words in different languages
        
        english_words = {'the', 'is', 'and', 'to', 'of', 'in', 'that', 'for'}
        spanish_words = {'el', 'la', 'de', 'que', 'y', 'en', 'es', 'por'}
        french_words = {'le', 'de', 'un', 'et', 'être', 'à', 'il', 'que'}
        german_words = {'der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das'}
        
        words = set(text.lower().split())
        
        en_count = len(words.intersection(english_words))
        es_count = len(words.intersection(spanish_words))
        fr_count = len(words.intersection(french_words))
        de_count = len(words.intersection(german_words))
        
        max_count = max(en_count, es_count, fr_count, de_count)
        
        if max_count == 0:
            return 'unknown'
        elif max_count == en_count:
            return 'en'
        elif max_count == es_count:
            return 'es'
        elif max_count == fr_count:
            return 'fr'
        elif max_count == de_count:
            return 'de'
        
        return 'unknown'

    def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """Analyze document structure.
        
        Args:
            text: Document text
            
        Returns:
            Structure analysis
        """
        # Detect potential headings (lines that are short and followed by longer text)
        lines = text.split('\n')
        potential_headings = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if 3 < len(line_stripped.split()) <= 10:  # Short lines that might be headings
                # Check if followed by longer content
                if i + 1 < len(lines) and len(lines[i + 1].strip().split()) > 10:
                    potential_headings.append({
                        'text': line_stripped,
                        'position': i,
                        'level': self._guess_heading_level(line_stripped)
                    })
        
        # Detect lists
        list_items = []
        list_patterns = [
            r'^\s*[\-\*\•]\s+',  # Bullet points
            r'^\s*\d+[\.\)]\s+',  # Numbered lists
            r'^\s*[a-z][\.\)]\s+',  # Lettered lists
        ]
        
        for i, line in enumerate(lines):
            for pattern in list_patterns:
                if re.match(pattern, line):
                    list_items.append({
                        'text': line.strip(),
                        'position': i,
                        'type': 'bullet' if pattern == list_patterns[0] else 'numbered'
                    })
                    break
        
        return {
            'headings': potential_headings,
            'listItems': list_items,
            'hasStructure': len(potential_headings) > 0 or len(list_items) > 0
        }

    def _guess_heading_level(self, text: str) -> int:
        """Guess heading level based on text characteristics.
        
        Args:
            text: Heading text
            
        Returns:
            Heading level (1-6)
        """
        # Simple heuristic: shorter and ALL CAPS = higher level
        if text.isupper():
            return 1
        elif len(text.split()) <= 5:
            return 2
        else:
            return 3

    def extract_tables(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract table data from document structure.
        
        Args:
            document_data: Full document data from Google Docs API
            
        Returns:
            List of table data
        """
        tables = []
        
        if 'body' not in document_data or 'content' not in document_data['body']:
            return tables
        
        for element in document_data['body']['content']:
            if 'table' in element:
                table_data = self._parse_table(element['table'])
                tables.append(table_data)
        
        return tables

    def _parse_table(self, table_element: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a table element into structured data.
        
        Args:
            table_element: Table element from document
            
        Returns:
            Structured table data
        """
        rows = []
        
        for row in table_element.get('tableRows', []):
            cells = []
            for cell in row.get('tableCells', []):
                cell_text = []
                for content in cell.get('content', []):
                    if 'paragraph' in content:
                        for element in content['paragraph'].get('elements', []):
                            if 'textRun' in element:
                                cell_text.append(element['textRun']['content'])
                cells.append(''.join(cell_text).strip())
            rows.append(cells)
        
        return {
            'rows': len(rows),
            'columns': len(rows[0]) if rows else 0,
            'data': rows
        }
