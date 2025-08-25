from App import db, Project, Blog, app

with app.app_context():
    print("Projects:", Project.query.all())
    print("Blogs:", Blog.query.all())
