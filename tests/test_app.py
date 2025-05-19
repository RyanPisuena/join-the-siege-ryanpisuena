from io import BytesIO

import pytest
from src.app import app, allowed_file

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.mark.parametrize("filename, expected", [
    ("file.pdf", True),
    ("file.png", True),
    ("file.jpg", True),
    ("file.jpeg", True),  # Added jpeg
    ("file.txt", False),
    ("file", False),
])

def test_allowed_file(filename, expected):
    assert allowed_file(filename) == expected

def test_no_file_in_request(client):
    response = client.post('/classify_file')
    assert response.status_code == 400
    assert response.get_json()['error'] == 'No file provided'
    assert response.get_json()['message'] == 'Please include a file in the request'

def test_no_selected_file(client):
    data = {'file': (BytesIO(b""), '')}  # Empty filename
    response = client.post('/classify_file', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.get_json()['error'] == 'No file selected'
    assert response.get_json()['message'] == 'Please select a file'

def test_invalid_file_type(client):
    data = {'file': (BytesIO(b"dummy content"), 'file.txt')}
    response = client.post('/classify_file', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.get_json()['error'] == 'Invalid file type'
    assert 'pdf' in response.get_json()['message']

def test_success_invoice(client):
    data = {'file': (BytesIO(b"dummy content"), 'invoice_1.pdf')}
    response = client.post('/classify_file', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['filename'] == 'invoice_1.pdf'
    assert json_data['classification'] == 'invoice'

def test_success_drivers_license(client):
    data = {'file': (BytesIO(b"dummy content"), 'drivers_license_1.jpg')}
    response = client.post('/classify_file', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['filename'] == 'drivers_license_1.jpg'
    assert json_data['classification'] == 'drivers_licence'

def test_success_bank_statement(client):
    data = {'file': (BytesIO(b"dummy content"), 'bank_statement_1.pdf')}
    response = client.post('/classify_file', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['filename'] == 'bank_statement_1.pdf'
    assert json_data['classification'] == 'bank_statement'

def test_unknown_file(client):
    data = {'file': (BytesIO(b"dummy content"), 'random_file.pdf')}
    response = client.post('/classify_file', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['classification'] == 'unknown file'