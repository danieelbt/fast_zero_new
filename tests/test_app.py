from http import HTTPStatus

from fast_zero.schemas import UserPublic


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
            'password': 'password'
        }
    )

    assert response.status_code == HTTPStatus.CREATED

    assert response.json() == {
        'id': 1,
        'username': 'test',
        'email': 'test@test.com'
    }


def test_create_user_username_already_exists(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'test',
            'email': 'email@email.com',
            'password': 'password'
        }
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_email_already_exists(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'test2',
            'email': 'test@test.com',
            'password': 'password'
        }
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

    assert response.json() == {
        'users': [user_schema]
    }


def test_read_one_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK

    assert response.json() == user_schema


def test_read_one_user_not_found(client):
    response = client.get('/users/100')

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json() == {'detail': 'User not found'}


def test_update_user(client, user):
    response = client.put(
        '/users/1',
        json={
            'username': 'testupdated',
            'email': 'test@updated.com',
            'password': 'passwordupdated'
        }
    )

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {
        'id': 1,
        'username': 'testupdated',
        'email': 'test@updated.com'
    }


def test_update_integrity_error(client, user):
    client.post(
        '/users',
        json={
            'username': 'jose',
            'email': 'jose@test.com',
            'password': 'testpassword'
        }
    )

    response_update = client.put(
        f'/users/{user.id}',
        json={
            'username': 'jose',
            'email': 'antonio@test.com',
            'password': 'testpassword'
        }
    )

    assert response_update.status_code == HTTPStatus.CONFLICT

    assert response_update.json() == {
        'detail': 'Username or email already exists'
    }


def test_update_user_not_found(client):
    response = client.put(
        '/users/1000',
        json={
            'username': 'testupdated',
            'email': 'test@updated.com',
            'password': 'passwordupdated'
        }
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json() == {'detail': 'User not found'}


def test_delete_user(client, user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK

    assert response.json() == {
        'message': 'User with id 1 has been deleted!'
    }


def test_delete_user_not_found(client):
    response = client.delete('/users/100')

    assert response.status_code == HTTPStatus.NOT_FOUND

    assert response.json() == {'detail': 'User not found'}
