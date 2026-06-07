from http import HTTPStatus

from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'
FORM_DATA = {'text': COMMENT_TEXT}
NEW_FORM_DATA = {'text': NEW_COMMENT_TEXT}


def test_anonymous_user_cant_create_comment(client, detail_url):
    client.post(detail_url, data=FORM_DATA)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, detail_url, url_to_comments, author, news):
    response = author_client.post(detail_url, data=FORM_DATA)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, ещё текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assert Comment.objects.count() == 0
    form = response.context['form']
    assert form.errors['text'] == [WARNING]


def test_author_can_delete_comment(author_client, delete_url, url_to_comments):
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(reader_client, delete_url):
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, edit_url, url_to_comments, comment):
    response = author_client.post(edit_url, data=NEW_FORM_DATA)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(reader_client, edit_url, comment):
    response = reader_client.post(edit_url, data=NEW_FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
