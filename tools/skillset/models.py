from db import get_db


class Tool:
    @staticmethod
    def get_all():
        db = get_db()
        return db.execute("SELECT * FROM tool ORDER BY id").fetchall()

    @staticmethod
    def get_by_id(tool_id):
        db = get_db()
        return db.execute("SELECT * FROM tool WHERE id = ?", (tool_id,)).fetchone()

    @staticmethod
    def create(name, description=""):
        db = get_db()
        db.execute(
            "INSERT INTO tool (name, description) VALUES (?, ?)",
            (name, description),
        )
        db.commit()
        return db.execute("SELECT * FROM tool WHERE id = last_insert_rowid()").fetchone()


class Stack:
    @staticmethod
    def get_by_tool(tool_id):
        db = get_db()
        return db.execute(
            "SELECT * FROM stack WHERE tool_id = ? ORDER BY sort_order, id",
            (tool_id,),
        ).fetchall()

    @staticmethod
    def get_by_id(stack_id):
        db = get_db()
        return db.execute("SELECT * FROM stack WHERE id = ?", (stack_id,)).fetchone()

    @staticmethod
    def create(tool_id, name, description="", sort_order=0):
        db = get_db()
        db.execute(
            "INSERT INTO stack (tool_id, name, description, sort_order) VALUES (?, ?, ?, ?)",
            (tool_id, name, description, sort_order),
        )
        db.commit()
        return db.execute("SELECT * FROM stack WHERE id = last_insert_rowid()").fetchone()

    @staticmethod
    def entry_count(stack_id, entry_type=None):
        db = get_db()
        if entry_type:
            row = db.execute(
                "SELECT COUNT(*) as cnt FROM entry WHERE stack_id = ? AND entry_type = ?",
                (stack_id, entry_type),
            ).fetchone()
        else:
            row = db.execute(
                "SELECT COUNT(*) as cnt FROM entry WHERE stack_id = ?", (stack_id,)
            ).fetchone()
        return row["cnt"]


class Entry:
    @staticmethod
    def get_by_stack(stack_id, entry_type=None):
        db = get_db()
        if entry_type:
            return db.execute(
                "SELECT * FROM entry WHERE stack_id = ? AND entry_type = ? ORDER BY updated_at DESC",
                (stack_id, entry_type),
            ).fetchall()
        return db.execute(
            "SELECT * FROM entry WHERE stack_id = ? ORDER BY updated_at DESC",
            (stack_id,),
        ).fetchall()

    @staticmethod
    def get_by_id(entry_id):
        db = get_db()
        return db.execute("SELECT * FROM entry WHERE id = ?", (entry_id,)).fetchone()

    @staticmethod
    def create(stack_id, title, content="", tags="", entry_type="note"):
        db = get_db()
        db.execute(
            "INSERT INTO entry (stack_id, title, content, tags, entry_type) VALUES (?, ?, ?, ?, ?)",
            (stack_id, title, content, tags, entry_type),
        )
        db.commit()
        return db.execute("SELECT * FROM entry WHERE id = last_insert_rowid()").fetchone()

    @staticmethod
    def update(entry_id, title, content, tags, entry_type):
        db = get_db()
        db.execute(
            "UPDATE entry SET title = ?, content = ?, tags = ?, entry_type = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (title, content, tags, entry_type, entry_id),
        )
        db.commit()

    @staticmethod
    def delete(entry_id):
        db = get_db()
        db.execute("DELETE FROM entry WHERE id = ?", (entry_id,))
        db.commit()
