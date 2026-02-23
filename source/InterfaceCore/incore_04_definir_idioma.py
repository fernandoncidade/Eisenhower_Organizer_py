from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QCoreApplication
from source.utils.LogManager import LogManager
logger = LogManager.get_logger()

def get_text(text):
    return QCoreApplication.translate("InterfaceGrafica", text)

def definir_idioma(app, codigo_idioma):
    idioma_nome = str(codigo_idioma or "").strip()

    try:
        try:
            idioma_nome = app.gerenciador_traducao.idiomas_disponiveis.get(codigo_idioma, idioma_nome)

        except Exception:
            pass

        resultado = bool(app.gerenciador_traducao.definir_idioma(codigo_idioma))

        try:
            if hasattr(app, "idioma_menu") and app.idioma_menu is not None:
                for acao in app.idioma_menu.actions():
                    acao.setChecked(acao.text() == idioma_nome)

        except Exception:
            pass

        try:
            if resultado:
                QMessageBox.information(
                    app,
                    get_text("Sucesso"),
                    (get_text('Idioma "{language}" aplicado com sucesso!') or 'Idioma "{language}" aplicado com sucesso!').replace("{language}", idioma_nome),
                )

            else:
                QMessageBox.warning(
                    app,
                    get_text("Erro"),
                    (get_text('Não foi possível aplicar o Idioma "{language}"!') or 'Não foi possível aplicar o Idioma "{language}"!').replace("{language}", idioma_nome),
                )

        except Exception:
            pass

        return resultado

    except Exception as e:
        logger.error(f"Erro ao definir idioma: {e}", exc_info=True)

        try:
            QMessageBox.warning(
                app,
                get_text("Erro"),
                (get_text('Não foi possível aplicar o Idioma "{language}"!') or 'Não foi possível aplicar o Idioma "{language}"!').replace("{language}", idioma_nome),
            )

        except Exception:
            pass

        return False
