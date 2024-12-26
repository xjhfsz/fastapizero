from http import HTTPStatus

from fastapizero.schemas import UserPublic


def test_read_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá, mundo!'}


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'usertest',
            'password': 'password',
            'email': 'user@test.com',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'usertest',
        'email': 'user@test.com',
        'id': 1,
    }


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.json() == {'users': [user_schema]}


def test_read_user(client, user):
    response = client.get(f'/users/{user.id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': user.username,
        'email': user.email,
        'id': user.id,
    }


def test_read_user_deve_retornar_not_found(client):
    response = client.get('/users/666')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found!'}


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'password': 'password',
            'username': 'bob',
            'email': 'bob@test.com',
            'id': user.id,
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@test.com',
        'id': user.id,
    }


def test_create_user_deve_retornar_400_se_usuario_ja_existe(client, user):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'email': 'novoemail@test.com',
            'password': 'password_test',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists!'}


def test_create_user_deve_retornar_400_se_email_ja_existe(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'new_user',
            'email': user.email,
            'password': 'password_test',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already exists!'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted!'}


def test_delete_user_should_return_unauthorized(client):
    response = client.delete('/users/666')
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_update_user_should_return_unauthorized(client):
    response = client.put(
        '/users/666',
        json={
            'username': 'user',
            'email': 'user@email.com',
            'password': 'password',
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_token(client, user):
    response = client.post(
        '/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )

    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_get_token_should_return_bas_request(client, user):
    response = client.post(
        '/token',
        data={
            'username': 'username',
            'password': 'password',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
