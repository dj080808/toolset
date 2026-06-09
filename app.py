from flask import Flask, redirect, url_for
import markdown
import os
from dotenv import load_dotenv
load_dotenv()  # 加载 .env（不覆盖已有的 OS 环境变量，系统优先）

from db import init_db
from tools.skillset.routes import bp as skillset_bp

app = Flask(__name__)
app.register_blueprint(skillset_bp)


# Jinja2 markdown filter
@app.template_filter("markdown")
def markdown_filter(text):
    return markdown.markdown(
        text,
        extensions=["fenced_code", "tables", "codehilite"],
    )


@app.route("/")
def home():
    return redirect(url_for("skillset.index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
