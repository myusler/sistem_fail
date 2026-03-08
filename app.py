import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- DATABASE CONFIG ---
database_url = os.environ.get('DATABASE_URL')  # Ambil dari env Render
if database_url and database_url.startswith("postgres://"):
    # SQLAlchemy perlukan postgresql:// bukannya postgres://
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.Integer)
    title = db.Column(db.String(200))
    description = db.Column(db.String(500))

@app.route('/')
def index():
    docs = Document.query.order_by(Document.serial).all()
    return render_template('index.html', docs=docs)

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        last = Document.query.order_by(Document.serial.desc()).first()
        serial = 1 if not last else last.serial + 1

        doc = Document(serial=serial, title=title, description=description)
        db.session.add(doc)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):
    doc = Document.query.get_or_404(id)

    if request.method == 'POST':
        doc.title = request.form['title']
        doc.description = request.form['description']
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit.html', doc=doc)

@app.route('/delete/<int:id>')
def delete(id):
    doc = Document.query.get_or_404(id)
    db.session.delete(doc)
    db.session.commit()
    reorder()
    return redirect(url_for('index'))

def reorder():
    docs = Document.query.order_by(Document.serial).all()
    for i, doc in enumerate(docs, start=1):
        doc.serial = i
    db.session.commit()

@app.route('/up/<int:id>')
def up(id):
    doc = Document.query.get(id)
    above = Document.query.filter(Document.serial == doc.serial - 1).first()

    if above:
        above.serial, doc.serial = doc.serial, above.serial
        db.session.commit()

    return redirect(url_for('index'))

@app.route('/down/<int:id>')
def down(id):
    doc = Document.query.get(id)
    below = Document.query.filter(Document.serial == doc.serial + 1).first()

    if below:
        below.serial, doc.serial = doc.serial, below.serial
        db.session.commit()

    return redirect(url_for('index'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)