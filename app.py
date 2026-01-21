from flask import Flask, render_template, request, redirect, url_for
import json, os, uuid
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
DATA_FILE = 'posts.json'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False)


    
def load_posts():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_posts(posts):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    posts = load_posts()
    posts.reverse()
    return render_template('index.html', posts=posts)

@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        posts = load_posts()

        image = request.files['image']
        image_filename = None

        if image:
            ext = image.filename.split('.')[-1]
            image_filename = f"{uuid.uuid4()}.{ext}"
            image.save(os.path.join(UPLOAD_FOLDER, image_filename))

        post = {
            "id": str(uuid.uuid4()),
            "title": request.form['title'],
            "content": request.form['content'],
            "image": image_filename,
            "date": datetime.now().strftime('%Y-%m-%d %H:%M')
        }

        posts.append(post)
        save_posts(posts)
        return redirect(url_for('index'))

    return render_template('write.html')

@app.route('/view/<post_id>')
def view(post_id):
    posts = load_posts()
    post = next(p for p in posts if p['id'] == post_id)
    return render_template('view.html', post=post)

@app.route('/delete/<post_id>')
def delete(post_id):
    posts = load_posts()
    posts = [p for p in posts if p['id'] != post_id]
    save_posts(posts)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
