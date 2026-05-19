import os
import PyPDF2
import docx
from anthropic import Anthropic
from django.shortcuts import render

# Initialise the Anthropic client
client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))


def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text


def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text


def extract_text_from_txt(file):
    return file.read().decode('utf-8')


def extract_text(file, filename):
    if filename.endswith('.pdf'):
        return extract_text_from_pdf(file)
    elif filename.endswith('.docx'):
        return extract_text_from_docx(file)
    elif filename.endswith('.txt'):
        return extract_text_from_txt(file)
    else:
        return None


def get_summary_from_claude(text):
    # Trim text to avoid hitting API limits
    trimmed_text = text[:10000]

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""You are a professional document summariser. 
                
Please analyse the following document and provide:

1. A clear and concise summary in 3 to 5 sentences
2. A list of exactly 5 key points from the document

Format your response exactly like this:
SUMMARY:
Your summary here

KEY POINTS:
- Key point 1
- Key point 2
- Key point 3
- Key point 4
- Key point 5

Here is the document:

{trimmed_text}"""
            }
        ]
    )

    # Extract the response text
    response_text = message.content[0].text

    # Split the response into summary and key points
    parts = response_text.split('KEY POINTS:')
    summary = parts[0].replace('SUMMARY:', '').strip()
    key_points_text = parts[1].strip()
    key_points = [
        point.replace('- ', '').strip()
        for point in key_points_text.split('\n')
        if point.strip()
    ]

    return summary, key_points

def summariser(request):
    summary = None
    key_points = []
    error = None

    if request.method == 'POST':
        uploaded_file = request.FILES.get('document')

        if not uploaded_file:
            error = 'Please upload a file.'
        else:
            text = extract_text(uploaded_file, uploaded_file.name)

            if not text:
                error = 'Sorry, we could not read that file type.'
            else:
                summary, key_points = get_summary_from_claude(text)

    return render(request, 'summariser/summariser.html', {
        'summary': summary,
        'key_points': key_points,
        'error': error,
    })

def documentation(request):
    return render(request, 'summariser/documentation.html')