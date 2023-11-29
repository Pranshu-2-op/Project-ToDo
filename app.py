from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ToDo.db"
app.config['SQLAlCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()

class ToDo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"


@app.route("/", methods=['GET', 'POST'])
def hello():
    if request.method == "POST":
        Title = request.form["title"]
        Desc = request.form["desc"]
    
        todo = ToDo(title=Title, desc=Desc)
        db.session.add(todo)
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

@app.route("/music.html")
def music():
    return render_template("music.html")

# @app.route("/movie.html")
# def movie():
#     return render_template("movie.html")

@app.route("/about.html")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)