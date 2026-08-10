import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend import database, models, seed_data
from backend.ai_service import mock_embed, cosine_similarity


@pytest.fixture(scope="module")
def client():
    # Explicitly trigger table creation & startup seeding for tests
    models.Base.metadata.create_all(bind=database.engine)
    db = database.SessionLocal()
    try:
        seed_data.seed_if_empty(db)
    finally:
        db.close()

    with TestClient(app) as c:
        yield c


def test_seed_dataset_and_list_students(client):
    """Verify initial database startup seeding of exact student dataset."""
    response = client.get("/students/")
    assert response.status_code == 200
    students = response.json()
    assert len(students) >= 9
    names = [s["name"] for s in students]
    assert "Aditi Rao" in names
    assert "Priya Iyer" in names


def test_min_age_filter(client):
    """Verify GET /students/?min_age=20 filters students with age >= 20."""
    response = client.get("/students/?min_age=20")
    assert response.status_code == 200
    students = response.json()
    for s in students:
        assert s["age"] >= 20


def test_student_validation_and_duplicate_email(client):
    """Verify Pydantic validation (missing '@' and negative age) and DB unique email constraint."""
    # Invalid email missing '@'
    resp = client.post("/students/", json={"name": "Test User", "email": "invalidemail.com", "age": 22})
    assert resp.status_code == 422

    # Negative age
    resp = client.post("/students/", json={"name": "Test User", "email": "test@example.com", "age": -5})
    assert resp.status_code == 422

    # Duplicate email rejection
    resp1 = client.post("/students/", json={"name": "Unique Test", "email": "aditi.rao@example.com", "age": 22})
    assert resp1.status_code == 400
    assert "already exists" in resp1.json()["detail"]


def test_student_crud_lifecycle(client):
    """Test full CRUD lifecycle for a Student record."""
    # Create
    create_resp = client.post("/students/", json={"name": "Karan Johar", "email": "karan.johar@example.com", "age": 24})
    assert create_resp.status_code == 201
    student = create_resp.json()
    student_id = student["id"]

    # Get Single
    get_resp = client.get(f"/students/{student_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Karan Johar"

    # Patch
    patch_resp = client.patch(f"/students/{student_id}", json={"age": 25})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["age"] == 25

    # Delete
    del_resp = client.delete(f"/students/{student_id}")
    assert del_resp.status_code == 200

    # Verify 404 after delete
    get_after_del = client.get(f"/students/{student_id}")
    assert get_after_del.status_code == 404


def test_course_count_endpoint(client):
    """Test GET /students/{student_id}/course-count aggregate endpoint."""
    # Get Aditi Rao's student ID
    students_resp = client.get("/students/")
    aditi = next(s for s in students_resp.json() if s["email"] == "aditi.rao@example.com")
    
    count_resp = client.get(f"/students/{aditi['id']}/course-count")
    assert count_resp.status_code == 200
    data = count_resp.json()
    assert data["student_id"] == aditi["id"]
    assert data["course_count"] >= 2

    # Nonexistent student 404
    bad_resp = client.get("/students/99999/course-count")
    assert bad_resp.status_code == 404


def test_insertion_sort_endpoint(client):
    """Test GET /students/sorted?by=age endpoint ordering."""
    response = client.get("/students/sorted?by=age")
    assert response.status_code == 200
    students = response.json()
    ages = [s["age"] for s in students]
    assert ages == sorted(ages)


def test_binary_search_endpoint(client):
    """Test GET /students/search?name= name lookup."""
    response = client.get("/students/search?name=Priya Iyer")
    assert response.status_code == 200
    match = response.json()
    assert match["name"] == "Priya Iyer"

    # Search non-existent
    bad_resp = client.get("/students/search?name=NonExistentPerson")
    assert bad_resp.status_code == 404


def test_roster_report_endpoint(client):
    """Test GET /students/report?min_age=21."""
    response = client.get("/students/report?min_age=21")
    assert response.status_code == 200
    data = response.json()
    assert "report" in data
    assert "count_meeting_min_age" in data
    assert isinstance(data["count_meeting_min_age"], int)


def test_ai_summarizer(client):
    """Test POST /assistant/summarize mock output schema and empty input handling."""
    # Non-empty input
    text = "Binary search requires a sorted array. It repeatedly halves search range."
    resp = client.post("/assistant/summarize", json={"text": text})
    assert resp.status_code == 200
    data = resp.json()
    assert set(data.keys()) == {"topic", "key_points", "difficulty"}
    assert isinstance(data["key_points"], list)
    assert len(data["key_points"]) > 0

    # Empty input edge case
    empty_resp = client.post("/assistant/summarize", json={"text": ""})
    assert empty_resp.status_code == 200
    empty_data = empty_resp.json()
    assert empty_data["topic"] == "untitled"
    assert empty_data["key_points"] == []
    assert empty_data["difficulty"] == "easy"


def test_ai_semantic_search(client):
    """Test GET /assistant/search?query= semantic search ranking and zero vector safety."""
    resp = client.get("/assistant/search?query=binary search algorithm")
    assert resp.status_code == 200
    notes = resp.json()
    assert len(notes) > 0
    # Note 1 should be ranked first
    assert notes[0]["id"] == 1

    # Empty query zero-vector safety
    empty_query_resp = client.get("/assistant/search?query=")
    assert empty_query_resp.status_code == 200
    all_zero_notes = empty_query_resp.json()
    for n in all_zero_notes:
        assert n["score"] == 0.0


def test_cosine_similarity_zero_vectors():
    """Verify first-principles cosine_similarity does not divide by zero."""
    v_zero = [0.0] * 12
    v_nonzero = mock_embed("binary search")

    assert cosine_similarity(v_zero, v_nonzero) == 0.0
    assert cosine_similarity(v_zero, v_zero) == 0.0
    assert cosine_similarity(v_nonzero, v_nonzero) == 1.0
