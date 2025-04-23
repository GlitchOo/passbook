# -*- coding: utf-8 -*-
import json
import pytest
from path import Path

from py_pkpass.models import (
    Barcode, BarcodeFormat, Pass, StoreCard, 
    Location, IBeacon, DateField, NumberField, 
    DateStyle, NumberStyle, Alignment
)

cwd = Path(__file__).parent

def create_base_pass():
    """Create a base pass for testing."""
    card_info = StoreCard()
    card_info.addPrimaryField('name', 'John Doe', 'Name')
    barcode = Barcode('test barcode', BarcodeFormat.QR, 'alternate text')
    passfile = Pass(
        card_info, 
        organizationName='Test Organization', 
        passTypeIdentifier='pass.com.test.pkpass', 
        teamIdentifier='AB12CD34EF'
    )
    passfile.barcode = barcode
    passfile.serialNumber = '12345678'
    passfile.description = 'Test Pass'
    return passfile

def test_location_feature():
    """Test adding location data to a pass."""
    passfile = create_base_pass()
    
    # Test adding a single location
    location = Location(37.7749, -122.4194, 12.0)
    location.relevantText = "You're near the location!"
    passfile.locations = [location.json_dict()]
    
    pass_json = passfile.json_dict()
    assert 'locations' in pass_json
    assert len(pass_json['locations']) == 1
    assert pass_json['locations'][0]['latitude'] == 37.7749
    assert pass_json['locations'][0]['longitude'] == -122.4194
    assert pass_json['locations'][0]['altitude'] == 12.0
    assert pass_json['locations'][0]['relevantText'] == "You're near the location!"
    
    # Test adding multiple locations
    location2 = Location(40.7128, -74.0060)
    location2.relevantText = "Welcome to New York!"
    passfile.locations = [location.json_dict(), location2.json_dict()]
    
    pass_json = passfile.json_dict()
    assert len(pass_json['locations']) == 2
    assert pass_json['locations'][1]['latitude'] == 40.7128
    assert pass_json['locations'][1]['longitude'] == -74.0060
    assert pass_json['locations'][1]['relevantText'] == "Welcome to New York!"

def test_ibeacon_feature():
    """Test adding iBeacon data to a pass."""
    passfile = create_base_pass()
    
    # Test adding a single iBeacon
    beacon = IBeacon('E2C56DB5-DFFB-48D2-B060-D0F5A71096E0', 100, 1)
    beacon.relevantText = "You're near an iBeacon!"
    passfile.ibeacons = [beacon.json_dict()]
    
    pass_json = passfile.json_dict()
    assert 'beacons' in pass_json
    assert len(pass_json['beacons']) == 1
    assert pass_json['beacons'][0]['proximityUUID'] == 'E2C56DB5-DFFB-48D2-B060-D0F5A71096E0'
    assert pass_json['beacons'][0]['major'] == 100
    assert pass_json['beacons'][0]['minor'] == 1
    assert pass_json['beacons'][0]['relevantText'] == "You're near an iBeacon!"
    
    # Test adding multiple iBeacons
    beacon2 = IBeacon('A4C56DB5-EFFB-48D2-B060-D0F5A71096E0', 200, 2)
    beacon2.relevantText = "Another iBeacon detected!"
    passfile.ibeacons = [beacon.json_dict(), beacon2.json_dict()]
    
    pass_json = passfile.json_dict()
    assert len(pass_json['beacons']) == 2
    assert pass_json['beacons'][1]['proximityUUID'] == 'A4C56DB5-EFFB-48D2-B060-D0F5A71096E0'
    assert pass_json['beacons'][1]['major'] == 200
    assert pass_json['beacons'][1]['minor'] == 2
    assert pass_json['beacons'][1]['relevantText'] == "Another iBeacon detected!"

def test_date_field():
    """Test date field functionality."""
    passfile = create_base_pass()
    
    # Test date field with different styles
    date_field = DateField('eventDate', '2023-05-15T19:00:00-08:00', 'Event Date', 
                          dateStyle=DateStyle.LONG, timeStyle=DateStyle.SHORT)
    passfile.passInformation.addPrimaryField('eventDate', date_field.value, date_field.label)
    passfile.passInformation.primaryFields[-1] = date_field
    
    pass_json = passfile.json_dict()
    assert pass_json['storeCard']['primaryFields'][1]['key'] == 'eventDate'
    assert pass_json['storeCard']['primaryFields'][1]['value'] == '2023-05-15T19:00:00-08:00'
    assert pass_json['storeCard']['primaryFields'][1]['dateStyle'] == DateStyle.LONG
    assert pass_json['storeCard']['primaryFields'][1]['timeStyle'] == DateStyle.SHORT

