"""
notes_client.py - CRUD operations for Notes API endpoints.
All methods assert HTTP status automatically via BaseAPIClient.
"""

from typing import Dict, List, Optional

import requests

from api_client.base_client import BaseAPIClient
from utils.logger import get_logger
from utils.performance import measure_time

log = get_logger(__name__)


class NotesClient(BaseAPIClient):
    _NOTES     = "/notes"
    _NOTE_BY_ID = "/notes/{note_id}"

    # ?? Create ????????????????????????????????????????????????????????????

    def create_note(
        self,
        title: str,
        description: str,
        category: str = "Home",
    ) -> dict:
        """POST /notes - returns the created note dict."""
        payload = {"title": title, "description": description, "category": category}
        with measure_time("POST /notes"):
            resp = self.post(self._NOTES, json=payload, expected_status=200)
        body = self.json(resp)
        note = body.get("data", {})
        log.info("Note created via API: id=%s title='%s'", note.get("id"), title)
        return note

    # ?? Read ??????????????????????????????????????????????????????????????

    def get_all_notes(self) -> List[dict]:
        """GET /notes - returns list of note dicts, asserts < 2s."""
        with measure_time("GET /notes"):
            resp = self.get(self._NOTES, expected_status=200)
        body = self.json(resp)
        notes = body.get("data", [])
        log.info("GET /notes returned %d note(s)", len(notes))
        return notes

    def get_note_by_id(self, note_id: str) -> dict:
        endpoint = self._NOTE_BY_ID.format(note_id=note_id)
        with measure_time(f"GET {endpoint}"):
            resp = self.get(endpoint, expected_status=200)
        return self.json(resp).get("data", {})

    # ?? Update ????????????????????????????????????????????????????????????

    def update_note(
        self,
        note_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> dict:
        endpoint = self._NOTE_BY_ID.format(note_id=note_id)
        payload = {}
        if title:       payload["title"]       = title
        if description: payload["description"] = description
        if category:    payload["category"]    = category
        if completed is not None: payload["completed"] = completed
        resp = self.put(endpoint, json=payload, expected_status=200)
        return self.json(resp).get("data", {})

    # ?? Delete ????????????????????????????????????????????????????????????

    def delete_note(self, note_id: str) -> bool:
        endpoint = self._NOTE_BY_ID.format(note_id=note_id)
        with measure_time(f"DELETE {endpoint}"):
            resp = self.delete(endpoint, expected_status=200)
        body = self.json(resp)
        success = body.get("success", False)
        log.info("Note id=%s deleted: %s", note_id, success)
        return success

    # ?? Helpers ???????????????????????????????????????????????????????????

    def find_note_by_title(self, title: str) -> Optional[dict]:
        """Return first note whose title matches (case-sensitive)."""
        notes = self.get_all_notes()
        for note in notes:
            if note.get("title") == title:
                return note
        log.warning("Note with title '%s' not found via API", title)
        return None

    # ?? Negative-test helpers ?????????????????????????????????????????????

    def create_note_raw(self, payload: dict) -> requests.Response:
        """POST /notes without auto-asserting status - for negative tests."""
        return self.post(self._NOTES, json=payload)

    def delete_note_raw(self, note_id: str) -> requests.Response:
        endpoint = self._NOTE_BY_ID.format(note_id=note_id)
        return self.delete(endpoint)

    def get_notes_no_auth(self) -> requests.Response:
        """GET /notes without auth header - for 401 test."""
        import requests as req
        url = f"{self.base_url}{self._NOTES}"
        return req.get(url, timeout=5)
