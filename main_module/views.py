from django.shortcuts import *
from bs4 import BeautifulSoup
import requests
from newspaper import Article
import os
import google.generativeai as genai
from duckduckgo_search import DDGS

def extract_text_from_url(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text

def analyze_article(text):
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    Analyze the following article text:

    {text}

    Provide your analysis in the following format:
    
    Claims:
    1. [Claim 1]
    2. [Claim 2]
    3. [Claim 3]

    Biases:
    1. [Bias 1]
    2. [Bias 2]

    Overall Neutrality: [Positive/Neutral/Negative]

    Justify the neutrality assessment in one sentence.
    """
    
    response = model.generate_content(prompt)
    return response.text

def generate_search_queries(claims, support=True):
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    Given the following claims from an article:

    {claims}

    Generate 3 search query suggestions to find articles that {'support' if support else 'do not support'} these claims.
    Format each as:
    1. [Search query 1]
    2. [Search query 2]
    3. [Search query 3]

    Ensure the queries are specific and relevant to the claims.
    """
    
    response = model.generate_content(prompt)
    return response.text


def ddg_search(query, num_results=5):
    with DDGS() as ddgs:
        results = [r['href'] for r in ddgs.text(query, max_results=num_results)]
    return results

def clean_queries(queries):
    if queries is None:
        return ""
    lines = queries.splitlines()
    cleaned = [line.split(". ", 1)[1].replace("*", "").strip() for line in lines if ". " in line]
    return "\n".join(cleaned)

def extract_analysis_components(analysis):
    try:
        claims_start = analysis.index("**Claims:**") + len("**Claims:**")
        biases_start = analysis.index("**Biases:**")
        neutrality_start = analysis.index("**Overall Neutrality:**")

        claims = analysis[claims_start:biases_start].strip()
        biases = analysis[biases_start + len("**Biases:**"):neutrality_start].strip()
        neutrality_section = analysis[neutrality_start + len("**Overall Neutrality:**"):].strip()

        # Split neutrality and justification
        neutrality_parts = neutrality_section.split("\n", 1)
        overall_neutrality = neutrality_parts[0].strip()
        justification = neutrality_parts[1].strip() if len(neutrality_parts) > 1 else ""

    except ValueError as e:
        print(f"Error: {e}")
        return None, None, None, None

    return claims, biases, overall_neutrality, justification




def search_view(request):
    return render(request, 'main_module/search.html')
    # return HttpResponse('hello')



def search_results(request):
    querylink = request.GET.get('query', '')
    genai.configure(api_key="AIzaSyAlGi5JFMx1KYPbsw2RvIVaFVHXMKRQ37o")

    
    # Process the query
    article_text = extract_text_from_url(querylink)
    analysis = analyze_article(article_text)

    claims, biases, overall_neutrality, justification = extract_analysis_components(analysis)
    claims = clean_queries(claims)
    biases = clean_queries(biases)
    
    print(analysis)

    supporting_queries = clean_queries(generate_search_queries(claims, support=True))
    opposing_queries = clean_queries(generate_search_queries(claims, support=False))

    # Initialize dictionaries to store URLs
    supporting_articles = {}
    opposing_articles = {}

    # Search for supporting articles
    for i, query in enumerate(supporting_queries.split('\n'), start=1):
        if query.strip():
            urls = ddg_search(query)
            supporting_articles[f"Query {i}"] = {
                'query': query,
                'urls': urls
            }

    # Search for opposing articles
    for i, query in enumerate(opposing_queries.split('\n'), start=1):
        if query.strip():
            urls = ddg_search(query)
            opposing_articles[f"Query {i}"] = {
                'query': query,
                'urls': urls
            }
    # Pass data to the template
    context = {
        'query': querylink,
        'analysis': analysis,
        'claims': claims,
        'biases' : biases,
        'overall_neutrality' : overall_neutrality,
        'justification': justification,
        'supporting_articles': supporting_articles,
        'opposing_articles': opposing_articles
    }

    return render(request, 'main_module/search_results.html', context)