def test_number_field():
    """Test number field functionality."""
    passfile = create_base_pass()
    
    # Test number field with different styles
    number_field = NumberField('score', 95, 'Score')
    number_field.numberStyle = NumberStyle.PERCENT
    passfile.passInformation.addSecondaryField('score', number_field.value, number_field.label)
    passfile.passInformation.secondaryFields[-1] = number_field
    
    pass_json = passfile.json_dict()
    assert pass_json['storeCard']['secondaryFields'][0]['key'] == 'score'
    assert pass_json['storeCard']['secondaryFields'][0]['value'] == 95
    assert pass_json['storeCard']['secondaryFields'][0]['numberStyle'] == NumberStyle.PERCENT

def test_text_alignment():
    """Test field text alignment."""
    passfile = create_base_pass()
    
    # Test field with different alignment
    field = passfile.passInformation.addPrimaryField('title', 'Centered Title', 'Title')
    field = passfile.passInformation.primaryFields[-1]
    field.textAlignment = Alignment.CENTER
    
    pass_json = passfile.json_dict()
    assert pass_json['storeCard']['primaryFields'][1]['textAlignment'] == Alignment.CENTER

def test_nfc_feature():
    """Test NFC feature in a pass."""
    passfile = create_base_pass()
    
    # Test adding NFC data
    nfc_message = "NFCURL:https://example.com/nfc"
    encryption_key = "MIIBCgKCAQEAxDvxODqrGm3kIcV9Hk2TMR9EyDV5CRdZPUhKw+fkOQDyGJnRFcrO1u7ghn8not5YFuQJH5DKGmSfQOQYfR/1anv/96WjeOdoFn40OGVL3hJRKpJFGM1S9W5MrSjriiUCx7olHxWE8r+aMXG9Gt4NyDWyJAFfMZew5qfUYIZ6RWLQ9LSLkS2UeKFzrnvZSqDI0gJoKXUjpfdpfR6LIEXyJNidtH0ejhXY5yvf+C+HvuNnKtPOp6c8hJB8OYz8P9kTKZ2qPe5eiG0+G0FY3O7FjgMp8K5a6FgOjNW4OyY3s4Xpb9r0zUyBsg9z4h5Y6yvIpWMcE0Y+lfO+JQXXlwIDAQAB"
    passfile.nfc_message = nfc_message
    passfile.encryption_public_key = encryption_key
    passfile.requiresAuthentication = True
    
    pass_json = passfile.json_dict()
    assert 'nfc' in pass_json
    assert pass_json['nfc']['message'] == nfc_message
    assert pass_json['nfc']['encryptionPublicKey'] == encryption_key
    assert pass_json['nfc']['requiresAuthentication'] == True

def test_sharing_prohibited():
    """Test sharingProhibited flag."""
    passfile = create_base_pass()
    
    # Test sharingProhibited flag
    passfile.sharingProhibited = True
    
    pass_json = passfile.json_dict()
    assert pass_json['sharingProhibited'] == True

def test_web_service_features():
    """Test web service features."""
    passfile = create_base_pass()
    
    # Test web service settings
    passfile.webServiceURL = "https://example.com/passes/"
    passfile.authenticationToken = "abc123def456"
    
    pass_json = passfile.json_dict()
    assert pass_json['webServiceURL'] == "https://example.com/passes/"
    assert pass_json['authenticationToken'] == "abc123def456"

def test_associated_store_identifiers():
    """Test associated store identifiers."""
    passfile = create_base_pass()
    
    # Test associated store identifiers
    passfile.associatedStoreIdentifiers = [123456789, 987654321]
    
    pass_json = passfile.json_dict()
    assert pass_json['associatedStoreIdentifiers'] == [123456789, 987654321]

def test_expiration_and_voided():
    """Test expiration date and voided flag."""
    passfile = create_base_pass()
    
    # Test expiration date
    passfile.expirationDate = "2023-12-31T23:59:59+00:00"
    
    pass_json = passfile.json_dict()
    assert pass_json['expirationDate'] == "2023-12-31T23:59:59+00:00"
    
    # Test voided flag
    passfile.voided = True
    
    pass_json = passfile.json_dict()
    assert pass_json['voided'] == True

def test_color_settings():
    """Test color settings."""
    passfile = create_base_pass()
    
    # Test color settings
    passfile.backgroundColor = "rgb(61, 152, 60)"
    passfile.foregroundColor = "rgb(255, 255, 255)"
    passfile.labelColor = "rgb(255, 255, 255)"
    
    pass_json = passfile.json_dict()
    assert pass_json['backgroundColor'] == "rgb(61, 152, 60)"
    assert pass_json['foregroundColor'] == "rgb(255, 255, 255)"
    assert pass_json['labelColor'] == "rgb(255, 255, 255)" 