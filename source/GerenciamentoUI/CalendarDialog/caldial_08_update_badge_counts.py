from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _update_badge_counts(self):
    try:
        task_dates = []
        for task in self._collect_tasks():
            date_str = task.get("date")
            if date_str:
                task_dates.append(date_str)
        
        calendars = self._iter_calendars() if hasattr(self, "_iter_calendars") else [self.calendar]

        for cal in calendars:
            if hasattr(cal, "set_task_counts"):
                cal.set_task_counts(task_dates)

    except Exception as e:
        logger.error(f"Erro ao atualizar contadores de badges: {e}", exc_info=True)
