from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', lf('news_pk_for_args')),
        ('users:login', None),
        ('users:signup', None),
        ('users:logout', None),
    )
)
def test_pages_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    if name == 'users:logout':
        response = client.post(url)
        assert response.status_code == HTTPStatus.OK
    else:
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('reader_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK),
    )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, name, comment, expected_status
):
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lf('comment_pk_for_args')),
        ('news:delete', lf('comment_pk_for_args')),
    )
)
def test_redirect_for_anonymous_client(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    response = client.get(url)
    assertRedirects(response, f'{login_url}?next={url}')
