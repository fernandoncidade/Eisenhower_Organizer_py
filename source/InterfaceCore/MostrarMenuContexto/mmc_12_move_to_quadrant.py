from PySide6.QtWidgets import QInputDialog, QMessageBox
from PySide6.QtCore import QCoreApplication, Qt
from .mmc_05_is_completed_list import _is_completed_list
from .mmc_06_quadrant_options import _quadrant_options
from .mmc_07_target_list_for_quadrant import _target_list_for_quadrant
from .mmc_09_base_text_from_item import _base_text_from_item
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)

def _move_to_quadrant(app, item, source_list):
    task_name = (_base_text_from_item(item) or "").strip()
    if not task_name:
        task_name = get_text("Tarefa")

    try:
        opts = _quadrant_options(app, include_completed=True)
        chosen, ok = QInputDialog.getItem(
            app,
            get_text("Mover tarefa"),
            get_text("Selecione o quadrante:"),
            opts,
            0,
            False
        )
        if not ok or not chosen:
            return

        try:
            idx = opts.index(chosen)

        except ValueError:
            return

        keep_completed = _is_completed_list(app, source_list)
        target = _target_list_for_quadrant(app, idx, keep_completed=keep_completed, include_completed=True)

        if target is None or target is source_list:
            try:
                QMessageBox.warning(
                    app,
                    get_text("Erro"),
                    (get_text('Não foi possível mover a tarefa "{item}"!') or 'Não foi possível mover a tarefa "{item}"!').replace("{item}", task_name),
                )

            except Exception:
                pass

            return

        new_state = Qt.Checked if _is_completed_list(app, target) else Qt.Unchecked
        source_list.blockSignals(True)
        target.blockSignals(True)
        moved_ok = False

        try:
            app.move_item_between_lists(item, source_list, target, new_state)
            moved_ok = True

        finally:
            source_list.blockSignals(False)
            target.blockSignals(False)

        try:
            app.save_tasks()

        except Exception:
            pass

        try:
            if hasattr(app, "calendar_pane") and app.calendar_pane:
                app.calendar_pane.calendar_panel.update_task_list()

        except Exception:
            pass

        try:
            if moved_ok:
                QMessageBox.information(
                    app,
                    get_text("Sucesso"),
                    (get_text('Tarefa "{item}" movida com sucesso!') or 'Tarefa "{item}" movida com sucesso!').replace("{item}", task_name),
                )

            else:
                QMessageBox.warning(
                    app,
                    get_text("Erro"),
                    (get_text('Não foi possível mover a tarefa "{item}"!') or 'Não foi possível mover a tarefa "{item}"!').replace("{item}", task_name),
                )

        except Exception:
            pass

    except Exception as e:
        logger.error(f"Erro ao mover tarefa de quadrante via menu: {e}", exc_info=True)

        try:
            QMessageBox.warning(
                app,
                get_text("Erro"),
                (get_text('Não foi possível mover a tarefa "{item}"!') or 'Não foi possível mover a tarefa "{item}"!').replace("{item}", task_name),
            )

        except Exception:
            pass
