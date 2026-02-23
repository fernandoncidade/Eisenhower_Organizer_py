from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QToolButton, QLabel, QSizePolicy, QApplication, QMenu, QMessageBox)
from PySide6.QtCore import Signal, QDate, QCoreApplication, Qt, QLocale, QEvent, QObject
from source.InterfaceCore.incore_07_MostrarMenuContexto import _find_source_item_for_calendar, edit_task_dialog
from source.InterfaceCore.incore_13_prioridade_display import prioridade_para_texto
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)


class YearCalendarWidget(QWidget):
    monthSelected = Signal(QDate)
    monthDoubleClicked = Signal(QDate)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._locale = QLocale.system()
        self._year = QDate.currentDate().year()
        self._selected_month = QDate.currentDate().month()
        self._month_counts = {}
        self._month_tooltips = {}
        self._theme_sync_filter = None
        self._styling_in_progress = False

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)

        self.prev_year_button = QToolButton(self)
        self.prev_year_button.setText("<")
        self.prev_year_button.clicked.connect(lambda: self.setYear(self._year - 1))
        header_layout.addWidget(self.prev_year_button)

        self.year_label = QLabel(self)
        self.year_label.setAlignment(Qt.AlignCenter)
        self.year_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        header_layout.addWidget(self.year_label, 1)

        self.next_year_button = QToolButton(self)
        self.next_year_button.setText(">")
        self.next_year_button.clicked.connect(lambda: self.setYear(self._year + 1))
        header_layout.addWidget(self.next_year_button)

        main_layout.addLayout(header_layout)

        self.month_grid = QGridLayout()
        self.month_grid.setContentsMargins(0, 0, 0, 0)
        self.month_grid.setHorizontalSpacing(6)
        self.month_grid.setVerticalSpacing(6)
        main_layout.addLayout(self.month_grid)

        self._month_buttons = []

        for month in range(1, 13):
            button = QToolButton(self)
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setMinimumHeight(56)
            button.setProperty("month", month)
            button.installEventFilter(self)
            button.clicked.connect(lambda _=False, m=month: self._on_month_clicked(m))
            self._month_buttons.append(button)

            row = (month - 1) // 4
            col = (month - 1) % 4
            self.month_grid.addWidget(button, row, col)

        self._refresh_header()
        self._refresh_month_buttons()
        self._apply_palette_style()
        self._install_theme_sync()

    def setLocale(self, locale: QLocale):
        try:
            self._locale = locale if isinstance(locale, QLocale) else QLocale.system()
            self._refresh_month_buttons()

        except Exception as e:
            logger.error(f"Erro ao definir locale no calendário anual: {e}", exc_info=True)

    def setYear(self, year: int):
        try:
            target_year = int(year)

            if int(self._year) == target_year:
                return

            self._year = target_year
            self._refresh_header()
            self._refresh_month_buttons()
            self.monthSelected.emit(self.selectedDate())

        except Exception as e:
            logger.error(f"Erro ao definir ano no calendário anual: {e}", exc_info=True)

    def year(self) -> int:
        return int(self._year)

    def setSelectedDate(self, qdate: QDate):
        try:
            if isinstance(qdate, QDate) and qdate.isValid():
                target_year = int(qdate.year())
                target_month = int(qdate.month())

                if int(self._year) == target_year and int(self._selected_month) == target_month:
                    return

                self._year = target_year
                self._selected_month = target_month
                self._refresh_header()
                self._refresh_month_buttons()

        except Exception as e:
            logger.error(f"Erro ao definir data selecionada no calendário anual: {e}", exc_info=True)

    def selectedDate(self) -> QDate:
        return QDate(self._year, self._selected_month, 1)

    def set_month_counts(self, month_counts: dict):
        try:
            new_counts = dict(month_counts or {})

            if self._month_counts == new_counts:
                return

            self._month_counts = new_counts
            self._refresh_month_buttons()

        except Exception as e:
            logger.error(f"Erro ao definir contagens mensais no calendário anual: {e}", exc_info=True)

    def set_month_tooltip_map(self, month_tooltips: dict):
        try:
            new_tooltips = dict(month_tooltips or {})

            if self._month_tooltips == new_tooltips:
                return

            self._month_tooltips = new_tooltips
            self._refresh_month_buttons()

        except Exception as e:
            logger.error(f"Erro ao definir tooltips mensais no calendário anual: {e}", exc_info=True)

    def set_month_data(self, month_counts: dict, month_tooltips: dict):
        try:
            new_counts = dict(month_counts or {})
            new_tooltips = dict(month_tooltips or {})

            if self._month_counts == new_counts and self._month_tooltips == new_tooltips:
                return

            self._month_counts = new_counts
            self._month_tooltips = new_tooltips
            self._refresh_month_buttons()

        except Exception as e:
            logger.error(f"Erro ao definir dados mensais no calendário anual: {e}", exc_info=True)

    def eventFilter(self, watched, event):
        try:
            if watched in self._month_buttons and event.type() == QEvent.ContextMenu:
                month = int(watched.property("month") or 0)

                if 1 <= month <= 12:
                    self._show_month_context_menu(month, watched, event)
                    return True

            if watched in self._month_buttons and event.type() == QEvent.MouseButtonDblClick:
                month = int(watched.property("month") or 0)

                if 1 <= month <= 12:
                    self._on_month_clicked(month)
                    self.monthDoubleClicked.emit(self.selectedDate())
                    return True

        except Exception as e:
            logger.error(f"Erro no eventFilter do calendário anual: {e}", exc_info=True)

        return super().eventFilter(watched, event)

    def changeEvent(self, event):
        try:
            event_types = {
                QEvent.PaletteChange,
                QEvent.ApplicationPaletteChange,
                QEvent.ThemeChange,
                QEvent.StyleChange,
            }

            try:
                event_types.add(QEvent.ColorSchemeChange)

            except AttributeError:
                pass

            if event.type() in event_types:
                self._apply_palette_style()

        except Exception as e:
            logger.error(f"Erro ao processar changeEvent no calendário anual: {e}", exc_info=True)

        super().changeEvent(event)

    def _month_tasks(self, month: int) -> list:
        tasks = []

        try:
            owner = getattr(self, "owner", None)

            if owner is None or not hasattr(owner, "_collect_tasks"):
                return tasks

            year = int(self._year)

            for task in owner._collect_tasks() or []:
                ds = (task or {}).get("date")
                if not ds:
                    continue

                qd = QDate.fromString(ds, Qt.ISODate)

                if not qd.isValid():
                    continue

                if qd.year() == year and qd.month() == int(month):
                    tasks.append(task)

            tasks.sort(key=lambda t: ((t.get("date") or ""), (t.get("time") or ""), (t.get("text") or "").lower()))

        except Exception as e:
            logger.error(f"Erro ao coletar tarefas do mês no calendário anual: {e}", exc_info=True)

        return tasks

    def _format_task_label(self, task: dict, show_priority: bool) -> str:
        try:
            text = (task.get("text") or "").strip() or (get_text("(Sem título)") or "(Sem título)")
            date_str = task.get("date") or ""
            time_str = task.get("time") or ""
            emoji = ""

            if show_priority:
                try:
                    prio_label = prioridade_para_texto(task.get("priority"), getattr(self, "owner", None))

                    if prio_label:
                        candidate = str(prio_label).strip()[:1]

                        if candidate in {"🔴", "🟠", "🟡", "🟢"}:
                            emoji = candidate

                except Exception:
                    emoji = ""

            if date_str:
                qd = QDate.fromString(date_str, Qt.ISODate)

                if qd.isValid():
                    date_format = "dd/MM/yyyy"

                    try:
                        owner = getattr(self, "owner", None)
                        date_format = getattr(owner, "_date_format", date_format) or date_format

                    except Exception:
                        pass

                    date_str = qd.toString(date_format)

            label = text

            if time_str:
                label = f"{date_str} {time_str} — {label}".strip()

            elif date_str:
                label = f"{date_str} — {label}".strip()

            if emoji:
                label = f"{emoji} {label}"

            return label

        except Exception:
            return (task.get("text") or "").strip() or (get_text("(Sem título)") or "(Sem título)")

    def _edit_task_from_data(self, task: dict):
        try:
            src_list, item = _find_source_item_for_calendar(self.app, task)

            if item is None or src_list is None:
                QMessageBox.warning(self, get_text("✏️ Editar Tarefa"), get_text("Tarefa não encontrada."))
                return

            try:
                edit_task_dialog(self.app, item)

            except Exception:
                pass

            owner = getattr(self, "owner", None)
            if owner is not None and hasattr(owner, "update_task_list"):
                owner.update_task_list()

        except Exception as e:
            logger.error(f"Erro ao editar tarefa no calendário anual: {e}", exc_info=True)

    def _remove_task_from_data(self, task: dict, confirm: bool = True) -> bool:
        try:
            src_list, item = _find_source_item_for_calendar(self.app, task)

            if item is None or src_list is None:
                QMessageBox.warning(self, get_text("🗑️ Remover Tarefa"), get_text("Tarefa não encontrada."))
                return False

            try:
                return bool(self.app.remove_task(item, src_list, confirm=confirm))

            except Exception:
                return False

        except Exception as e:
            logger.error(f"Erro ao remover tarefa no calendário anual: {e}", exc_info=True)
            return False

    def _remove_all_tasks_for_month(self, month: int) -> int:
        try:
            tasks = self._month_tasks(month)
            if not tasks:
                return 0

            confirm = QMessageBox.question(
                self,
                get_text("Remover Todas") or "Remover Todas",
                get_text("Deseja remover todas as tarefas deste mês?") or "Deseja remover todas as tarefas deste mês?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if confirm != QMessageBox.Yes:
                return 0

            removed = 0
            failed = 0

            for task in list(tasks):
                if self._remove_task_from_data(task, confirm=False):
                    removed += 1

                else:
                    failed += 1

            owner = getattr(self, "owner", None)
            if owner is not None and hasattr(owner, "update_task_list"):
                owner.update_task_list()

            if removed > 0 and failed == 0:
                QMessageBox.information(
                    self,
                    get_text("🗑️ Remover Tarefa"),
                    get_text("Tarefa(s) removida(s) com sucesso.") or "Tarefa(s) removida(s) com sucesso.",
                )

            elif removed > 0:
                QMessageBox.warning(
                    self,
                    get_text("🗑️ Remover Tarefa"),
                    get_text("Algumas tarefas não puderam ser removidas.") or "Algumas tarefas não puderam ser removidas.",
                )

            else:
                QMessageBox.warning(
                    self,
                    get_text("🗑️ Remover Tarefa"),
                    get_text("Não foi possível remover as tarefas deste mês.") or "Não foi possível remover as tarefas deste mês.",
                )

            return int(removed)

        except Exception as e:
            logger.error(f"Erro ao remover tarefas do mês no calendário anual: {e}", exc_info=True)
            return 0

    def _show_month_context_menu(self, month: int, watched, event):
        try:
            tasks = self._month_tasks(month)
            show_priority = True

            try:
                owner = getattr(self, "owner", None)

                if owner is not None and hasattr(owner, "show_priority_checkbox"):
                    show_priority = bool(owner.show_priority_checkbox.isChecked())

            except Exception:
                show_priority = True

            menu = QMenu(self)
            edit_menu = menu.addMenu(get_text("✏️ Editar Tarefa") or "✏️ Editar Tarefa")
            remove_menu = menu.addMenu(get_text("🗑️ Remover Tarefa") or "🗑️ Remover Tarefa")

            if tasks:
                for task in tasks:
                    label = self._format_task_label(task, show_priority=show_priority)
                    act_edit = edit_menu.addAction(label)
                    act_edit.triggered.connect(lambda _=False, t=task: self._edit_task_from_data(t))

                for task in tasks:
                    label = self._format_task_label(task, show_priority=show_priority)
                    act_remove = remove_menu.addAction(label)
                    act_remove.triggered.connect(lambda _=False, t=task: self._remove_task_from_data(t, True))

                remove_menu.addSeparator()
                act_remove_all = remove_menu.addAction(get_text("Remover Todas") or "Remover Todas")
                act_remove_all.triggered.connect(lambda _=False, m=month: self._remove_all_tasks_for_month(m))

            else:
                edit_menu.setEnabled(False)
                remove_menu.setEnabled(False)

            try:
                global_pos = event.globalPos()

            except Exception:
                pos = event.pos() if hasattr(event, "pos") else watched.rect().center()
                global_pos = watched.mapToGlobal(pos)

            menu.exec(global_pos)

        except Exception as e:
            logger.error(f"Erro ao exibir menu de contexto do mês no calendário anual: {e}", exc_info=True)

    def _on_month_clicked(self, month: int):
        try:
            self._selected_month = int(month)
            self._refresh_month_buttons()
            self.monthSelected.emit(self.selectedDate())

        except Exception as e:
            logger.error(f"Erro ao selecionar mês no calendário anual: {e}", exc_info=True)

    def _refresh_header(self):
        text = str(self._year)

        if self.year_label.text() != text:
            self.year_label.setText(text)

    def _refresh_month_buttons(self):
        for idx, button in enumerate(self._month_buttons, start=1):
            month_name = self._locale.standaloneMonthName(idx, QLocale.ShortFormat) or self._locale.monthName(idx, QLocale.ShortFormat)

            if not month_name:
                month_name = QDate(self._year, idx, 1).toString("MMM")

            count = int(self._month_counts.get((self._year, idx), 0) or 0)
            label = month_name.capitalize()

            if count > 0:
                label = f"{label}\n{count}"

            if button.text() != label:
                button.setText(label)

            should_be_checked = idx == self._selected_month

            if button.isChecked() != should_be_checked:
                button.setChecked(should_be_checked)

            has_tasks = bool(count > 0)
            current_has_tasks = bool(button.property("hasTasks"))

            if current_has_tasks != has_tasks:
                button.setProperty("hasTasks", has_tasks)
                button.style().unpolish(button)
                button.style().polish(button)

            lines = self._month_tooltips.get((self._year, idx), []) or []
            tooltip_text = "\n".join(lines) if lines else ""

            if button.toolTip() != tooltip_text:
                button.setToolTip(tooltip_text)

    def _apply_palette_style(self):
        try:
            if self._styling_in_progress:
                return

            self._styling_in_progress = True
            pal = self.palette()
            base_color = pal.base().color()
            is_light_base = base_color.lightness() >= 128
            border_color = base_color.darker(135) if is_light_base else base_color.lighter(150)
            border = border_color.name()
            base_bg = base_color.name()
            text = pal.text().color().name()
            highlight = pal.highlight().color().name()
            highlight_text = pal.highlightedText().color().name()

            self.setStyleSheet(
                f"""
                QToolButton {{
                    border: 1px solid {border};
                    border-radius: 8px;
                    padding: 6px;
                    background: {base_bg};
                    color: {text};
                    font-weight: 600;
                }}
                QToolButton:hover {{
                    background: {base_bg};
                    border: 1px solid {highlight};
                }}
                QToolButton[hasTasks="true"] {{
                    border: 1px solid {highlight};
                }}
                QToolButton:checked {{
                    background: {highlight};
                    color: {highlight_text};
                }}
                """
            )

            for button in self._month_buttons:
                button.style().unpolish(button)
                button.style().polish(button)
                button.update()

        except Exception as e:
            logger.error(f"Erro ao aplicar estilo no calendário anual: {e}", exc_info=True)

        finally:
            self._styling_in_progress = False

    def _install_theme_sync(self):
        try:
            class _ThemeSyncFilter(QObject):
                def __init__(self, owner):
                    super().__init__(owner)
                    self.owner = owner

                def eventFilter(self, obj, event):
                    try:
                        qt_app = QApplication.instance()

                        if qt_app is None or obj is not qt_app:
                            return super().eventFilter(obj, event)

                        event_types = (
                            QEvent.ApplicationPaletteChange,
                            QEvent.ThemeChange,
                        )

                        try:
                            event_types = event_types + (QEvent.ColorSchemeChange,)

                        except AttributeError:
                            pass

                        if event.type() in event_types:
                            self.owner._apply_palette_style()

                    except Exception:
                        pass

                    return super().eventFilter(obj, event)

            qt_app = QApplication.instance()

            if qt_app is not None:
                self._theme_sync_filter = _ThemeSyncFilter(self)
                qt_app.installEventFilter(self._theme_sync_filter)

        except Exception as e:
            logger.error(f"Erro ao instalar sincronização de tema no calendário anual: {e}", exc_info=True)
