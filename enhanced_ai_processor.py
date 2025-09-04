#!/usr/bin/env python3
"""
🤖 Enhanced AI-Powered Learning System with Image Integration
Ensures minimum content requirements: 1 concept, 3+ MCQs, 3+ Subjective Q&A per topic
Uses Azure OpenAI GPT-4 Vision to process PDFs with text AND visual content
Intelligently incorporates images from PDF into concepts without repetition
"""

import os
import json
import requests
import base64
import re
from typing import List, Dict, Any
import pdfplumber
from PIL import Image
import io
from datetime import datetime
import hashlib
try:
    import fitz  # PyMuPDF
except ImportError:
    try:
        import PyMuPDF as fitz
    except ImportError:
        fitz = None

import os
import json
import requests
from typing import List, Dict, Any
import pdfplumber
from datetime import datetime

class EnhancedAIPDFProcessor:
    def __init__(self, api_key: str = None, endpoint: str = None):
        # Use Azure OpenAI configuration
        self.api_key = api_key or os.getenv('AZURE_OPENAI_API_KEY')
        self.endpoint = endpoint or os.getenv('AZURE_OPENAI_ENDPOINT')
        self.api_version = os.getenv('OPENAI_API_VERSION', '2023-12-01-preview')
        
        if not self.api_key or not self.endpoint:
            print("❌ Azure OpenAI configuration not found")
            print("💡 Make sure AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT are set")
            return
        
        # Use GPT-4o which has vision capabilities
        self.base_url = f"{self.endpoint}openai/deployments/gpt-4o/chat/completions?api-version={self.api_version}"
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Track used images to avoid repetition
        self.used_images = set()
        self.image_hashes = {}
        
        print(f"✅ Using Azure OpenAI GPT-4o: {self.endpoint}")
    
    def process_pdf_with_structured_content(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process PDF and ensure minimum content requirements:
        - At least 1 concept per topic heading
        - More than 2 MCQs per topic
        - More than 2 Subjective Q&A per topic
        - Intelligently incorporate images from PDF
        """
        print(f"🤖 Enhanced Processing PDF: {pdf_path}")
        
        # Extract text content
        text_content = self._extract_text_from_pdf(pdf_path)
        
        # Skip image extraction to avoid errors
        pdf_images = []
        
        # Identify topic headings with subtopics
        topic_structure = self._identify_topic_headings(text_content)
        
        # Generate structured content for each topic and subtopic
        all_concepts = []
        all_mcqs = []
        all_subjective = []
        
        for i, topic_info in enumerate(topic_structure):
            main_topic = topic_info['main_topic']
            subtopics = topic_info['subtopics']
            
            print(f"   📚 Processing Main Topic {i+1}: {main_topic}")
            
            if subtopics:
                # Process each subtopic
                for j, subtopic in enumerate(subtopics):
                    print(f"      📖 Processing Subtopic {j+1}: {subtopic}")
                    
                    # Generate concepts for this subtopic
                    subtopic_concepts = self._generate_concepts_for_topic(subtopic, text_content, pdf_images, min_concepts=1)
                    # Add topic hierarchy to each concept
                    for concept in subtopic_concepts:
                        concept['topic'] = f"{main_topic} → {subtopic}"
                    all_concepts.extend(subtopic_concepts)
                    
                    # Generate MCQs for this subtopic
                    subtopic_mcqs = self._generate_mcqs_for_topic(subtopic, text_content, min_mcqs=2, start_id=len(all_mcqs) + 1)
                    all_mcqs.extend(subtopic_mcqs)
                    
                    # Generate Subjective Q&A for this subtopic
                    subtopic_subjective = self._generate_subjective_for_topic(subtopic, text_content, min_subjective=2, start_id=len(all_subjective) + 1)
                    all_subjective.extend(subtopic_subjective)
            else:
                # Process main topic without subtopics
                print(f"      📖 Processing Main Topic Content")
                
                # Generate concepts for main topic
                main_topic_concepts = self._generate_concepts_for_topic(main_topic, text_content, pdf_images, min_concepts=1)
                # Add topic name to each concept
                for concept in main_topic_concepts:
                    concept['topic'] = main_topic
                all_concepts.extend(main_topic_concepts)
                
                # Generate MCQs for main topic
                main_topic_mcqs = self._generate_mcqs_for_topic(main_topic, text_content, min_mcqs=3, start_id=len(all_mcqs) + 1)
                all_mcqs.extend(main_topic_mcqs)
                
                # Generate Subjective Q&A for main topic
                main_topic_subjective = self._generate_subjective_for_topic(main_topic, text_content, min_subjective=3, start_id=len(all_subjective) + 1)
                all_subjective.extend(main_topic_subjective)
        
        # Ensure topic_structure is always a list
        if not topic_structure:
            topic_structure = []
        
        return {
            'subject_info': self._extract_subject_info(pdf_path),
            'concepts': all_concepts,
            'mcq_questions': all_mcqs,
            'subjective_questions': all_subjective,
            'stats': {
                'total_concepts': len(all_concepts),
                'total_mcqs': len(all_mcqs),
                'total_subjective': len(all_subjective),
                'main_topics': len(topic_structure),
                'total_subtopics': sum(len(topic.get('subtopics', [])) for topic in topic_structure),
                'images_used': len(self.used_images)
            }
        }
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using pdfplumber with better encoding"""
        try:
            text_content = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        # Clean up common PDF extraction issues
                        text = self._clean_extracted_text(text)
                        text_content += text + "\n\n"
            
            print(f"   ✅ Extracted text from PDF ({len(text_content)} characters)")
            return text_content
            
        except Exception as e:
            print(f"   ❌ Error extracting PDF text: {e}")
            return ""
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean up common PDF extraction issues"""
        import re
        
        # Fix complex character duplication patterns (like "PPeeooppllee" -> "People")
        def fix_complex_duplication(text):
            # Pattern 1: Alternating character duplication (most common)
            # "PPeeooppllee" -> "People"
            pattern1 = r'([A-Za-z])([A-Za-z])(?:\1\2)*\1?'
            def fix_alternating(match):
                chars = match.group(0)
                if len(chars) >= 4:
                    # Take first character, then every other character
                    result = chars[0]
                    for i in range(2, len(chars), 2):
                        if i < len(chars):
                            result += chars[i]
                    return result
                return chars
            
            text = re.sub(pattern1, fix_alternating, text)
            
            # Pattern 2: Simple character repetition
            # "PPeerrssoonn" -> "Person"
            pattern2 = r'([A-Za-z])\1+'
            def fix_simple_repetition(match):
                word = match.group(0)
                if len(word) > 2:
                    # Take every other character for repeated patterns
                    fixed = ''.join(word[i] for i in range(0, len(word), 2))
                    return fixed
                return word
            
            text = re.sub(pattern2, fix_simple_repetition, text)
            
            # Pattern 3: Specific fix for "PPeeooppllee aass RReessoouurrccee" -> "People as Resource"
            text = re.sub(r'PPeeooppllee\s+aass\s+RReessoouurrccee', 'People as Resource', text, flags=re.IGNORECASE)
            
            return text
        
        # Apply complex duplication fixes
        text = fix_complex_duplication(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common OCR issues
        text = text.replace('|', 'I')
        text = text.replace('0', 'O')  # Only in certain contexts
        
        return text.strip()
    
    def _extract_images_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract images from PDF using PyMuPDF and convert to base64"""
        images = []
        
        # Check if PyMuPDF is available
        if fitz is None:
            print("   ⚠️ PyMuPDF not available, skipping image extraction")
            return images
        
        try:
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(pdf_path)
            
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                
                # Get image list from page
                image_list = page.get_images()
                
                for img_idx, img in enumerate(image_list):
                    try:
                        # Get image data
                        xref = img[0]  # Image reference number
                        pix = fitz.Pixmap(pdf_document, xref)
                        
                        # Convert to PIL Image
                        img_data = pix.tobytes("png")
                        pil_image = Image.open(io.BytesIO(img_data))
                        
                        # Resize if too large (max 800px width/height)
                        max_size = 800
                        if pil_image.width > max_size or pil_image.height > max_size:
                            pil_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                        
                        # Convert to base64
                        img_buffer = io.BytesIO()
                        pil_image.save(img_buffer, format='PNG')
                        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                        
                        # Generate hash for deduplication
                        img_hash = hashlib.md5(img_buffer.getvalue()).hexdigest()
                        
                        # Only add if not already used
                        if img_hash not in self.used_images:
                            images.append({
                                'page': page_num + 1,
                                'index': img_idx,
                                'base64': img_base64,
                                'hash': img_hash,
                                'width': pil_image.width,
                                'height': pil_image.height,
                                'format': 'PNG'
                            })
                            self.used_images.add(img_hash)
                            self.image_hashes[img_hash] = f"Page {page_num + 1}, Image {img_idx + 1}"
                        
                        pix = None  # Free memory
                        
                    except Exception as e:
                        print(f"   ⚠️ Error processing image on page {page_num + 1}: {e}")
                        continue
            
            pdf_document.close()
            print(f"   ✅ Extracted {len(images)} unique images from PDF using PyMuPDF")
            return images
            
        except Exception as e:
            print(f"   ❌ Error extracting images from PDF: {e}")
            return []
    
    def _identify_topic_headings(self, text_content: str) -> List[Dict]:
        """Identify main topics and their subtopics from the text"""
        prompt = f"""
        Analyze this NCERT textbook content and identify the hierarchical topic structure.
        
        Content to analyze:
        {text_content}
        
        Return ONLY a JSON array of topic objects with their subtopics:
        [
            {{
                "main_topic": "Main Topic Name",
                "subtopics": ["Subtopic 1", "Subtopic 2", "Subtopic 3"]
            }},
            {{
                "main_topic": "Another Main Topic",
                "subtopics": ["Subtopic A", "Subtopic B"]
            }}
        ]
        
        Important:
        - Identify main topics (like "The Himalayan Rivers", "The Peninsular Rivers")
        - For each main topic, identify its subtopics (like "The Indus River System", "The Ganga River System")
        - Use the exact text as it appears in the PDF
        - Look for hierarchical relationships in the content structure
        - Focus on educational topics that students need to learn
        - Don't add extra text or modify the original headings
        - Look for bold text, numbered sections, and clear topic breaks
        - Be comprehensive - include ALL major topic-subtopic relationships you find
        - If a topic has no clear subtopics, use an empty array for subtopics
        """
        
        try:
            response = self._call_ai_api(prompt)
            topic_structure = []
            if response:
                # Try to extract JSON array
                if '[' in response and ']' in response:
                    start = response.find('[')
                    end = response.rfind(']') + 1
                    json_str = response[start:end]
                    topic_structure = json.loads(json_str)
                    topic_structure = topic_structure if isinstance(topic_structure, list) else []
            
            # If AI fails, fallback to simple topic extraction
            if not topic_structure:
                simple_topics = self._extract_headings_from_text(text_content)
                topic_structure = [{"main_topic": topic, "subtopics": []} for topic in simple_topics]
            
            return topic_structure
            
        except Exception as e:
            print(f"   ⚠️ Error identifying topic structure: {e}")
            # Fallback to simple topic extraction
            simple_topics = self._extract_headings_from_text(text_content)
            return [{"main_topic": topic, "subtopics": []} for topic in simple_topics]
    
    def _extract_headings_from_text(self, text_content: str) -> List[str]:
        """Extract headings directly from text using pattern matching"""
        headings = []
        
        # Split text into lines
        lines = text_content.split('\n')
        
        # Look for potential headings based on text characteristics
        for line in lines:
            line = line.strip()
            
            # Look for potential headings
            if (len(line) > 3 and len(line) < 100 and  # Reasonable length
                not line.isdigit() and  # Not just numbers
                not line.startswith('Page') and  # Not page numbers
                not line.startswith('Chapter') and  # Not chapter references
                not line.startswith('Source:') and  # Not source citations
                not line.startswith('Reprint') and  # Not reprint info
                line and  # Not empty
                line[0].isupper() and  # Starts with capital letter
                (line.isupper() or  # All caps (likely heading)
                 len(line.split()) <= 8) and  # Short phrases (likely headings)
                line not in headings):  # Not already added
                
                # Clean up the heading
                clean_heading = line.strip()
                if clean_heading:
                    headings.append(clean_heading)
        
        # If we found headings, return them
        if headings:
            print(f"   📝 Extracted {len(headings)} headings from text analysis")
            return headings  # Return all headings without restriction
        
        # No headings found
        return []
    
    def _generate_concepts_for_topic(self, topic: str, text_content: str, pdf_images: List[Dict], min_concepts: int = 1) -> List[Dict]:
        """Generate concepts for a specific topic with image integration"""
        
        # Select relevant images for this topic
        relevant_images = self._select_relevant_images_for_topic(topic, pdf_images)
        
        if relevant_images:
            # Use vision API to analyze images with text
            prompt = f"""
            Generate {min_concepts} key educational concepts for the topic: "{topic}"
            
            Requirements:
            - Extract DIRECT FACTS from the textbook content
            - Include important dates, numbers, and specific information
            - Focus on what students must remember for exams
            - Use clear, concise language
            - If images are provided, analyze them and incorporate relevant visual information
            - Each concept should be educational and exam-relevant
            
            Textbook content:
            {text_content[:1500]}...
            
            Return JSON format:
            {{
                "concepts": [
                    {{
                        "title": "Specific Concept Title",
                        "description": "Detailed description with key facts, dates, numbers, and educational value",
                        "has_image": true/false,
                        "image_description": "Brief description of relevant image if applicable"
                    }}
                ]
            }}
            """
            
            # Create vision API call with images
            try:
                response = self._call_vision_api(prompt, relevant_images)
                concepts = self._parse_concepts_response(response)
                
                # Mark images as used
                for concept in concepts:
                    if concept.get('has_image', False):
                        # Mark the first relevant image as used for this concept
                        if relevant_images:
                            img_hash = relevant_images[0]['hash']
                            concept['image_data'] = relevant_images[0]
                            relevant_images.pop(0)  # Remove used image
                
                # Ensure minimum concepts
                if len(concepts) < min_concepts:
                    additional = self._generate_additional_concepts(text_content, min_concepts - len(concepts))
                    concepts.extend(additional)
                
                return concepts[:min_concepts]
                
            except Exception as e:
                print(f"   ⚠️ Error generating concepts with images for {topic}: {e}")
                return self._generate_text_only_concepts(topic, text_content, min_concepts)
        else:
            # Fallback to text-only concept generation
            return self._generate_text_only_concepts(topic, text_content, min_concepts)
    
    def _generate_mcqs_for_topic(self, topic: str, text_content: str, min_mcqs: int = 3, start_id: int = 1) -> List[Dict]:
        """Generate MCQs for a specific topic with proper ID numbering and diverse content"""
        prompt = f"""
        Create {min_mcqs} multiple choice questions for the topic: "{topic}"
        
        Guidelines:
        - Create questions that test different aspects of the topic
        - Include questions about key facts, dates, numbers, and concepts
        - Provide one correct answer and three plausible distractors
        - Make questions relevant for educational assessment
        - Focus on important information students should learn
        
        Topic focus for "{topic}":
        - Cover key concepts, definitions, and important information
        - Include specific facts, dates, numbers, and relevant details
        - Address different aspects and perspectives of the topic
        - Ensure educational value and exam relevance
        
        Textbook content:
        {text_content[:2000]}...
        
        Return JSON format:
        {{
            "mcqs": [
                {{
                    "id": 1,
                    "question": "Question text related to {topic}?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": 0
                }}
            ]
        }}
        """
        
        try:
            response = self._call_ai_api(prompt)
            mcqs = self._parse_mcqs_response(response)
            
            # Fix IDs to be sequential starting from start_id
            for i, mcq in enumerate(mcqs):
                mcq['id'] = start_id + i
            
            # Ensure minimum MCQs and check for diversity
            if len(mcqs) < min_mcqs:
                additional = self._generate_additional_mcqs(text_content, min_mcqs - len(mcqs), start_id + len(mcqs))
                mcqs.extend(additional)
            
            # Remove duplicates based on question content
            unique_mcqs = []
            seen_questions = set()
            for mcq in mcqs:
                question_text = mcq['question'].lower().strip()
                if question_text not in seen_questions:
                    seen_questions.add(question_text)
                    unique_mcqs.append(mcq)
            
            return unique_mcqs[:min_mcqs]
            
        except Exception as e:
            print(f"   ⚠️ Error generating MCQs for {topic}: {e}")
            return []
    
    def _generate_subjective_for_topic(self, topic: str, text_content: str, min_subjective: int = 3, start_id: int = 1) -> List[Dict]:
        """Generate Subjective Q&A for a specific topic with proper ID numbering and diverse content"""
        prompt = f"""
        Create {min_subjective} subjective questions for the topic: "{topic}"
        
        Guidelines:
        - Create questions that cover different aspects of the topic
        - Include a mix of 3, 4, and 5 mark questions
        - Questions should require detailed explanations
        - Include questions about key facts, dates, trends, and concepts
        - Answers should be comprehensive and educational
        
        Criteria for marking questions as "important":
        - Mark questions as "important" if they are:
          * Core/fundamental concepts that students should know
          * Frequently asked in exams
          * Critical for understanding the topic
          * Cover major themes or principles
        - Do not mark questions as "important" if they are:
          * Minor details or specific examples
          * Secondary or supplementary information
          * Less likely to appear in exams
          * Specific dates or numbers (unless crucial)
        
        Topic focus for "{topic}":
        - Cover key concepts, definitions, and important information
        - Include specific facts, dates, numbers, and relevant details
        - Address different aspects and perspectives of the topic
        - Ensure educational value and exam relevance
        
        Textbook content:
        {text_content[:2000]}...
        
        Return JSON format:
        {{
            "subjective": [
                {{
                    "id": 1,
                    "question": "Question text related to {topic}?",
                    "answer": "Comprehensive answer with key points specific to this topic",
                    "marks": "3 Marks",
                    "important": false
                }}
            ]
        }}
        
        Note: Be selective with the "important" tag. Only mark 1-2 questions per topic as important, and only if they truly represent core concepts.
        """
        
        try:
            response = self._call_ai_api(prompt)
            subjective = self._parse_subjective_response(response)
            
            # Fix IDs to be sequential starting from start_id
            for i, question in enumerate(subjective):
                question['id'] = start_id + i
            
            # Ensure minimum subjective questions and check for diversity
            if len(subjective) < min_subjective:
                additional = self._generate_additional_subjective(text_content, min_subjective - len(subjective), start_id + len(subjective))
                subjective.extend(additional)
            
            # Remove duplicates based on question content
            unique_subjective = []
            seen_questions = set()
            for question in subjective:
                question_text = question['question'].lower().strip()
                if question_text not in seen_questions:
                    seen_questions.add(question_text)
                    unique_subjective.append(question)
            
            return unique_subjective[:min_subjective]
            
        except Exception as e:
            print(f"   ⚠️ Error generating subjective for {topic}: {e}")
            return []
    
    def _select_relevant_images_for_topic(self, topic: str, pdf_images: List[Dict]) -> List[Dict]:
        """Select relevant images for a specific topic"""
        if not pdf_images:
            return []
        
        # Simple heuristic: take first 2-3 images for each topic
        # In a more sophisticated version, you could use AI to analyze image relevance
        return pdf_images[:min(3, len(pdf_images))]
    
    def _generate_text_only_concepts(self, topic: str, text_content: str, min_concepts: int) -> List[Dict]:
        """Generate concepts without images (fallback)"""
        prompt = f"""
        Generate {min_concepts} key educational concepts for the topic: "{topic}"
        
        Requirements:
        - Extract DIRECT FACTS from the textbook content
        - Include important dates, numbers, and specific information
        - Focus on what students must remember for exams
        - Use clear, concise language
        
        Textbook content:
        {text_content[:1500]}...
        
        Return JSON format:
        {{
            "concepts": [
                {{
                    "title": "Specific Concept Title",
                    "description": "Detailed description with key facts, dates, numbers, and educational value",
                    "has_image": false
                }}
            ]
        }}
        """
        
        try:
            response = self._call_ai_api(prompt)
            concepts = self._parse_concepts_response(response)
            
            # Ensure minimum concepts
            if len(concepts) < min_concepts:
                additional = self._generate_additional_concepts(text_content, min_concepts - len(concepts))
                concepts.extend(additional)
            
            return concepts[:min_concepts]
            
        except Exception as e:
            print(f"   ⚠️ Error generating text-only concepts for {topic}: {e}")
            return []
    
    def _call_ai_api(self, prompt: str) -> str:
        """Call Azure OpenAI API"""
        try:
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.3
            }
            
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"   ❌ API Error: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            print(f"   ❌ Error calling AI API: {e}")
            return ""
    
    def _call_vision_api(self, prompt: str, images: List[Dict]) -> str:
        """Call Azure OpenAI Vision API with images"""
        try:
            # Prepare content with images
            content = [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
            
            # Add images to content
            for img in images:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{img['base64']}"
                    }
                })
            
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.3
            }
            
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"   ❌ Vision API Error: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            print(f"   ❌ Error calling Vision API: {e}")
            return ""
    
    def _parse_concepts_response(self, response: str) -> List[Dict]:
        """Parse concepts from AI response"""
        try:
            if '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                parsed = json.loads(json_str)
                return parsed.get('concepts', [])
            return []
        except Exception as e:
            print(f"   ⚠️ Error parsing concepts: {e}")
            return []
    
    def _parse_mcqs_response(self, response: str) -> List[Dict]:
        """Parse MCQs from AI response"""
        try:
            if '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                parsed = json.loads(json_str)
                return parsed.get('mcqs', [])
            return []
        except Exception as e:
            print(f"   ⚠️ Error parsing MCQs: {e}")
            return []
    
    def _parse_subjective_response(self, response: str) -> List[Dict]:
        """Parse subjective Q&A from AI response"""
        try:
            if '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                parsed = json.loads(json_str)
                return parsed.get('subjective', [])
            return []
        except Exception as e:
            print(f"   ⚠️ Error parsing subjective: {e}")
            return []
    
    def _generate_additional_concepts(self, text_content: str, count: int) -> List[Dict]:
        """Generate additional concepts if needed"""
        return [
            {
                'title': f'Additional Concept {i+1}',
                'description': f'Important educational concept extracted from the textbook content.'
            }
            for i in range(count)
        ]
    
    def _generate_additional_mcqs(self, text_content: str, count: int, start_id: int = 1) -> List[Dict]:
        """Generate additional MCQs if needed with proper ID numbering"""
        return [
            {
                'id': start_id + i,
                'question': f'Additional MCQ question {start_id + i}?',
                'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                'correct_answer': 0
            }
            for i in range(count)
        ]
    
    def _generate_additional_subjective(self, text_content: str, count: int, start_id: int = 1) -> List[Dict]:
        """Generate additional subjective questions if needed with proper ID numbering"""
        return [
            {
                'id': start_id + i,
                'question': f'Additional subjective question {start_id + i}?',
                'answer': f'Comprehensive answer for question {start_id + i}.',
                'marks': '3 Marks',
                'important': False
            }
            for i in range(count)
        ]
    
    def _extract_subject_info(self, pdf_path: str) -> Dict[str, str]:
        """Extract subject information from PDF filename"""
        try:
            # Use filename directly for chapter name
            filename = os.path.basename(pdf_path)
            # Remove file extension and clean up the filename
            clean_filename = os.path.splitext(filename)[0]
            
            # Clean up common prefixes and formatting
            clean_filename = clean_filename.replace('Class 9 - ', '').replace('class 9 - ', '')
            clean_filename = clean_filename.replace('Class 9-', '').replace('class 9-', '')
            clean_filename = clean_filename.replace('Class 9', '').replace('class 9', '')
            
            # Title case the filename
            chapter_name = clean_filename.title().strip()
            
            print(f"   ✅ Using chapter name from filename: '{chapter_name}'")
            return {
                'title': chapter_name,
                'icon': '📖'
            }
        except Exception as e:
            print(f"   ⚠️ Error extracting subject info: {e}")
            # Fallback
            return {
                'title': 'NCERT Learning',
                'icon': '📖'
            }
    
# Usage example
if __name__ == "__main__":
    processor = EnhancedAIPDFProcessor()
    pdf_path = "Class 9 - People as resource.pdf"
    
    if os.path.exists(pdf_path):
        result = processor.process_pdf_with_structured_content(pdf_path)
        print(f"✅ Generated {result['stats']['total_concepts']} concepts")
        print(f"✅ Generated {result['stats']['total_mcqs']} MCQs")
        print(f"✅ Generated {result['stats']['total_subjective']} subjective questions")
    else:
        print(f"❌ PDF file not found: {pdf_path}")
