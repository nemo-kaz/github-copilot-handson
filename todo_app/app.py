from flask import Flask, render_template, request, redirect, url_for
from enum import Enum

app = Flask(__name__)

class Status(Enum):
    TODO = 'Todo'
    DOING = 'Doing'
    COMPLETED = 'Completed'

# メモリ上のToDoリスト（本番ではDB推奨）
todos = []

def get_next_id():
    if not todos:
        return 1
    return max(item['id'] for item in todos) + 1

@app.route('/')
def index():
    grouped = {s.value: [] for s in Status}
    for item in todos:
        grouped[item['status']].append(item)
    return render_template('index.html', grouped=grouped, Status=Status)

@app.route('/add', methods=['POST'])
def add():
    title = request.form['title']
    status = request.form['status']
    todos.append({'id': get_next_id(), 'title': title, 'status': status})
    return redirect(url_for('index'))

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit(item_id):
    item = next((t for t in todos if t['id'] == item_id), None)
    if not item:
        return 'Not found', 404
    if request.method == 'POST':
        item['title'] = request.form['title']
        item['status'] = request.form['status']
        return redirect(url_for('index'))
    return render_template('edit.html', item=item, Status=Status)

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete(item_id):
    global todos
    todos = [t for t in todos if t['id'] != item_id]
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
