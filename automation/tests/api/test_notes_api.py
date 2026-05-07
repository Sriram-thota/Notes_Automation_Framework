"""
test_notes_api.py — API automation: CRUD on Notes + performance + negative tests.
"""

import allure
import pytest

from api_client.notes_client import NotesClient


@allure.feature("Notes — API")
class TestNotesAPI:

    # ── GET /notes ─────────────────────────────────────────────────────────

    @allure.story("GET /notes")
    @allure.title("TC-API-01 | GET /notes returns 200 with a list")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_get_notes_returns_list(self, notes_client: NotesClient):
        notes = notes_client.get_all_notes()
        assert isinstance(notes, list), "Expected a list from GET /notes"

    @allure.story("GET /notes")
    @allure.title("TC-API-02 | GET /notes response time < 2 seconds")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_notes_performance(self, notes_client: NotesClient):
        # measure_time() inside get_all_notes() handles assertion
        notes_client.get_all_notes()

    @allure.story("GET /notes")
    @allure.title("TC-API-03 | GET /notes without auth token → 401")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_notes_no_auth(self, notes_client: NotesClient):
        resp = notes_client.get_notes_no_auth()
        assert resp.status_code == 401, (
            f"Expected 401 Unauthorized, got {resp.status_code}"
        )

    # ── POST /notes ────────────────────────────────────────────────────────

    @allure.story("POST /notes")
    @allure.title("TC-API-04 | Create note via API → note appears in GET /notes")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_create_note_appears_in_list(self, notes_client: NotesClient, note_data):
        created = notes_client.create_note(**note_data)

        assert created.get("id"), "Created note has no ID"
        assert created.get("title") == note_data["title"]
        assert created.get("description") == note_data["description"]

        notes = notes_client.get_all_notes()
        ids = [n["id"] for n in notes]
        assert created["id"] in ids, "Newly created note not found in GET /notes"

    @allure.story("POST /notes")
    @allure.title("TC-API-05 | Create note with empty title → 400 Bad Request")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_note_empty_title(self, notes_client: NotesClient):
        resp = notes_client.create_note_raw(
            {"title": "", "description": "No title given", "category": "Home"}
        )
        assert resp.status_code in (400, 422), (
            f"Expected 400/422 for empty title, got {resp.status_code}"
        )

    @allure.story("POST /notes")
    @allure.title("TC-API-06 | Create note missing required fields → 400")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_note_missing_fields(self, notes_client: NotesClient):
        resp = notes_client.create_note_raw({})
        assert resp.status_code in (400, 422)

    # ── DELETE /notes/{id} ─────────────────────────────────────────────────

    @allure.story("DELETE /notes")
    @allure.title("TC-API-07 | Delete note → no longer in GET /notes")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_delete_note_removed_from_list(self, notes_client: NotesClient, note_data):
        created = notes_client.create_note(**note_data)
        note_id = created["id"]

        deleted = notes_client.delete_note(note_id)
        assert deleted is True

        remaining_ids = [n["id"] for n in notes_client.get_all_notes()]
        assert note_id not in remaining_ids, (
            f"Deleted note id={note_id} still present in GET /notes"
        )

    @allure.story("DELETE /notes")
    @allure.title("TC-API-08 | Delete non-existent note → 404")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_nonexistent_note(self, notes_client: NotesClient):
        resp = notes_client.delete_note_raw("000000000000000000000000")
        assert resp.status_code == 404

    # ── Field Validation ──────────────────────────────────────────────────

    @allure.story("Response Schema")
    @allure.title("TC-API-09 | Note object contains all required fields")
    @allure.severity(allure.severity_level.NORMAL)
    def test_note_schema_completeness(self, notes_client: NotesClient, note_data):
        created = notes_client.create_note(**note_data)
        required_fields = {"id", "title", "description", "category", "completed"}
        missing = required_fields - set(created.keys())
        assert not missing, f"Note response missing fields: {missing}"
