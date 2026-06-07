from flask import Blueprint, render_template, request, redirect, url_for
from .models import Tool, Stack, Entry, Favorite

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
    groups = Stack.get_groups(tool_id)
    if groups:
        # 有分组 → 展示分组卡片
        group_list = []
        for g in groups:
            gn = g["group_name"]
            stacks = Stack.get_by_tool(tool_id, gn)
            total_entries = sum(Stack.entry_count(s["id"], "note") for s in stacks)
            total_interviews = sum(Stack.entry_count(s["id"], "interview") for s in stacks)
            active = sum(1 for s in stacks if not s["is_deprecated"])
            deprecated = sum(1 for s in stacks if s["is_deprecated"])
            group_list.append({
                "name": gn,
                "stack_count": len(stacks),
                "active_count": active,
                "deprecated_count": deprecated,
                "entry_count": total_entries,
                "interview_count": total_interviews,
            })
        return render_template("tool_groups.html", tool=tool, groups=group_list)
    # fallback: no groups → direct stack list
    stacks = Stack.get_by_tool(tool_id)
    stack_list = []
    for s in stacks:
        sd = dict(s)
        sd["entry_count"] = Stack.entry_count(s["id"], "note")
        sd["interview_count"] = Stack.entry_count(s["id"], "interview")
        stack_list.append(sd)
    return render_template("tool.html", tool=tool, stacks=stack_list)


@bp.route("/tool/<int:tool_id>/group/<group_name>")
def group_detail(tool_id, group_name):
    tool = Tool.get_by_id(tool_id)
    if not tool:
        return "工具不存在", 404
    stacks = Stack.get_by_tool(tool_id, group_name)
    if not stacks:
        return "分组不存在", 404
    stack_list = []
    for s in stacks:
        sd = dict(s)
        sd["entry_count"] = Stack.entry_count(s["id"], "note")
        sd["interview_count"] = Stack.entry_count(s["id"], "interview")
        stack_list.append(sd)
    return render_template("group_detail.html", tool=tool, group_name=group_name, stacks=stack_list)


@bp.route("/stack/<int:stack_id>")
def stack_detail(stack_id):
    stack = Stack.get_by_id(stack_id)
    if not stack:
        return "技术栈不存在", 404
    tool = Tool.get_by_id(stack["tool_id"])
    notes = Entry.get_by_stack(stack_id, "note")
    interviews = Entry.get_by_stack(stack_id, "interview")
    group_name = stack["group_name"] if stack["group_name"] else None
    return render_template("stack.html", tool=tool, stack=stack, notes=notes, interviews=interviews, group_name=group_name)


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
        entry_type = request.form.get("entry_type", "note")
        if title:
            Entry.create(stack_id, title, content, tags, entry_type)
        return redirect(url_for(".stack_detail", stack_id=stack_id))
    # GET 时可从 query string 预设类型
    preset_type = request.args.get("type", "note")
    return render_template("entry_form.html", tool=tool, stack=stack, entry=None, preset_type=preset_type)


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
        entry_type = request.form.get("entry_type", "note")
        if title:
            Entry.update(entry_id, title, content, tags, entry_type)
        return redirect(url_for(".stack_detail", stack_id=stack["id"]))
    return render_template("entry_form.html", tool=tool, stack=stack, entry=entry, preset_type=None)


@bp.route("/entry/<int:entry_id>/delete", methods=["POST"])
def entry_delete(entry_id):
    entry = Entry.get_by_id(entry_id)
    if entry:
        Entry.delete(entry_id)
        return redirect(url_for(".stack_detail", stack_id=entry["stack_id"]))
    return "条目不存在", 404


# ==================== Practice ====================

@bp.route("/practice")
def practice_select():
    groups = Stack.get_groups(1)
    grouped = {}
    for g in groups:
        gn = g["group_name"]
        stacks = Stack.get_by_tool(1, gn)
        active = [dict(s) for s in stacks if not s["is_deprecated"]]
        if active: grouped[gn] = active
    return render_template("practice_select.html", grouped=grouped)


@bp.route("/practice/start", methods=["POST"])
def practice_start():
    stack_ids = request.form.getlist("stack_ids", type=int)
    if not stack_ids: return redirect(url_for(".practice_select"))
    questions = Entry.get_random_interviews(stack_ids, 10)
    if not questions: return "please add interview items first", 404
    return render_template("practice_quiz.html", questions=questions)


@bp.route("/practice/review", methods=["POST"])
def practice_review():
    answers = {}
    for key, val in request.form.items():
        if key.startswith("answer_"):
            answers[int(key.replace("answer_", ""))] = val.strip()
    ids = list(answers.keys())
    questions = [q for q in (Entry.get_by_id(eid) for eid in ids) if q]
    return render_template("practice_review.html", questions=questions, answers=answers)


# ==================== Favorites ====================

@bp.route("/favorites")
def favorite_list():
    favorites = Favorite.get_all()
    return render_template("favorites.html", favorites=favorites)


@bp.route("/favorite/<int:entry_id>/toggle", methods=["POST"])
def favorite_toggle(entry_id):
    if Favorite.is_favorited(entry_id):
        Favorite.remove(entry_id)
        favorited = False
    else:
        Favorite.add(entry_id)
        favorited = True
    # AJAX request: return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return {"favorited": favorited}
    # Form request: redirect back
    ref = request.form.get("ref", url_for(".index"))
    return redirect(ref)
