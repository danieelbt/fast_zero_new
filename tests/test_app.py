from http import HTTPStatus

from fast_zero.schemas import UserPublic
from fast_zero.security import create_access_token


def test_read_root(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {'message': 'Hello World!'}


def test_create_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'test',
            'email': 'test@test.com',
            'password': 'password',
        },
    )

    assert response.status_code == HTTPStatus.CREATED

    assert response.json() == {
        'id': 1,
        'username': 'test',
        'email': 'test@test.com',
    }


def test_create_user_username_already_exists(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'test',
            'email': 'email@email.com',
            'password': 'password',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_email_already_exists(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'test2',
            'email': 'test@test.com',
            'password': 'password',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert response.json() == {'detail': 'Email already exists'}


def test_read_users_without_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {'users': [user_schema]}


def test_read_one_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK

    assert response.json() == user_schema


def test_read_one_user_not_found(client):
    response = client.get('/users/100')

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json() == {'detail': 'User not found'}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'testupdated',
            'email': 'test@updated.com',
            'password': 'passwordupdated',
        },
    )

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {
        'id': 1,
        'username': 'testupdated',
        'email': 'test@updated.com',
    }


def test_update_user_not_enough_permission(client, user, token):
    response = client.put(
        '/users/100',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'testupdated',
            'email': 'test@updated.com',
            'password': 'passwordupdated'
        }
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {
        'detail': 'Not enough permission'
    }


def test_update_integrity_error(client, user, token):
    client.post(
        '/users',
        json={
            'username': 'jose',
            'email': 'jose@test.com',
            'password': 'testpassword',
        },
    )

    response_update = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'jose',
            'email': 'antonio@test.com',
            'password': 'testpassword',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT

    assert response_update.json() == {
        'detail': 'Username or email already exists'
    }


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {'message': 'User with id 1 has been deleted!'}


def test_delete_user_not_enough_permission(client, user, token):
    response = client.delete(
        '/users/100',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN

    assert response.json() == {
        'detail': 'Not enough permission'
    }


def test_get_token(client, user):
    response = client.post(
        '/token',
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
        '/token',
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
        '/token',
        data={
            'username': 'wrong username',
            'password': user.clean_password,
        }
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'detail': 'Incorrect username or password'
    }


def test_jwt_invalid_token(client, user):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': 'Bearer invalid-token'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    assert response.json() == {
        'detail': 'Could not validate credentials'
    }


def test_get_current_user_username_not_found(client):
    data = {'naosouumsub': 'naosouumsubject'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    assert response.json() == {
        'detail': 'Could not validate credentials'
    }


def test_get_current_user_doesnt_exists(client):
    data = {'sub': 'naoexistonobanco@test.com'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    assert response.json() == {
        'detail': 'Could not validate credentials'
    }
