import json
import uuid
from PySide6.QtCore import Qt
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def save_tasks(app):
    try:
        def _normalize_priority(value):
            try:
                if value is None or value == "":
                    return None

                return int(value)

            except Exception:
                return None

        def list_to_entries(lst):
            entries = []

            for i in range(lst.count()):
                item = lst.item(i)

                if item.flags() & Qt.ItemIsSelectable:
                    data = item.data(Qt.UserRole) or {}

                    if not isinstance(data, dict):
                        data = {}

                    task_id = (data.get("id") or "").strip()

                    if not task_id:
                        task_id = str(uuid.uuid4())
                        data["id"] = task_id
                        item.setData(Qt.UserRole, data)

                    text = data.get("text", item.text())
                    date = data.get("date")
                    time = data.get("time")
                    entry = {
                        "id": task_id,
                        "text": text,
                        "date": date,
                        "time": time,
                    }

                    try:
                        file_path = data.get("file_path")

                        if file_path:
                            entry["file_path"] = file_path

                    except Exception:
                        pass

                    try:
                        description = data.get("description")

                        if description:
                            entry["description"] = description

                    except Exception:
                        pass

                    try:
                        priority = _normalize_priority(data.get("priority"))

                        if priority is not None:
                            entry["priority"] = priority

                    except Exception:
                        pass

                    entries.append(entry)

            return entries

        tasks = {
            "quadrant1": list_to_entries(app.quadrant1_list),
            "quadrant1_completed": list_to_entries(app.quadrant1_completed_list),
            "quadrant2": list_to_entries(app.quadrant2_list),
            "quadrant2_completed": list_to_entries(app.quadrant2_completed_list),
            "quadrant3": list_to_entries(app.quadrant3_list),
            "quadrant3_completed": list_to_entries(app.quadrant3_completed_list),
            "quadrant4": list_to_entries(app.quadrant4_list),
            "quadrant4_completed": list_to_entries(app.quadrant4_completed_list),
        }
        with open(app.tasks_path, "w", encoding="utf-8") as file:
            json.dump(tasks, file, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"Erro ao salvar tarefas: {e}", exc_info=True)
