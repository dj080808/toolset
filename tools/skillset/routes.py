from flask import Blueprint, render_template, request, redirect, url_for
from .models import Tool, Stack, Entry

bp = Blueprint("skillset", __name__, url_prefix="/skillset", template_folder="../../templates/skillset")


@bp.route("/")
def index():
    tools = Tool.get_all()
    return render_template("index.html", tools=tools)


@bp.route("/tool/<int:tool_id>")
def tool_detail(tool_id):
    tool = Tool.get_by_id(tool_id)
    if not tool:
        return "工具不存在", 404
    stacks = Stack.get_by_tool(tool_id)
    # 统计每个技术栈的条目数
    stack_list = []
    for s in stacks:
        s_dict = dict(s)
        s_dict["entry_count"] = Stack.entry_count(s["id"])
        stack_list.append(s_dict)
    return render_template("tool.html", tool=tool, stacks=stack_list)


@bp.route("/stack/<int:stack_id>")
def stack_detail(stack_id):
    stack = Stack.get_by_id(stack_id)
    if not stack:
        return "技术栈不存在", 404
    tool = Tool.get_by_id(stack["tool_id"])
    entries = Entry.get_by_stack(stack_id)
    return render_template("stack.html", tool=tool, stack=stack, entries=entries)


@bp.route("/stack/<int:stack_id>/entry/new", methods=["GET", "POST"])
def entry_new(stack_id):
    stack = Stack.get_by_id(stack_id)
    if not stack:
        return "技术栈不存在", 404
    tool = Tool.get_by_id(stack["tool_id"])
    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()
        tags = request.form.get("tags", "").strip()
        if title:
            Entry.create(stack_id, title, content, tags)
        return redirect(url_for(".stack_detail", stack_id=stack_id))
    return render_template("entry_form.html", tool=tool, stack=stack, entry=None)


@bp.route("/entry/<int:entry_id>/edit", methods=["GET", "POST"])
def entry_edit(entry_id):
    entry = Entry.get_by_id(entry_id)
    if not entry:
        return "条目不存在", 404
    stack = Stack.get_by_id(entry["stack_id"])
    tool = Tool.get_by_id(stack["tool_id"])
    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()
        tags = request.form.get("tags", "").strip()
        if title:
            Entry.update(entry_id, title, content, tags)
        return redirect(url_for(".stack_detail", stack_id=stack["id"]))
    return render_template("entry_form.html", tool=tool, stack=stack, entry=entry)


@bp.route("/entry/<int:entry_id>/delete", methods=["POST"])
def entry_delete(entry_id):
    entry = Entry.get_by_id(entry_id)
    if entry:
        Entry.delete(entry_id)
        return redirect(url_for(".stack_detail", stack_id=entry["stack_id"]))
    return "条目不存在", 404
