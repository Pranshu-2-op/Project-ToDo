from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

    

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ToDo.db"
app.config['SQLAlCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
app.app_context().push()

class ToDo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    
    dt = timedelta(hours=5, minutes=30) + datetime.utcnow()
    nt= dt.strftime("%Y-%m-%d %I:%M:%S %p %Z")
    date_created = db.Column(db.String(20), default=nt)
    def date_created_ist(self):

        ist_offset = timedelta(hours=5, minutes=30)
        return self.date_created + ist_offset  
    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"
    
class VisitorLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    ip_address = db.Column(db.String(20))
    visited = db.Column(db.String(300))
    
    dt = timedelta(hours=5, minutes=30) + datetime.utcnow()
    nt= dt.strftime("%Y-%m-%d %I:%M:%S %p %Z")
    date_created = db.Column(db.String(20), default=nt)
    def date_created_ist(self):

        ist_offset = timedelta(hours=5, minutes=30)
        return self.date_created + ist_offset

    def __repr__(self):
        return f"<VisitorLog {self.ip_address}>"


@app.route("/", methods=['GET', 'POST'])
def hello():
    if request.method == "POST":
        Title = request.form["title"]
        Desc = request.form["desc"]
        ip = request.remote_addr
        if Title == "":
            alltodo = ToDo.query.all()
            return render_template('index.html',title=False,  alltodo=alltodo)
        else:
            todo = ToDo(title=Title, desc=Desc)
            db.session.add(todo)
            db.session.commit()
            
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    oip = VisitorLog(ip_address = ip)
    db.session.add(oip)
    db.session.commit()
    
    alltodo = ToDo.query.all()
    # print(alltodo)
    return render_template('index.html', alltodo=alltodo)
    # return "Hello World!" 

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
    
    todo = ToDo.query.filter_by(sno=sno).first()
    return render_template('edit.html', todo=todo)
    

@app.route("/done/<int:sno>")
def delete(sno):
    todo = ToDo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")


# Function to retrieve songs for a specific page
def get_songs_for_page(page_num, per_page):
    songs_directory = os.path.join(app.root_path, 'static', 'music')  # Path to your songs directory
    all_songs = os.listdir(songs_directory)  # Get all file names in the directory
    start = (page_num - 1) * per_page
    end = start + per_page
    return all_songs[start:end]


@app.route("/music")
def display_songs():
    page = request.args.get('page', 1, type=int)
    per_page = 3  # Number of songs per page
    all_songs = get_songs_for_page(page, per_page)
    songs = []
    for song in all_songs:
        song_details = {
            "title": song,  # Assuming song file name is the title
            "thumbnail": f"thumbnail/{song.replace('.mp3', '.png')}",  # Assuming thumbnails have same name as songs with .png extension
            "audio": f"music/{song}"  # Path to the audio file
        }
        songs.append(song_details)
    total_songs = len(os.listdir(os.path.join(app.root_path, 'static', 'music')))
    total_pages = (total_songs + per_page - 1) // per_page
    return render_template('songs.html', songs=songs, page=page, total_pages=total_pages)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/updates")
def updates():
    return render_template("updates.html")

@app.route("/ip")
def dev():
    logs = VisitorLog.query.all()
    return render_template("ip.html", ip_add=logs)




if __name__ == "__main__":
    db.create_all()
    app.run()


