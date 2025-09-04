#!/usr/bin/env python3
"""
🎨 HTML Generator for Enhanced AI-Powered Learning
Generates individual HTML pages and index page
"""

import json
from datetime import datetime

class HTMLGenerator:
    def __init__(self):
        pass
    
    def generate_html_content(self, content_data):
        """Generate complete HTML content for a single PDF"""
        # Extract data
        subject_info = content_data['subject_info']
        concepts = content_data['concepts']
        mcq_questions = content_data['mcq_questions']
        subjective_questions = content_data['subjective_questions']
        stats = content_data.get('stats', {
            'total_concepts': len(concepts),
            'total_mcqs': len(mcq_questions),
            'total_subjective': len(subjective_questions),
            'main_topics': 0,
            'total_subtopics': 0,
            'images_used': 0
        })
        
        # Generate HTML sections
        concepts_html = self._generate_concepts_html(concepts)
        mcq_html = self._generate_mcq_html(mcq_questions)
        subjective_html = self._generate_subjective_html(subjective_questions)
        
        # Convert to JSON for JavaScript
        concepts_json = json.dumps([{
            'title': concept['title'],
            'description': concept['description']
        } for concept in concepts], ensure_ascii=False)
        
        mcq_json = json.dumps(mcq_questions, ensure_ascii=False)
        subjective_json = json.dumps(subjective_questions, ensure_ascii=False)
        
        # Generate topic tree HTML
        topic_tree_html = self._generate_topic_tree_html({'concepts': concepts})
        
        # Fill template
        html_content = self.template.format(
            title=subject_info['title'],
            icon=subject_info['icon'],
            total_concepts=stats['total_concepts'],
            total_mcqs=len(mcq_questions),
            total_subjective=len(subjective_questions),
            topic_tree_html=topic_tree_html,
            concepts_html=concepts_html,
            mcq_html=mcq_html,
            subjective_html=subjective_html,
            concepts_json=concepts_json,
            mcq_json=mcq_json,
            subjective_json=subjective_json,
            timestamp=datetime.now().strftime("%B %d, %Y at %I:%M %p")
        )
        
        return html_content
    
    def generate_index_page(self, processed_pdfs):
        """Generate main index page with links to all PDF pages"""
        # Generate cards for each PDF
        pdf_cards = ""
        for pdf_info in processed_pdfs:
            pdf_cards += f"""
            <div class="pdf-card" onclick="window.open('output/{pdf_info['filename']}', '_blank')">
                <div class="pdf-icon">{pdf_info['icon']}</div>
                <div class="pdf-info">
                    <h3>{pdf_info['title']}</h3>
                    <p class="pdf-stats">
                        📚 {pdf_info['stats']['total_concepts']} Concepts • 
                        📝 {pdf_info['stats']['total_mcqs']} MCQs • 
                        💭 {pdf_info['stats']['total_subjective']} Subjective Qs
                    </p>
                    <p class="pdf-original">Original: {pdf_info['original_pdf']}</p>
                </div>
                <div class="pdf-arrow">→</div>
            </div>
            """
        
        # Fill index template
        index_content = self.index_template.format(
            total_pdfs=len(processed_pdfs),
            pdf_cards=pdf_cards,
            timestamp=datetime.now().strftime("%B %d, %Y at %I:%M %p")
        )
        
        return index_content
    
    def _generate_concepts_html(self, concepts):
        """Generate HTML for concepts section"""
        html = ""
        for i, concept in enumerate(concepts):
            html += f"""
            <div class="concept-card" id="concept-{i}">
                <div class="concept-title">
                    <span>{i+1}. {concept['title']}</span>
                    <span class="reading-indicator" id="indicator-{i}" style="display:none;">🔊</span>
                </div>
                <div class="concept-description" id="text-{i}">
                    {concept['description']}
                </div>
                <div class="concept-controls">
                    <button onclick="readConcept({i})" class="concept-btn">🔊 Read This Concept</button>
                    <button onclick="repeatConcept({i})" class="concept-btn">🔄 Repeat</button>
                    <span class="topic-name">{concept.get('topic', '')}</span>
                </div>
            </div>
            """
        return html
    
    def _generate_mcq_html(self, mcq_questions):
        """Generate HTML for MCQ section"""
        html = ""
        for mcq in mcq_questions:
            options_html = ""
            for i, option in enumerate(mcq['options']):
                options_html += f'<li class="mcq-option" onclick="selectMCQOption({mcq["id"]}, {i})"><span class="option-label">{chr(65+i)}.</span>{option}</li>'
            
            html += f"""
            <div class="mcq-card" data-question="{mcq['id']}" data-correct="{mcq['correct_answer']}">
                <div class="mcq-question">
                    Q{mcq['id']}: {mcq['question']}
                    <span class="mcq-marks">1 Mark</span>
                </div>
                <ul class="mcq-options">
                    {options_html}
                </ul>
                <div class="feedback"></div>
            </div>
            """
        return html
    
    def _generate_topic_tree_html(self, content_data):
        """Generate HTML for topic structure tree with concepts"""
        # Extract topic structure from concepts
        topics = {}
        for concept in content_data['concepts']:
            topic = concept.get('topic', '')
            if ' → ' in topic:
                main_topic, subtopic = topic.split(' → ', 1)
                if main_topic not in topics:
                    topics[main_topic] = {}
                if subtopic not in topics[main_topic]:
                    topics[main_topic][subtopic] = []
                topics[main_topic][subtopic].append(concept)
            else:
                if topic not in topics:
                    topics[topic] = {}
                if 'main' not in topics[topic]:
                    topics[topic]['main'] = []
                topics[topic]['main'].append(concept)
        
        html = ""
        for main_topic, subtopics in topics.items():
            html += f"""
            <div class="topic-item">
                <div class="main-topic">📖 {main_topic}</div>
                {self._generate_subtopics_with_concepts_html(subtopics)}
            </div>
            """
        return html
    
    def _generate_subtopics_with_concepts_html(self, subtopics):
        """Generate HTML for subtopics with their concepts"""
        if not subtopics:
            return ""
        
        subtopics_html = ""
        for subtopic_name, concepts in subtopics.items():
            if subtopic_name == 'main':
                # Main topic concepts
                subtopics_html += f'<div class="subtopic">└─ 📝 Main Topic</div>'
                for concept in concepts:
                    subtopics_html += f"""
                    <div class="concept-under-topic">
                        <div class="concept-header">
                            <div class="concept-title">• {concept['title']}</div>
                            <div class="concept-controls">
                                <button onclick="readSingleConcept('{concept['title']}', '{concept['description'].replace("'", "\\'")}')" class="concept-btn">🔊 Read</button>
                                <button onclick="repeatSingleConcept('{concept['title']}', '{concept['description'].replace("'", "\\'")}')" class="concept-btn">🔄 Repeat</button>
                            </div>
                        </div>
                        <div class="concept-description">{concept['description']}</div>
                    </div>
                    """
            else:
                # Subtopic with concepts
                subtopics_html += f'<div class="subtopic">└─ 📝 {subtopic_name}</div>'
                for concept in concepts:
                    subtopics_html += f"""
                    <div class="concept-under-topic">
                        <div class="concept-header">
                            <div class="concept-title">• {concept['title']}</div>
                            <div class="concept-controls">
                                <button onclick="readSingleConcept('{concept['title']}', '{concept['description'].replace("'", "\\'")}')" class="concept-btn">🔊 Read</button>
                                <button onclick="repeatSingleConcept('{concept['title']}', '{concept['description'].replace("'", "\\'")}')" class="concept-btn">🔄 Repeat</button>
                            </div>
                        </div>
                        <div class="concept-description">{concept['description']}</div>
                    </div>
                    """
        
        return f'<div class="subtopics">{subtopics_html}</div>'
    
    def _generate_subjective_html(self, subjective_questions):
        """Generate HTML for subjective questions section"""
        html = ""
        for question in subjective_questions:
            important_tag = '<span class="important-tag">IMPORTANT</span>' if question.get('important', False) else ''
            marks = question.get('marks', '3 Marks')
            html += f"""
            <div class="subjective-card" data-question="{question['id']}">
                <div class="subjective-question">
                    Q{question['id']}: {question['question']} {important_tag}
                    <span class="subjective-marks">{marks}</span>
                </div>
                <button class="toggle-btn" onclick="toggleAnswer({question['id']})">Show Answer</button>
                <div class="subjective-answer" data-answer="{question['id']}">
                    <strong>Answer:</strong><br>
                    {question['answer'].replace(chr(10), '<br>')}
                </div>
            </div>
            """
        return html
    
    # HTML template for individual PDF pages
    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📚</text></svg>">
    <title>{title} - Interactive Learning</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .header-top {{
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            margin-bottom: 20px;
        }}
        
        .home-btn {{
            position: absolute;
            left: 0;
            background: linear-gradient(45deg, #10b981, #059669);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        }}
        
        .home-btn:hover {{
            background: linear-gradient(45deg, #059669, #047857);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .controls {{
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }}
        
        .btn {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            margin: 5px;
            transition: transform 0.2s;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
        }}
        
        .stat {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px 25px;
            border-radius: 15px;
            text-align: center;
            min-width: 120px;
        }}
        
        .stat .number {{
            font-size: 1.8em;
            font-weight: bold;
            display: block;
        }}
        
        .tabs {{
            display: flex;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 5px;
            margin-bottom: 30px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }}
        
        .tab {{
            flex: 1;
            padding: 15px 20px;
            text-align: center;
            cursor: pointer;
            border-radius: 10px;
            transition: all 0.3s ease;
            font-weight: 500;
        }}
        
        .tab.active {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            transform: translateY(-2px);
        }}
        
        .content {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .concept-card {{
            background: white;
            margin: 20px 0;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border-left: 5px solid #667eea;
            position: relative;
        }}
        
        .concept-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.15);
        }}
        
        .concept-card.reading {{
            background: linear-gradient(135deg, #fef7cd, #fef3c7);
            border-left-color: #f59e0b;
            transform: scale(1.02);
        }}
        
        .concept-title {{
            font-size: 1.3em;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .concept-description {{
            font-size: 1.1em;
            line-height: 1.7;
            color: #374151;
            margin-bottom: 20px;
        }}
        
        .concept-controls {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .topic-name {{
            color: #6b7280;
            font-size: 0.9em;
            font-style: italic;
            margin-left: 10px;
            background: #f3f4f6;
            padding: 4px 8px;
            border-radius: 12px;
            border-left: 3px solid #667eea;
        }}
        
        .concept-btn {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .concept-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        
        .reading-indicator {{
            color: #f59e0b;
            font-size: 1.2em;
        }}
        
        .mcq-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            position: relative;
        }}
        
        .mcq-question {{
            font-size: 1.2em;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 20px;
            line-height: 1.5;
        }}
        
        .mcq-marks {{
            background: #3b82f6;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 12px;
            float: right;
            margin-left: 10px;
        }}
        
        .mcq-options {{
            list-style: none;
            margin-bottom: 20px;
        }}
        
        .mcq-option {{
            background: #f8fafc;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
        }}
        
        .mcq-option:hover {{
            background: #e2e8f0;
            border-color: #cbd5e1;
        }}
        
        .mcq-option.selected {{
            background: #dbeafe;
            border-color: #3b82f6;
            color: #1e40af;
        }}
        
        .mcq-option.correct {{
            background: #dcfce7;
            border-color: #16a34a;
            color: #15803d;
        }}
        
        .mcq-option.incorrect {{
            background: #fee2e2;
            border-color: #dc2626;
            color: #b91c1c;
        }}
        
        .feedback {{
            margin-top: 15px;
            padding: 15px;
            border-radius: 10px;
            font-weight: 600;
            display: none;
        }}
        
        .feedback.correct {{
            background: #dcfce7;
            color: #15803d;
            border: 2px solid #16a34a;
        }}
        
        .feedback.incorrect {{
            background: #fee2e2;
            color: #b91c1c;
            border: 2px solid #dc2626;
        }}
        
        .subjective-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        
        .subjective-question {{
            font-size: 1.2em;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 20px;
            line-height: 1.5;
        }}
        
        .subjective-marks {{
            background: #10b981;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 12px;
            float: right;
            margin-left: 10px;
        }}
        
        .important-tag {{
            background: #f59e0b;
            color: white;
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 10px;
            font-weight: bold;
            margin-left: 10px;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
            100% {{ opacity: 1; }}
        }}
        
        .toggle-btn {{
            background: linear-gradient(45deg, #10b981, #059669);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .toggle-btn:hover {{
            background: linear-gradient(45deg, #059669, #047857);
            transform: translateY(-2px);
        }}
        
        .subjective-answer {{
            display: none;
            margin-top: 20px;
            padding: 20px;
            background: #f8fafc;
            border-radius: 10px;
            border-left: 4px solid #10b981;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 4px;
            margin: 20px 0;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(45deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.3s ease;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: white;
            font-size: 0.9em;
        }}
        
        .topic-structure {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}
        
        .topic-structure h3 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.4em;
        }}
        
        .topic-tree {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        
        .topic-item {{
            border-left: 3px solid #667eea;
            padding-left: 15px;
        }}
        
        .main-topic {{
            font-weight: 600;
            color: #1f2937;
            font-size: 1.1em;
            margin-bottom: 8px;
        }}
        
        .subtopics {{
            margin-left: 20px;
        }}
        
        .subtopic {{
            color: #6b7280;
            font-size: 0.95em;
            margin-bottom: 5px;
            padding-left: 10px;
        }}
        
        .concept-under-topic {{
            margin-left: 30px;
            margin-bottom: 15px;
            padding: 15px;
            background: #f8fafc;
            border-radius: 8px;
            border-left: 3px solid #10b981;
        }}
        
        .concept-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .concept-controls {{
            display: flex;
            gap: 8px;
        }}
        
        .concept-btn {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 15px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .concept-btn:hover {{
            background: linear-gradient(45deg, #5a67d8, #6b46c1);
            transform: translateY(-1px);
        }}
        
        .concept-under-topic .concept-title {{
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 8px;
            font-size: 1em;
        }}
        
        .concept-under-topic .concept-description {{
            color: #4b5563;
            line-height: 1.5;
            font-size: 0.9em;
        }}
        
        .concept-under-topic.reading {{
            background: #dbeafe;
            border-left-color: #3b82f6;
            transform: scale(1.02);
            transition: all 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-top">
                <button onclick="window.open('../index.html', '_self')" class="home-btn">🏠 Home</button>
                <h1>{icon} {title}</h1>
            </div>
            <div class="stats">
                <div class="stat">
                    <span class="number">{total_concepts}</span>
                    <span class="label">Concepts</span>
                </div>
                <div class="stat">
                    <span class="number">{total_mcqs}</span>
                    <span class="label">MCQ Questions</span>
                </div>
                <div class="stat">
                    <span class="number">{total_subjective}</span>
                    <span class="label">Subjective Qs</span>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <button onclick="readAllConcepts()" class="btn" id="readAllBtn">🔊 Read All Concepts</button>
            <button onclick="stopReading()" class="btn" id="stopBtn">⏹️ Stop Reading</button>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" id="progressFill"></div>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="showTab('concepts')">🎯 Key Concepts</div>
            <div class="tab" onclick="showTab('mcq')">📝 MCQ Quiz</div>
            <div class="tab" onclick="showTab('subjective')">💭 Subjective Q&A</div>
        </div>
        
        <div class="content">
            <div id="concepts" class="tab-content active">
                <div class="topic-structure">
                    <h3>📚 Topic Structure</h3>
                    <div class="topic-tree">
                        {topic_tree_html}
                    </div>
                </div>
            </div>
            
            <div id="mcq" class="tab-content">
                {mcq_html}
            </div>
            
            <div id="subjective" class="tab-content">
                {subjective_html}
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>📚 Interactive Learning Content • {timestamp}</p>
        <p>🎓 Enhanced AI-Powered Learning</p>
    </div>
    
    <script>
        let currentSpeech = null;
        let currentConceptIndex = 0;
        let isReading = false;
        let allConcepts = {concepts_json};
        let allMCQs = {mcq_json};
        let allSubjective = {subjective_json};
        
        // Set default voice to Google UK English Female
        let defaultVoice = null;
        
        // Check if browser supports speech synthesis
        if (!('speechSynthesis' in window)) {{
            alert('Your browser does not support text-to-speech. Please use Chrome, Firefox, or Safari.');
        }}
        
        function loadVoices() {{
            const voices = speechSynthesis.getVoices();
            
            // Find Google UK English Female voice
            defaultVoice = voices.find(voice => 
                voice.name.includes('Google UK English Female') && voice.lang === 'en-GB'
            );
            
            // Fallback to any UK English voice if Google UK English Female not found
            if (!defaultVoice) {{
                defaultVoice = voices.find(voice => 
                    voice.lang === 'en-GB'
                );
            }}
            
            // Fallback to any English voice if UK English not found
            if (!defaultVoice) {{
                defaultVoice = voices.find(voice => 
                    voice.lang.startsWith('en')
                );
            }}
        }}
        
        speechSynthesis.onvoiceschanged = loadVoices;
        loadVoices();
        
        function showTab(tabName) {{
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => {{
                content.classList.remove('active');
            }});
            
            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }}
        
        // Reading functions
        function readConcept(index) {{
            if (isReading && currentConceptIndex !== index) {{
                stopReading();
            }}
            
            currentConceptIndex = index;
            isReading = true;
            
            for (let i = 0; i < allConcepts.length; i++) {{
                highlightConcept(i, false);
            }}
            
            highlightConcept(index, true);
            updateProgress();
            
            const concept = allConcepts[index];
            const textToRead = `${{concept.title}}. ${{concept.description}}`;
            
            readText(textToRead, () => {{
                highlightConcept(index, false);
                isReading = false;
                if (currentConceptIndex === allConcepts.length - 1) {{
                    document.getElementById('progressFill').style.width = '100%';
                }}
            }});
        }}
        
        function readAllConcepts() {{
            if (allConcepts.length === 0) return;
            
            currentConceptIndex = 0;
            isReading = true;
            
            function readNext() {{
                if (currentConceptIndex >= allConcepts.length) {{
                    isReading = false;
                    document.getElementById('progressFill').style.width = '100%';
                    return;
                }}
                
                readConcept(currentConceptIndex);
                currentSpeech.onend = () => {{
                    highlightConcept(currentConceptIndex, false);
                    currentConceptIndex++;
                    if (currentConceptIndex < allConcepts.length) {{
                        setTimeout(readNext, 1500);
                    }} else {{
                        isReading = false;
                        document.getElementById('progressFill').style.width = '100%';
                    }}
                }};
            }}
            
            readNext();
        }}
        
        function highlightConcept(index, highlight = true) {{
            const conceptElements = document.querySelectorAll('.concept-under-topic');
            if (conceptElements[index]) {{
                if (highlight) {{
                    conceptElements[index].classList.add('reading');
                    conceptElements[index].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                }} else {{
                    conceptElements[index].classList.remove('reading');
                }}
            }}
        }}
        
        function readText(text, onEnd = null) {{
            if (currentSpeech) {{
                speechSynthesis.cancel();
            }}
            
            currentSpeech = new SpeechSynthesisUtterance(text);
            currentSpeech.rate = 0.85;
            currentSpeech.pitch = 1.0;
            currentSpeech.volume = 1.0;
            
            // Use default voice if available
            if (defaultVoice) {{
                currentSpeech.voice = defaultVoice;
            }}
            
            currentSpeech.onend = () => {{
                if (onEnd) onEnd();
            }};
            
            speechSynthesis.speak(currentSpeech);
        }}
        
        function repeatConcept(index) {{
            readConcept(index);
        }}
        
        function readSingleConcept(title, description) {{
            const textToRead = `${{title}}. ${{description}}`;
            readText(textToRead);
        }}
        
        function repeatSingleConcept(title, description) {{
            const textToRead = `${{title}}. ${{description}}`;
            readText(textToRead);
        }}
        
        function stopReading() {{
            if (currentSpeech) {{
                speechSynthesis.cancel();
            }}
            
            for (let i = 0; i < allConcepts.length; i++) {{
                highlightConcept(i, false);
            }}
            
            isReading = false;
        }}
        
        function updateProgress() {{
            if (allConcepts.length > 0) {{
                const progress = (currentConceptIndex / allConcepts.length) * 100;
                document.getElementById('progressFill').style.width = progress + '%';
            }}
        }}
        
        // MCQ functions
        function selectMCQOption(questionId, optionIndex) {{
            const question = document.querySelector(`[data-question="${{questionId}}"]`);
            const options = question.querySelectorAll('.mcq-option');
            const correctAnswer = parseInt(question.getAttribute('data-correct'));
            const feedback = question.querySelector('.feedback');
            
            // Remove previous selections
            options.forEach(option => option.classList.remove('selected', 'correct', 'incorrect'));
            
            // Mark selected option
            options[optionIndex].classList.add('selected');
            
            // Check if correct and show feedback
            if (optionIndex === correctAnswer) {{
                options[optionIndex].classList.add('correct');
                feedback.textContent = '✅ Correct! Well done!';
                feedback.className = 'feedback correct';
            }} else {{
                options[optionIndex].classList.add('incorrect');
                options[correctAnswer].classList.add('correct');
                feedback.textContent = '❌ Incorrect. The correct answer is highlighted in green.';
                feedback.className = 'feedback incorrect';
            }}
            
            feedback.style.display = 'block';
            
            // Disable all options after selection
            options.forEach(option => {{
                option.style.cursor = 'default';
                option.onclick = null;
            }});
        }}
        
        function toggleAnswer(questionId) {{
            const answer = document.querySelector(`[data-answer="${{questionId}}"]`);
            if (answer.style.display === 'block') {{
                answer.style.display = 'none';
            }} else {{
                answer.style.display = 'block';
            }}
        }}
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {{
            if (e.key === ' ' && e.ctrlKey) {{
                e.preventDefault();
                if (isReading) {{
                    stopReading();
                }} else {{
                    readAllConcepts();
                }}
            }} else if (e.key === 'Escape') {{
                stopReading();
            }}
        }});
    </script>
</body>
</html>"""
    
    # Index page template
    index_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📚</text></svg>">
    <title>Disha's Learning System - Index</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            font-size: 3em;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            color: #7f8c8d;
            margin-bottom: 20px;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
        }}
        
        .stat {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px 30px;
            border-radius: 15px;
            text-align: center;
            min-width: 150px;
        }}
        
        .stat .number {{
            font-size: 2em;
            font-weight: bold;
            display: block;
        }}
        
        .pdf-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .pdf-card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        
        .pdf-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        }}
        
        .pdf-icon {{
            font-size: 3em;
            min-width: 60px;
            text-align: center;
        }}
        
        .pdf-info {{
            flex: 1;
        }}
        
        .pdf-info h3 {{
            font-size: 1.3em;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .pdf-stats {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        
        .pdf-original {{
            color: #95a5a6;
            font-size: 0.8em;
            font-style: italic;
        }}
        
        .pdf-arrow {{
            font-size: 1.5em;
            color: #667eea;
            font-weight: bold;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: white;
            font-size: 0.9em;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Enhanced AI-Powered Learning</h1>
            <p>Interactive Learning Content Generated Using Azure OpenAI GPT-4o</p>
            <div class="stats">
                <div class="stat">
                    <span class="number">{total_pdfs}</span>
                    <span class="label">PDF Documents</span>
                </div>
            </div>
        </div>
        
        <div class="pdf-grid">
            {pdf_cards}
        </div>
    </div>
    
    <div class="footer">
        <p>🎓 Interactive Learning Content published at • {timestamp}</p>
    </div>
</body>
</html>"""
