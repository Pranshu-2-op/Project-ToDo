from flask import Flask, render_template, redirect, request, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ToDo.db"
app.config['SQLAlCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
app.app_context().push()


def time():
    utc = datetime.utcnow()
    ist = timedelta(days=0, hours=5, minutes=30, seconds=0)
    utctoist = utc + ist
    time = utctoist.strftime("%Y-%m-%d %I:%M:%S %p")
    return time


# Storing todo tasks
class ToDo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.String(30))

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"


class VisitorLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(20))
    device = db.Column(db.String(60))
    page = db.Column(db.String(30))
    ist_time = db.Column(db.String(30))



def log_visitor(page):
    new_log = VisitorLog(
        ip_address=request.headers.get('X-Forwarded-For', request.remote_addr),
        page=page,
        device = request.headers.get('User-Agent'),
        ist_time = time()
    )
    db.session.add(new_log)
    db.session.commit()




@app.route("/", methods=['GET', 'POST'])
def hello():
    if request.method == "POST":
        Title = request.form["title"]
        Desc = request.form["desc"]
        if Title == "":
            alltodo = ToDo.query.all()
            return render_template('index.html',title=False,  alltodo=alltodo)
        else:
            todo = ToDo(title=Title, desc=Desc, date_created = time())
            db.session.add(todo)
            db.session.commit()

    page = "Home"
    log_visitor(page)

    ip_add = VisitorLog.query.all()
    alltodo = ToDo.query.all()
    return render_template('index.html',ip_add=ip_add, alltodo=alltodo)


# to edit a task
@app.route("/edit/<int:sno>", methods=['GET', 'POST'])
def edit(sno):
    if request.method == "POST":
        Title = request.form["title"]
        Desc = request.form["desc"]
        todo = ToDo.query.filter_by(sno=sno).first()
        todo.title = Title
        todo.desc = Desc
        db.session.add(todo)
        db.session.commit()
        return redirect("/")
    page = "Edit"
    log_visitor(page)

    todo = ToDo.query.filter_by(sno=sno).first()
    return render_template('edit.html', todo=todo)

# Function to delete a task
@app.route("/done/<int:sno>")
def delete(sno):
    page = "Delete"
    log_visitor(page)

    todo = ToDo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")


# Function to retrieve songs for a specific page
def get_songs_for_page(page_num, per_page):
    songs_directory = os.path.join(app.root_path, 'static', 'music')
    all_songs = os.listdir(songs_directory)

    # Priority songs should be listed as separate strings, not one string
    priority_songs = ["Mera Safar.mp3", "Raabta.mp3", "The Specture.mp3", "Soch Na Sake.mp3", "Meri Baari.mp3", "Amit Mahajan.mp3"]

    # Prioritize existing songs
    prioritized_songs = [song for song in priority_songs if song in all_songs]
    for song in prioritized_songs:
        all_songs.remove(song)
        all_songs.insert(0, song)
        
    start = (page_num - 1) * per_page
    end = start + per_page
    return all_songs[start:end]

@app.route("/music", methods=['GET', 'POST'])
def display_songs():
    page = "Music"
    log_visitor(page)

    page = request.args.get('page', 1, type=int)
    per_page = 3
    all_songs = get_songs_for_page(page, per_page)
    songs = []
    for song in all_songs:
        song_details = {
            "title": song.replace('.mp3', ''),
            "thumbnail": f"thumbnail/{song.replace('.mp3', '.png')}",
            "audio": f"music/{song}"
        }
        songs.append(song_details)
    total_songs = len(os.listdir(os.path.join(app.root_path, 'static', 'music')))
    total_pages = (total_songs + per_page - 1) // per_page
    return render_template('songs.html', songs=songs, page=page, total_pages=total_pages)


@app.route("/about")
def about():
    page = "About"
    log_visitor(page)
    return render_template("about.html")


@app.route("/github")
def github_repo():
    return redirect("https://github.com/Pranshu-2-op/ToDo")

@app.route("/updates")
def updates():
    page = "Updates"
    log_visitor(page)
    return render_template("updates.html")

@app.route("/log")
def dev():
    page = "Log"
    log_visitor(page)
    logs = VisitorLog.query.all()
    return render_template("ip.html", ip_add=logs)




if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)


