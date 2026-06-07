from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

HOME_URL = reverse('news:home')


def test_news_count(client, news_list):
    response = client.get(HOME_URL)
    assert response.context['object_list'].count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_list):
    response = client.get(HOME_URL)
    all_dates = [news.date for news in response.context['object_list']]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, comments, detail_url):
    response = client.get(detail_url)
    all_timestamps = [c.created for c in response.context['news'].comment_set.all()]
    assert all_timestamps == sorted(all_timestamps)


def test_anonymous_client_has_no_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, detail_url):
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
