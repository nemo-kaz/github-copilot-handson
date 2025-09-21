"""
app.pyの主要機能に対する単体テスト。
pytestで実行可能。
"""
import pytest
from app import app, Status, todos, get_next_id

@pytest.fixture(autouse=True)
def clear_todos():
    # 各テスト前にtodosをクリア
    todos.clear()

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_empty(client):
    """ToDoが空の場合も200で表示される"""
    rv = client.get('/')
    assert rv.status_code == 200
    assert 'なし' in rv.data.decode('utf-8')

def test_add_and_list(client):
    """ToDo追加と一覧表示"""
    rv = client.post('/add', data={'title': 'task1', 'status': Status.TODO.value})
    assert rv.status_code == 302  # リダイレクト
    rv = client.get('/')
    assert b'task1' in rv.data
    assert b'Todo' in rv.data

def test_add_invalid(client):
    """不正な入力は400"""
    rv = client.post('/add', data={'title': '', 'status': Status.TODO.value})
    assert rv.status_code == 400
    rv = client.post('/add', data={'title': 'x', 'status': 'INVALID'})
    assert rv.status_code == 400

def test_edit(client):
    """ToDo編集"""
    client.post('/add', data={'title': 'task2', 'status': Status.DOING.value})
    item_id = todos[0]['id']
    rv = client.post(f'/edit/{item_id}', data={'title': 'task2-edit', 'status': Status.COMPLETED.value})
    assert rv.status_code == 302
    assert todos[0]['title'] == 'task2-edit'
    assert todos[0]['status'] == Status.COMPLETED.value

def test_edit_invalid(client):
    """存在しないIDや不正入力"""
    rv = client.post('/edit/999', data={'title': 'x', 'status': Status.TODO.value})
    assert rv.status_code == 404
    client.post('/add', data={'title': 'task3', 'status': Status.TODO.value})
    item_id = todos[0]['id']
    rv = client.post(f'/edit/{item_id}', data={'title': '', 'status': Status.TODO.value})
    assert rv.status_code == 400
    rv = client.post(f'/edit/{item_id}', data={'title': 'ok', 'status': 'NG'})
    assert rv.status_code == 400

def test_delete(client):
    """ToDo削除"""
    client.post('/add', data={'title': 'task4', 'status': Status.DOING.value})
    item_id = todos[0]['id']
    rv = client.post(f'/delete/{item_id}')
    assert rv.status_code == 302
    assert len(todos) == 0

def test_delete_notfound(client):
    """存在しないIDの削除もエラーにならない"""
    rv = client.post('/delete/999')
    assert rv.status_code == 302
