
# 標準ライブラリと最小限の外部依存（Flask）のみを使用
from flask import Flask, render_template, request, redirect, url_for, abort
from enum import Enum


# Flaskアプリケーションのインスタンス生成
app = Flask(__name__)


class Status(Enum):
    """
    ToDoアイテムの状態を表す列挙型。
    バージョン依存性のないEnum利用。
    """
    TODO = 'Todo'
    DOING = 'Doing'
    COMPLETED = 'Completed'


# メモリ上のToDoリスト（本番運用時はDB等を利用）
todos = []


def get_next_id():
    """
    ToDoアイテムの一意なIDを生成する。
    """
    if not todos:
        return 1
    return max(item['id'] for item in todos) + 1


@app.route('/')
def index():
    """
    ToDoアイテムをステータスごとに区分けして一覧表示。
    """
    grouped = {s.value: [] for s in Status}
    for item in todos:
        # ステータス値が不正な場合も考慮
        if item['status'] in grouped:
            grouped[item['status']].append(item)
    return render_template('index.html', grouped=grouped, Status=Status)


@app.route('/add', methods=['POST'])
def add():
    """
    ToDoアイテムの新規作成。
    入力値のバリデーションも実施。
    """
    title = request.form.get('title', '').strip()
    status = request.form.get('status')
    if not title or status not in [s.value for s in Status]:
        abort(400, description="Invalid input.")
    todos.append({'id': get_next_id(), 'title': title, 'status': status})
    return redirect(url_for('index'))


@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit(item_id):
    """
    ToDoアイテムの編集（タイトル・ステータス）。
    存在しないIDや不正な入力もハンドリング。
    """
    item = next((t for t in todos if t['id'] == item_id), None)
    if not item:
        abort(404, description="Item not found.")
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        status = request.form.get('status')
        if not title or status not in [s.value for s in Status]:
            abort(400, description="Invalid input.")
        item['title'] = title
        item['status'] = status
        return redirect(url_for('index'))
    return render_template('edit.html', item=item, Status=Status)


@app.route('/delete/<int:item_id>', methods=['POST'])
def delete(item_id):
    """
    ToDoアイテムの削除。
    存在しないIDも安全に処理。
    """
    global todos
    before = len(todos)
    todos = [t for t in todos if t['id'] != item_id]
    # 削除対象がなかった場合もリダイレクト
    return redirect(url_for('index'))


if __name__ == '__main__':
    # バージョン依存性を抑えるため、host/portはデフォルト値
    app.run(debug=True)
