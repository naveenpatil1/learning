# Interactive Learning System

An AI-powered PDF learning system that converts NCERT textbooks into interactive learning experiences.

## Features

- 🤖 **AI-Powered Processing**: Uses Azure OpenAI GPT-4 to extract concepts, generate MCQs, and create subjective questions
- 📚 **Topic Structure**: Hierarchical organization of main topics and subtopics
- 🔊 **Text-to-Speech**: Read concepts aloud with individual and bulk reading options
- 📝 **Interactive MCQs**: Auto-submit with immediate feedback
- 💭 **Subjective Q&A**: Comprehensive questions with answers and importance tags
- 🏠 **Easy Navigation**: Home button to return to main index

## How to Use

1. Upload PDF files to the `pdfs/` directory
2. Run `python parallel_pdf_processor.py` to process all PDFs
3. Access the generated HTML pages through `index.html`

## Technology Stack

- **Backend**: Python with Azure OpenAI API
- **Frontend**: HTML, CSS, JavaScript
- **PDF Processing**: pdfplumber, PyMuPDF
- **AI Integration**: GPT-4o with Vision capabilities

## Live Demo

Visit: [https://naveenpatil1.github.io/InteractiveLearning/](https://naveenpatil1.github.io/InteractiveLearning/)

## License

MIT License
