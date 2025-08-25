from flask import Flask, render_template, request, redirect, flash , url_for , session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy


# بارگذاری متغیرهای محیطی
load_dotenv()

app = Flask(__name__)
app.secret_key = "mysecretkey"  # برای فلش‌مسج‌ها

# ساخت دیتابیس
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# کلاس های دیتابیس
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)



# گرفتن مقادیر از .env
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

def send_email(name, email, message):
    subject = f"پیام جدید از {name}"
    body = f"""
    نام: {name}
    ایمیل: {email}
    پیام:
    {message}
    """

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print("خطا در ارسال ایمیل:", e)
        return False

project_list = []
blog_list = []

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/projects")
def projects():
    projects = Project.query.all()
    return render_template("projects.html", projects=projects)


@app.route("/projects/<int:project_id>")
def project_detail(project_id):
    # اینجا می‌تونی دیتای پروژه رو از دیتابیس یا لیست بخونی
    projects = {
        1: {"title": "برج مسکونی الف", "desc": "جزئیات کامل پروژه برج ۲۰ طبقه ..."},
        2: {"title": "مجتمع تجاری ب", "desc": "جزئیات کامل مجتمع تجاری ..."},
        3: {"title": "ساختمان اداری ج", "desc": "جزئیات کامل ساختمان اداری ..."}
    }
    project = projects.get(project_id, {"title": "پروژه یافت نشد", "desc": "چنین پروژه‌ای وجود ندارد."})
    return render_template("project_detail.html", project=project)

@app.route("/blog")
def blog():
    blogs = Blog.query.all()
    return render_template("blog.html", blogs=blogs)


@app.route("/blog/<int:blog_id>")
def blog_detail(blog_id):
    blogs = {
        1: {
            "title": "اصول طراحی معماری پایدار",
            "content": "اینجا متن کامل مقاله مربوط به معماری پایدار قرار می‌گیرد..."
        },
        2: {
            "title": "نکات کلیدی در محاسبات سازه",
            "content": "اینجا متن کامل مقاله محاسبات سازه قرار می‌گیرد..."
        },
        3: {
            "title": "طراحی تاسیسات مکانیکی کارآمد",
            "content": "اینجا متن کامل مقاله تاسیسات مکانیکی قرار می‌گیرد..."
        }
    }
    blog = blogs.get(blog_id, {"title": "مقاله یافت نشد", "content": "چنین مقاله‌ای وجود ندارد."})
    return render_template("blog_detail.html", blog=blog)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        if not name or not email or not message:
            flash("لطفاً همه فیلدها را پر کنید.", "error")
            return redirect("/contact")

        if send_email(name, email, message):
            flash("پیام شما با موفقیت ارسال شد ✅", "success")
        else:
            flash("خطا در ارسال پیام ❌ دوباره تلاش کنید.", "error")

        # اینجا می‌تونی پیام‌ها رو تو دیتابیس ذخیره کنی یا ایمیل بفرستی
        print(f"پیام جدید:\nنام: {name}\nایمیل: {email}\nپیام: {message}")

        return redirect("/contact")
    
    return render_template("contact.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "1234":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("نام کاربری یا رمز اشتباه است ❌", "danger")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

@app.route("/admin")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    project_list = Project.query.all()
    blog_list = Blog.query.all()
    return render_template("admin_dashboard.html", projects=project_list, blogs=blog_list)



@app.route("/admin/add_project", methods=["POST"])
def add_project():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    title = request.form["title"]
    description = request.form["description"]

    new_project = Project(title=title, description=description)
    db.session.add(new_project)
    db.session.commit()   # ✅ این خیلی مهمه

    flash("پروژه با موفقیت اضافه شد!", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/edit_project/<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    project = Project.query.get_or_404(project_id)

    if request.method == "POST":
        project.title = request.form.get("title")
        project.description = request.form.get("description")
        db.session.commit()
        flash("پروژه با موفقیت ویرایش شد!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("edit_project.html", project=project)



@app.route("/admin/add_blog", methods=["POST"])
def add_blog():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    title = request.form.get("title")
    content = request.form.get("content")

    try:
        new_blog = Blog(title=title, content=content)
        db.session.add(new_blog)
        db.session.commit()   # ✅ ذخیره واقعی در دیتابیس
        flash("مقاله با موفقیت اضافه شد!", "success")
    except Exception as e:
        db.session.rollback()  # اگر خطا خورد، دیتابیس برمی‌گرده
        flash(f"❌ خطا در ذخیره مقاله: {str(e)}", "danger")

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/edit_blog/<int:blog_id>", methods=["GET", "POST"])
def edit_blog(blog_id):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    blog = Blog.query.get_or_404(blog_id)

    if request.method == "POST":
        blog.title = request.form.get("title")
        blog.content = request.form.get("content")
        db.session.commit()
        flash("مقاله با موفقیت ویرایش شد!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("edit_blog.html", blog=blog)


@app.route("/test_db")
def test_db():
    test_project = Project(title="پروژه تستی", description="برای بررسی ذخیره در دیتابیس")
    db.session.add(test_project)
    db.session.commit()
    projects = Project.query.all()
    return f"✅ تعداد پروژه‌ها در دیتابیس: {len(projects)}"


if __name__ == "__main__":
    app.run(debug=True)