from http import HTTPStatus

from fastapizero.models import Todo, TodoState
from tests.conftest import TodoFactory


# test_create_todo
def test_create_todo(client, token, mock_db_time):
    with mock_db_time(model=Todo) as time:
        response = client.post(
            '/todos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test',
                'description': 'Test',
                'state': 'Draft',
            },
        )

    assert response.json() == {
        'id': 1,
        'title': 'Test',
        'description': 'Test',
        'state': 'Draft',
        'user_id': 1,
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


# test_list_todos
def test_list_todos_should_return_n_elements(session, client, user, token):
    n_elements = 7
    session.bulk_save_objects(
        TodoFactory.create_batch(n_elements, user_id=user.id)
    )
    session.commit()
    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == n_elements


def test_list_todos_pagination_should_return_n_elements(
    session, client, user, token
):
    # variáveis
    offset = 1
    n_elements = 2

    # building objects
    session.bulk_save_objects(TodoFactory.create_batch(7, user_id=user.id))
    session.commit()
    response = client.get(
        f'/todos/?offset={offset}&limit={n_elements}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert len(response.json()['todos']) == n_elements


def test_list_todos_filter_title_should_return_n_elements(
    session, client, user, token
):
    # variáveis
    n_elements = 5
    title = 'Test Todo'

    # building objects
    session.bulk_save_objects(
        TodoFactory.create_batch(n_elements, user_id=user.id, title=title)
    )
    session.commit()
    response = client.get(
        f'/todos/?title={title}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert len(response.json()['todos']) == n_elements


def test_list_todos_filter_description_should_return_n_elements(
    session, client, user, token
):
    # variáveis
    n_elements = 5
    desc = 'description test'

    # building objects
    session.bulk_save_objects(
        TodoFactory.create_batch(n_elements, user_id=user.id, description=desc)
    )
    session.commit()
    response = client.get(
        '/todos/?description=desc',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert len(response.json()['todos']) == n_elements


def test_list_todos_filter_state_should_return_n_elements(
    session, client, user, token
):
    # variáveis
    n_elements = 5
    state = TodoState.draft

    # building objects
    session.bulk_save_objects(
        TodoFactory.create_batch(n_elements, user_id=user.id, state=state)
    )
    session.commit()
    response = client.get(
        '/todos/?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert len(response.json()['todos']) == n_elements


def test_list_todos_filter_combined_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='Test combined',
            description='combined description',
            state=TodoState.done,
        )
    )

    session.bulk_save_objects(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Other title',
            description='other description',
            state=TodoState.todo,
        )
    )
    session.commit()

    response = client.get(
        '/todos/?title=Test combined&description=combined&state=done',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


# test_delete_todo
def test_delete_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task deleted!'}


def test_delete_todo_should_return_not_found(client, token):
    response = client.delete(
        '/todos/666',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found!'}


# test_patch_todo
def test_patch_todo_should_return_not_found(client, token):
    response = client.patch(
        '/todos/666',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found!'}


def test_patch_todo(client, session, token, user):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    session.commit()
    session.refresh(todo)

    response = client.patch(
        f'/todos/{todo.id}',
        json={'title': 'Título teste'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'Título teste'
    assert response.json()['description'] == todo.description


# teste exercício todos atributos OK
def test_list_todos_should_return_all_expected_fields(
    session, client, user, token, mock_db_time
):
    with mock_db_time(model=Todo) as time:
        todo = TodoFactory(user_id=user.id)
        session.add(todo)
        session.commit()

    session.refresh(todo)
    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json()['todos'] == [
        {
            'id': todo.id,
            'title': todo.title,
            'description': todo.description,
            'state': todo.state,
            'user_id': todo.user_id,
            'created_at': time.isoformat(),
            'updated_at': time.isoformat(),
        }
    ]
