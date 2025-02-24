from http import HTTPStatus


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.username,
            'password': user.clean_password,
        }
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert token['token_type']  # Jeito simples de verificar
    assert 'access_token' in token  # // verboso de verificar


def test_get_token_incorrect_password(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.username,
            'password': 'wrong password',
        }
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'detail': 'Incorrect username or password'
    }


def test_get_token_incorrect_username(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': 'wrong username',
            'password': user.clean_password,
        }
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'detail': 'Incorrect username or password'
    }
