from aqt import mw, gui_hooks
from aqt.utils import showInfo, qconnect
from anki.notes import Note
import aqt.qt

from . import config
from . import settings
from . import model
from . import deck

def start():
    # Load config
    config.load_config()

    def open_settings():
        window = settings.SettingsWindow()
        window.exec()

    def on_profile_loaded():
        # Create anki card model
        model.create_model()

        # Add settings tool button
        action = aqt.qt.QAction("Kanji Splitter", mw)
        qconnect(action.triggered, open_settings)
        mw.form.menuTools.addAction(action)

        # Add settings to addon page
        mw.addonManager.setConfigAction(__name__, open_settings)

    gui_hooks.profile_did_open.append(on_profile_loaded)

    # Listen for new notes in selected deck
    def addedNote(note: Note):  
        if not model.get_model():
            model.create_model()

        if note.has_tag(deck.get_tag()):
            return

        deckId = deck.get_deck_id()

        result = mw.col.db.scalar(
            "SELECT 1 FROM cards WHERE nid = ? AND did = ?", note.id, deckId
        )

        if result:
            deck.scan_note(note)
            
    gui_hooks.add_cards_did_add_note.append(addedNote)

    