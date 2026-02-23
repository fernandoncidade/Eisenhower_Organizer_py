from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def _quadrant_options(app, include_completed: bool = False):
    try:
        pending = [
            app.quadrant1_label.text(),
            app.quadrant2_label.text(),
            app.quadrant3_label.text(),
            app.quadrant4_label.text(),
        ]

        if not include_completed:
            return pending

        completed = [
            app.quadrant1_completed_label.text(),
            app.quadrant2_completed_label.text(),
            app.quadrant3_completed_label.text(),
            app.quadrant4_completed_label.text(),
        ]
        return pending + completed

    except Exception as e:
        logger.error(f"Error getting quadrant options: {e}", exc_info=True)
        return []
