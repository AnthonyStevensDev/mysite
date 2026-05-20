from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.models import UsageTracking
import os
import PyPDF2
import docx
from anthropic import Anthropic

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

    response_text = message.content[0].text
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
    FREE_USES = 3

    # Check usage limits
    if request.method == 'POST':
        uploaded_file = request.FILES.get('document')

        if not uploaded_file:
            error = 'Please upload a file.'
        else:
            # Check if user is authenticated
            if request.user.is_authenticated:
                # Registered user — get or create their usage record
                usage, created = UsageTracking.objects.get_or_create(
                    user=request.user
                )
                # Registered users have unlimited access
                text = extract_text(uploaded_file, uploaded_file.name)
                if not text:
                    error = 'Sorry, we could not read that file type.'
                else:
                    summary, key_points = get_summary_from_claude(text)
                    usage.summariser_uses += 1
                    usage.save()

            else:
                # Guest user — track uses in session
                session_uses = request.session.get('summariser_uses', 0)

                if session_uses >= FREE_USES:
                    # Redirect to register page with a message
                    messages.info(
                        request,
                        'You have used your 3 free summarisations. Create a free account for unlimited access.'
                    )
                    return redirect('/accounts/register')

                text = extract_text(uploaded_file, uploaded_file.name)
                if not text:
                    error = 'Sorry, we could not read that file type.'
                else:
                    summary, key_points = get_summary_from_claude(text)
                    request.session['summariser_uses'] = session_uses + 1

    # Work out remaining free uses for guests
    session_uses = request.session.get('summariser_uses', 0)
    remaining = max(0, FREE_USES - session_uses)

    return render(request, 'summariser/summariser.html', {
        'summary': summary,
        'key_points': key_points,
        'error': error,
        'remaining': remaining,
        'is_authenticated': request.user.is_authenticated,
    })


