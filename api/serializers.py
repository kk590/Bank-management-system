from typing import Any, Dict


def _common(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


def serialize_user(doc: Dict[str, Any]) -> Dict[str, Any]:
    doc = _common(doc)
    doc.pop("hashed_password", None)
    return doc


def serialize_account(doc: Dict[str, Any]) -> Dict[str, Any]:
    return _common(doc)


def serialize_transaction(doc: Dict[str, Any]) -> Dict[str, Any]:
    return _common(doc)
