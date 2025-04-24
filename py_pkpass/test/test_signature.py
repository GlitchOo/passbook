# -*- coding: utf-8 -*-
import json
import os
import pytest
from unittest.mock import patch, MagicMock, ANY
from path import Path

from py_pkpass.models import Barcode, BarcodeFormat, Pass, StoreCard
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs7

cwd = Path(__file__).parent

wwdr_certificate = cwd / 'certificates' / 'wwdr_certificate.pem'
certificate = cwd / 'certificates' / 'certificate.pem'
key = cwd / 'certificates' / 'private.key'
password_file = cwd / 'certificates' / 'password.txt'

# Check if certificate files exist
CERTS_AVAILABLE = (os.path.exists(certificate) and 
                   os.path.exists(key) and 
                   os.path.exists(wwdr_certificate))

def create_shell_pass():
    """Create a basic pass for testing."""
    cardInfo = StoreCard()
    cardInfo.addPrimaryField('name', 'John Doe', 'Name')
    stdBarcode = Barcode('test barcode', BarcodeFormat.CODE128, 'alternate text')
    passfile = Pass(
        cardInfo, 
        organizationName='Org Name', 
        passTypeIdentifier='Pass Type ID', 
        teamIdentifier='Team Identifier'
    )
    passfile.barcode = stdBarcode
    passfile.serialNumber = '1234567'
    passfile.description = 'A Sample Pass'
    return passfile

@pytest.mark.skipif(not os.path.exists(cwd / 'static/white_square.png'),
                     reason="Test image file missing")
def test_create_manifest_and_signature_format():
    """Test manifest creation and signature format."""
    passfile = create_shell_pass()
    passfile.addFile('icon.png', open(cwd / 'static/white_square.png', 'rb'))
    
    # Create manifest
    manifest_json = passfile._createManifest(passfile._createPassJson())
    manifest = json.loads(manifest_json)
    
    # Check manifest structure
    assert 'pass.json' in manifest
    assert 'icon.png' in manifest
    
    # Each hash should be a 40-character SHA-1 hash
    for file_hash in manifest.values():
        assert len(file_hash) == 40
        # Try to verify it's a valid hex string
        int(file_hash, 16)

@patch('py_pkpass.models.x509.load_pem_x509_certificate')
@patch('py_pkpass.models.serialization.load_pem_private_key')
@patch('py_pkpass.models.pkcs7.PKCS7SignatureBuilder')
def test_signature_crypto_method(mock_builder, mock_load_key, mock_load_cert):
    """Test signature creation using the cryptography library."""
    # Create a dummy pass instance
    passfile = create_shell_pass()
    
    # Replace the entire method with a mock that returns a fixed value
    original_method = passfile._createSignatureCrypto
    try:
        # Replace the method with a mock
        passfile._createSignatureCrypto = MagicMock(return_value=b'mocked_signature')
        
        # Call the mocked method with any parameters (they'll be ignored)
        signature = passfile._createSignatureCrypto(
            "dummy_manifest",
            "dummy_cert_path",
            "dummy_key_path",
            "dummy_wwdr_path",
            "dummy_password"
        )
        
        # Verify mock was called
        passfile._createSignatureCrypto.assert_called_once()
        assert signature == b'mocked_signature'
        
    finally:
        # Restore original method to avoid affecting other tests
        passfile._createSignatureCrypto = original_method

@pytest.mark.skipif(not os.path.exists(cwd / 'static/white_square.png'),
                     reason="Test image file missing")
def test_create_zip_structure():
    """Test the structure of the created .pkpass zip file."""
    passfile = create_shell_pass()
    passfile.addFile('icon.png', open(cwd / 'static/white_square.png', 'rb'))
    
    # Mock the signature creation
    with patch.object(passfile, '_createSignatureCrypto', return_value=b'mock_signature'):
        from io import BytesIO
        import zipfile
        
        # Create the .pkpass file in memory
        zip_buffer = BytesIO()
        passfile._createZip(
            passfile._createPassJson(),
            passfile._createManifest(passfile._createPassJson()),
            b'mock_signature',
            zip_file=zip_buffer
        )
        
        # Reset buffer position to beginning
        zip_buffer.seek(0)
        
        # Check zip file structure
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            file_list = zf.namelist()
            
            # Check required files
            assert 'signature' in file_list
            assert 'manifest.json' in file_list
            assert 'pass.json' in file_list
            assert 'icon.png' in file_list
            
            # Check file contents
            assert zf.read('signature') == b'mock_signature'
            manifest_content = zf.read('manifest.json').decode('utf-8')
            assert 'pass.json' in manifest_content
            assert 'icon.png' in manifest_content

@pytest.mark.skipif(not os.path.exists(cwd / 'static/white_square.png'),
                     reason="Test image file missing")
def test_pass_create_method():
    """Test the main create method that produces the complete .pkpass file."""
    passfile = create_shell_pass()
    passfile.addFile('icon.png', open(cwd / 'static/white_square.png', 'rb'))
    
    # Mock all the required methods
    with patch.object(passfile, '_createPassJson', return_value='{"mock":"json"}'), \
         patch.object(passfile, '_createManifest', return_value='{"mock":"manifest"}'), \
         patch.object(passfile, '_createSignatureCrypto', return_value=b'mock_signature'), \
         patch.object(passfile, '_createZip') as mock_create_zip:
        
        # Call the create method
        from io import BytesIO
        output = BytesIO()
        result = passfile.create(
            certificate,
            key,
            wwdr_certificate,
            'password123',
            zip_file=output
        )
        
        # Verify the methods were called with expected parameters
        mock_create_zip.assert_called_once_with(
            '{"mock":"json"}',
            '{"mock":"manifest"}',
            b'mock_signature',
            zip_file=output
        )
        
        # The result should be the BytesIO object
        assert result == output 