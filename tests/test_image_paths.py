"""Tests for image storage-key persistence (LP-913).

Storage keys were not round-tripped by save_settings, so after a reload the
block no longer knew which file belonged to a card. These tests are independent
of which authoring editor the block uses.
"""
from unittest.mock import Mock

from xblock.field_data import DictFieldData
from xblock.fields import ScopeIds

from games.constants import UPLOAD
from games.games import GamesXBlock
from games.handlers.common import CommonHandlers

BLOCK_ID = "1234567890abcdef1234567890abcdef"


def _make_block():
    usage_id = Mock()
    usage_id.block_id = BLOCK_ID
    scope_ids = ScopeIds("user", "games", "def", usage_id)
    block = GamesXBlock(Mock(), DictFieldData({}), scope_ids)
    block.game_type = "flashcards"
    block.cards = [{"term": "a", "definition": "b"}]
    block.is_shuffled = True
    block.has_timer = False
    block.display_name = "Games"
    return block


def test_save_settings_persists_image_paths():
    """Storage keys must round-trip, or the card loses track of its file."""
    xblock = _make_block()
    result = CommonHandlers.save_settings(xblock, {
        "game_type": "flashcards",
        "cards": [{
            "term": "t",
            "definition": "d",
            "term_image": "http://example.com/i.png",
            "term_image_path": f"{UPLOAD.PATH_PREFIX}/{BLOCK_ID}/d41d8cd98f00b204e9800998ecf8427e.png",
            "definition_image_path": f"{UPLOAD.PATH_PREFIX}/{BLOCK_ID}/other.png",
        }],
    })
    assert result["success"] is True
    card = xblock.cards[0]
    assert card["term_image_path"] == f"{UPLOAD.PATH_PREFIX}/{BLOCK_ID}/d41d8cd98f00b204e9800998ecf8427e.png"
    assert card["definition_image_path"] == f"{UPLOAD.PATH_PREFIX}/{BLOCK_ID}/other.png"


def test_save_settings_tolerates_cards_without_image_paths():
    """Content authored before this change has no *_image_path keys."""
    xblock = _make_block()
    CommonHandlers.save_settings(xblock, {
        "game_type": "flashcards",
        "cards": [{"term": "t", "definition": "d"}],
    })
    assert xblock.cards[0]["term_image_path"] == ""


def test_save_settings_drops_keys_that_are_not_this_blocks():
    """A key for another block, a traversal, or a non-string is never persisted.

    The keys come from the client and are meant to drive a later cleanup, and
    the storage bucket is shared by the whole platform.
    """
    xblock = _make_block()
    CommonHandlers.save_settings(xblock, {
        "game_type": "flashcards",
        "cards": [
            {"term": "t", "definition": "d",
             "term_image_path": f"{UPLOAD.PATH_PREFIX}/otherblock/x.png",
             "definition_image_path": f"{UPLOAD.PATH_PREFIX}/{BLOCK_ID}/../x.png"},
            {"term": "t", "definition": "d",
             "term_image_path": "../../etc/passwd",
             "definition_image_path": 123},
        ],
    })
    for card in xblock.cards:
        assert card["term_image_path"] == ""
        assert card["definition_image_path"] == ""
