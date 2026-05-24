from django.shortcuts import render, get_object_or_404
from .models import Article
from django.db.models import Count, Q
import datetime as dt

def article_list(request):
    """
    A view that retrieves all articles from the database, calculates stage
    counts, and passes them to a template for rendering.
    """
    # Check if the request is for resetting a specific vote section
    if request.headers.get('Hx-Request') and 'article_id' in request.GET:
        try:
            article_id = int(request.GET.get('article_id'))
            article = get_object_or_404(Article, pk=article_id)
            return render(request, 'news/_voting_section.html', {'article': article})
        except (ValueError, TypeError):
            # Handle cases where article_id is not a valid integer
            pass

    articles = Article.objects.all()
    
    # Define the fixed stages
    fixed_stages = [
        "Vireilletulo", "Lähetekeskustelu", "Valiokuntakäsittely", 
        "Mietinnön pöydällepano", "Ensimmäinen käsittely", "Toinen käsittely", 
        "Eduskunnan vastaus", "Säädöskokoelma"
    ]

    # Get the counts of articles in each stage
    stage_counts = Article.objects.values('stage_fi').annotate(count=Count('id')).order_by()
    
    # Create a dictionary for easy lookup
    counts_dict = {item['stage_fi']: item['count'] for item in stage_counts}

    # Build the final list of stages with their counts
    stage_summaries = []
    for stage in fixed_stages:
        stage_summaries.append({
            'stage_name': stage,
            'article_count': counts_dict.get(stage, 0)
        })

    context = {
        'articles': articles,
        'stage_summaries': stage_summaries,
    }
    return render(request, 'news/article_list.html', context)

def vote(request, article_id, vote_type):
    
    article = get_object_or_404(Article, id=article_id)
    
    # Get the user's vote history from the session
    user_votes = request.session.get('user_votes', {})
    previous_vote = user_votes.get(str(article_id))

    # If the user has voted before on this article, decrement the old vote count
    if previous_vote:
        if previous_vote == 'yes':
            article.votes_yes -= 1
        elif previous_vote == 'no':
            article.votes_no -= 1
        elif previous_vote == 'undecided':
            article.votes_undecided -= 1

    # Increment the new vote count
    if vote_type == 'yes':
        article.votes_yes += 1
    elif vote_type == 'no':
        article.votes_no += 1
    elif vote_type == 'undecided':
        article.votes_undecided += 1
        
    # Update the user's vote history in the session
    user_votes[str(article_id)] = vote_type
    request.session['user_votes'] = user_votes

    # Recalculate total votes
    total_votes = article.votes_yes + article.votes_undecided + article.votes_no

    if total_votes > 0:
        pct_yes = int((article.votes_yes / total_votes) * 100)
        pct_undecided = int((article.votes_undecided / total_votes) * 100)
        pct_no = int((article.votes_no / total_votes) * 100)

        # Distribute rounding errors
        remainder = 100 - (pct_yes + pct_undecided + pct_no)
        if remainder > 0:
            if pct_yes > 0: pct_yes += remainder
            elif pct_undecided > 0: pct_undecided += remainder
            else: pct_no += remainder
        
        article.pct_yes = pct_yes
        article.pct_undecided = pct_undecided
        article.pct_no = pct_no
    else: 
        article.pct_yes, article.pct_undecided, article.pct_no = 0, 0, 0

    article.last_voted_at = dt.datetime.now()
    article.total_votes = total_votes

    article.save()

    context = {
        'article': article,
        'user_vote_type': vote_type,
    }

    return render(request, 'news/_voted_section.html', context)

def search_results(request):
    query = request.POST.get('search', '')
    articles = Article.objects.none()

    if query:
        # Search in tags (exact match first)
        articles_by_tags = Article.objects.filter(tags__icontains=query).distinct()

        # Search in subject (Finnish, Swedish, English)
        articles_by_subject = Article.objects.filter(
            Q(subject_fi__icontains=query) |
            Q(subject_sv__icontains=query) |
            Q(subject_en__icontains=query)
        ).distinct()

        # Search in raw content
        articles_by_content = Article.objects.filter(raw_content__icontains=query).distinct()

        # Combine results, prioritizing tags, then subject, then content
        combined_articles = list(articles_by_tags) + list(articles_by_subject) + list(articles_by_content)
        # Remove duplicates while preserving order of first appearance
        seen = set()
        articles = []
        for article in combined_articles:
            if article.pk not in seen:
                articles.append(article)
                seen.add(article.pk)

        # Debug: If no articles found, add a dummy one to force expansion
        if not articles:
            from django.utils import timezone
            dummy_source = Article.objects.first().source if Article.objects.exists() else None
            if dummy_source:
                dummy_article = Article(
                    id=0,  # Use a dummy ID or handle appropriately in template
                    title_fi=f"Dummy Result for '{query}'",
                    subject_fi=f"This is a dummy subject for '{query}'",
                    source_url="#",
                    source=dummy_source,
                    raw_content="Dummy content",
                    created_at=timezone.now(),
                    updated_at=timezone.now()
                )
                articles.append(dummy_article)

    context = {
        'articles': articles,
        'query': query,
    }
    return render(request, 'news/search_results.html', context)

def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    context = {
        'article': article
    }
    return render(request, 'news/article_detail.html', context)