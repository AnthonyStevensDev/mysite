import os
from django.shortcuts import render
from newsapi import NewsApiClient
from anthropic import Anthropic

# Initialise clients
newsapi = NewsApiClient(api_key=os.environ.get('NEWS_API_KEY'))
claude = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))


def load_blocked_terms():
    """Load blocked terms from file"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'blocked_terms.txt')
        with open(file_path, 'r') as f:
            return [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        print("blocked_terms.txt not found — no terms blocked")
        return []


def get_news_articles(keyword):
    """Fetch recent news articles for a keyword"""
    try:
        response = newsapi.get_everything(
            q=f'"{keyword}"',
            language='en',
            sort_by='publishedAt',
            page_size=10
        )
        return response.get('articles', [])
    except Exception as e:
        print(f"NewsAPI error: {e}")
        return []


def analyse_sentiment_with_claude(articles, keyword):
    """Send articles to Claude for sentiment analysis"""
    articles_text = ""
    for i, article in enumerate(articles[:10], 1):
        title = article.get('title', 'No title')
        description = article.get('description', 'No description')
        articles_text += f"{i}. {title}\n{description}\n\n"

    if not articles_text:
        return None

    message = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""You are a sentiment analysis expert. Analyse the sentiment of these news articles about "{keyword}".

For each article give it one of three labels: POSITIVE, NEGATIVE, or NEUTRAL.

Important rules:
- If an article is clearly not relevant to "{keyword}" label it as NEUTRAL and ignore it in your summary
- Only include genuinely relevant articles in your overall summary
- Base your sentiment scores only on articles that are actually about "{keyword}"

Then provide an overall summary.

Format your response EXACTLY like this:
SCORES:
positive: [number]
negative: [number]
neutral: [number]

SUMMARY:
Your 3-4 sentence summary of the overall sentiment here

Here are the articles:

{articles_text}"""
            }
        ]
    )

    return message.content[0].text


def parse_claude_response(response_text):
    """Extract scores and summary from Claude's response"""
    try:
        parts = response_text.split('SUMMARY:')
        scores_section = parts[0].replace('SCORES:', '').strip()
        summary = parts[1].strip() if len(parts) > 1 else ''

        scores = {'positive': 0, 'negative': 0, 'neutral': 0}
        for line in scores_section.split('\n'):
            line = line.strip()
            if line.startswith('positive:'):
                scores['positive'] = int(line.split(':')[1].strip())
            elif line.startswith('negative:'):
                scores['negative'] = int(line.split(':')[1].strip())
            elif line.startswith('neutral:'):
                scores['neutral'] = int(line.split(':')[1].strip())

        return scores, summary
    except Exception as e:
        print(f"Parse error: {e}")
        return {'positive': 0, 'negative': 0, 'neutral': 0}, ''


def sentiment(request):
    results = None
    keyword = None
    error = None
    FREE_USES = 3

    if request.method == 'POST':
        keyword = request.POST.get('keyword', '').strip()

        if not keyword:
            error = 'Please enter a keyword to analyse.'

        elif len(keyword) > 100:
            error = 'Search term is too long. Please use fewer than 100 characters.'
            keyword = None

        else:
            blocked_terms = load_blocked_terms()
            keyword_lower = keyword.lower()

            if any(term in keyword_lower for term in blocked_terms):
                error = 'That search term is not permitted. Please try a different keyword.'
                keyword = None

            else:
                if request.user.is_authenticated:
                    # Registered user — unlimited access
                    articles = get_news_articles(keyword)

                    if not articles:
                        error = f'No recent news articles found for "{keyword}". Try a different keyword.'
                    else:
                        claude_response = analyse_sentiment_with_claude(articles, keyword)

                        if claude_response:
                            scores, summary = parse_claude_response(claude_response)

                            if request.user.is_authenticated:
                                from accounts.models import UsageTracking
                                usage, created = UsageTracking.objects.get_or_create(
                                    user=request.user
                                )
                                usage.sentiment_uses += 1
                                usage.save()

                            total = scores['positive'] + scores['negative'] + scores['neutral']
                            if total > 0:
                                percentages = {
                                    'positive': round((scores['positive'] / total) * 100),
                                    'negative': round((scores['negative'] / total) * 100),
                                    'neutral': round((scores['neutral'] / total) * 100),
                                }
                            else:
                                percentages = {'positive': 0, 'negative': 0, 'neutral': 0}

                            results = {
                                'scores': scores,
                                'percentages': percentages,
                                'summary': summary,
                                'total': len([a for a in articles[:10] if a.get('title') and a.get('title') != '[Removed]']),
                                'articles': articles[:10],
                            }
                        else:
                            error = 'Could not analyse sentiment. Please try again.'

                else:
                    # Guest user — 3 free uses via session
                    session_uses = request.session.get('sentiment_uses', 0)

                    if session_uses >= FREE_USES:
                        from django.contrib import messages
                        messages.info(
                            request,
                            'You have used your 3 free sentiment analyses. Create a free account for unlimited access.'
                        )
                        from django.shortcuts import redirect
                        return redirect('/accounts/register')

                    articles = get_news_articles(keyword)

                    if not articles:
                        error = f'No recent news articles found for "{keyword}". Try a different keyword.'
                    else:
                        claude_response = analyse_sentiment_with_claude(articles, keyword)

                        if claude_response:
                            scores, summary = parse_claude_response(claude_response)
                            request.session['sentiment_uses'] = session_uses + 1

                            total = scores['positive'] + scores['negative'] + scores['neutral']
                            if total > 0:
                                percentages = {
                                    'positive': round((scores['positive'] / total) * 100),
                                    'negative': round((scores['negative'] / total) * 100),
                                    'neutral': round((scores['neutral'] / total) * 100),
                                }
                            else:
                                percentages = {'positive': 0, 'negative': 0, 'neutral': 0}

                            results = {
                                'scores': scores,
                                'percentages': percentages,
                                'summary': summary,
                                'total': len([a for a in articles[:10] if a.get('title') and a.get('title') != '[Removed]']),
                                'articles': articles[:10],
                            }
                        else:
                            error = 'Could not analyse sentiment. Please try again.'

    session_uses = request.session.get('sentiment_uses', 0)
    remaining = max(0, FREE_USES - session_uses)

    return render(request, 'sentiment/sentiment.html', {
        'results': results,
        'keyword': keyword,
        'error': error,
        'remaining': remaining,
        'is_authenticated': request.user.is_authenticated,
    })