# -*- coding: utf-8 -*-
import json
import pytest
from path import Path

from py_pkpass.models import (
    Barcode, BarcodeFormat, Pass, StoreCard, 
    BoardingPass, Coupon, EventTicket, Generic,
    TransitType
)

cwd = Path(__file__).parent

def test_boarding_pass():
    """Test creating a boarding pass."""
    # Create a boarding pass for air travel
    boarding_info = BoardingPass(TransitType.AIR)
    
    # Add header fields
    boarding_info.addHeaderField('gate', 'B12', 'Gate')
    boarding_info.addHeaderField('date', '2023-06-15', 'Date')
    
    # Add primary fields
    boarding_info.addPrimaryField('origin', 'SFO', 'San Francisco')
    boarding_info.addPrimaryField('destination', 'JFK', 'New York')
    
    # Add secondary fields
    boarding_info.addSecondaryField('passenger', 'John Doe', 'Passenger')
    boarding_info.addSecondaryField('class', 'Business', 'Class')
    
    # Add auxiliary fields
    boarding_info.addAuxiliaryField('boardingTime', '10:25 AM', 'Boarding')
    boarding_info.addAuxiliaryField('flightNumber', 'AA123', 'Flight')
    
    # Add back fields
    boarding_info.addBackField('terms', 'Terms and conditions apply.', 'Terms')
    
    # Create pass instance
    barcode = Barcode('BOARDINGPASS123', BarcodeFormat.QR, 'Boarding Pass')
    passfile = Pass(
        boarding_info,
        organizationName='Test Airlines',
        passTypeIdentifier='pass.com.testairlines.boardingpass',
        teamIdentifier='AB12CD34EF'
    )
    passfile.barcode = barcode
    passfile.serialNumber = 'ABCD1234'
    passfile.description = 'Test Airlines Boarding Pass'
    
    # Test the JSON structure
    pass_json = passfile.json_dict()
    
    # Check pass type
    assert 'boardingPass' in pass_json
    assert pass_json['boardingPass']['transitType'] == TransitType.AIR
    
    # Check fields
    assert len(pass_json['boardingPass']['headerFields']) == 2
    assert len(pass_json['boardingPass']['primaryFields']) == 2
    assert len(pass_json['boardingPass']['secondaryFields']) == 2
    assert len(pass_json['boardingPass']['auxiliaryFields']) == 2
    assert len(pass_json['boardingPass']['backFields']) == 1
    
    # Check specific field values
    assert pass_json['boardingPass']['primaryFields'][0]['key'] == 'origin'
    assert pass_json['boardingPass']['primaryFields'][0]['value'] == 'SFO'
    assert pass_json['boardingPass']['secondaryFields'][1]['key'] == 'class'
    assert pass_json['boardingPass']['secondaryFields'][1]['value'] == 'Business'

def test_event_ticket():
    """Test creating an event ticket."""
    # Create an event ticket
    event_info = EventTicket()
    
    # Add header fields
    event_info.addHeaderField('venue', 'Concert Hall', 'Venue')
    
    # Add primary fields
    event_info.addPrimaryField('event', 'Summer Concert', 'Event')
    event_info.addPrimaryField('date', 'June 15, 2023', 'Date')
    
    # Add secondary fields
    event_info.addSecondaryField('location', '123 Main St', 'Location')
    event_info.addSecondaryField('time', '8:00 PM', 'Time')
    
    # Add auxiliary fields
    event_info.addAuxiliaryField('section', 'A', 'Section')
    event_info.addAuxiliaryField('row', '15', 'Row')
    event_info.addAuxiliaryField('seat', '27', 'Seat')
    
    # Create pass instance
    barcode = Barcode('EVENT123456', BarcodeFormat.QR, 'Event Ticket')
    passfile = Pass(
        event_info,
        organizationName='Test Events',
        passTypeIdentifier='pass.com.testevents.ticket',
        teamIdentifier='AB12CD34EF'
    )
    passfile.barcode = barcode
    passfile.serialNumber = 'EVENT123456'
    passfile.description = 'Test Events Concert Ticket'
    
    # Test the JSON structure
    pass_json = passfile.json_dict()
    
    # Check pass type
    assert 'eventTicket' in pass_json
    
    # Check fields
    assert len(pass_json['eventTicket']['headerFields']) == 1
    assert len(pass_json['eventTicket']['primaryFields']) == 2
    assert len(pass_json['eventTicket']['secondaryFields']) == 2
    assert len(pass_json['eventTicket']['auxiliaryFields']) == 3
    
    # Check specific field values
    assert pass_json['eventTicket']['primaryFields'][0]['key'] == 'event'
    assert pass_json['eventTicket']['primaryFields'][0]['value'] == 'Summer Concert'
    assert pass_json['eventTicket']['auxiliaryFields'][2]['key'] == 'seat'
    assert pass_json['eventTicket']['auxiliaryFields'][2]['value'] == '27'

def test_coupon():
    """Test creating a coupon."""
    # Create a coupon
    coupon_info = Coupon()
    
    # Add primary fields
    coupon_info.addPrimaryField('offer', '20% OFF', 'Offer')
    
    # Add secondary fields
    coupon_info.addSecondaryField('expires', 'Dec 31, 2023', 'Expires')
    
    # Add auxiliary fields
    coupon_info.addAuxiliaryField('promocode', 'SUMMER20', 'Promo Code')
    
    # Add back fields
    coupon_info.addBackField('terms', 'Cannot be combined with other offers.', 'Terms')
    coupon_info.addBackField('locations', 'Valid at all retail locations.', 'Locations')
    
    # Create pass instance
    barcode = Barcode('COUPON123456', BarcodeFormat.QR, 'Coupon Code')
    passfile = Pass(
        coupon_info,
        organizationName='Test Store',
        passTypeIdentifier='pass.com.teststore.coupon',
        teamIdentifier='AB12CD34EF'
    )
    passfile.barcode = barcode
    passfile.serialNumber = 'COUPON123456'
    passfile.description = 'Test Store Discount Coupon'
    passfile.backgroundColor = 'rgb(255, 240, 240)'
    passfile.foregroundColor = 'rgb(180, 0, 0)'
    
    # Test the JSON structure
    pass_json = passfile.json_dict()
    
    # Check pass type
    assert 'coupon' in pass_json
    
    # Check fields
    assert len(pass_json['coupon']['primaryFields']) == 1
    assert len(pass_json['coupon']['secondaryFields']) == 1
    assert len(pass_json['coupon']['auxiliaryFields']) == 1
    assert len(pass_json['coupon']['backFields']) == 2
    
    # Check specific field values
    assert pass_json['coupon']['primaryFields'][0]['key'] == 'offer'
    assert pass_json['coupon']['primaryFields'][0]['value'] == '20% OFF'
    assert pass_json['coupon']['backFields'][0]['key'] == 'terms'
    
    # Check colors
    assert pass_json['backgroundColor'] == 'rgb(255, 240, 240)'
    assert pass_json['foregroundColor'] == 'rgb(180, 0, 0)'

def test_generic_pass():
    """Test creating a generic pass."""
    # Create a generic pass
    generic_info = Generic()
    
    # Add header fields
    generic_info.addHeaderField('type', 'Membership Card', 'Type')
    
    # Add primary fields
    generic_info.addPrimaryField('name', 'John Doe', 'Member Name')
    
    # Add secondary fields
    generic_info.addSecondaryField('number', 'M123456789', 'Member #')
    generic_info.addSecondaryField('since', 'Jan 2023', 'Member Since')
    
    # Add auxiliary fields
    generic_info.addAuxiliaryField('level', 'Gold', 'Level')
    
    # Add back fields
    generic_info.addBackField('website', 'www.example.com', 'Website')
    generic_info.addBackField('contact', '+1 (800) 123-4567', 'Contact')
    
    # Create pass instance
    barcode = Barcode('M123456789', BarcodeFormat.CODE128, 'Membership Number')
    passfile = Pass(
        generic_info,
        organizationName='Test Club',
        passTypeIdentifier='pass.com.testclub.membership',
        teamIdentifier='AB12CD34EF'
    )
    passfile.barcode = barcode
    passfile.serialNumber = 'MEMBER123456'
    passfile.description = 'Test Club Membership Card'
    passfile.backgroundColor = 'rgb(20, 20, 20)'
    passfile.foregroundColor = 'rgb(230, 180, 0)'
    passfile.logoText = 'TEST CLUB'
    
    # Test the JSON structure
    pass_json = passfile.json_dict()
    
    # Check pass type
    assert 'generic' in pass_json
    
    # Check fields
    assert len(pass_json['generic']['headerFields']) == 1
    assert len(pass_json['generic']['primaryFields']) == 1
    assert len(pass_json['generic']['secondaryFields']) == 2
    assert len(pass_json['generic']['auxiliaryFields']) == 1
    assert len(pass_json['generic']['backFields']) == 2
    
    # Check specific field values
    assert pass_json['generic']['headerFields'][0]['key'] == 'type'
    assert pass_json['generic']['headerFields'][0]['value'] == 'Membership Card'
    assert pass_json['generic']['secondaryFields'][0]['key'] == 'number'
    assert pass_json['generic']['secondaryFields'][0]['value'] == 'M123456789'
    
    # Check other pass settings
    assert pass_json['logoText'] == 'TEST CLUB'
    assert pass_json['backgroundColor'] == 'rgb(20, 20, 20)'
    assert pass_json['foregroundColor'] == 'rgb(230, 180, 0)'
    
def test_store_card():
    """Test creating a store card."""
    # Create a store card
    store_info = StoreCard()
    
    # Add header fields
    store_info.addHeaderField('balance', '$250.00', 'Balance')
    
    # Add primary fields
    store_info.addPrimaryField('name', 'John Doe', 'Cardholder')
    
    # Add secondary fields
    store_info.addSecondaryField('number', '6789 1234 5678 9012', 'Card Number')
    
    # Add auxiliary fields
    store_info.addAuxiliaryField('level', 'Platinum', 'Member Level')
    store_info.addAuxiliaryField('points', '1,200', 'Reward Points')
    
    # Add back fields
    store_info.addBackField('terms', 'Earn 1 point for every $1 spent.', 'Rewards Terms')
    
    # Create pass instance
    barcode = Barcode('6789123456789012', BarcodeFormat.CODE128, 'Card Number')
    passfile = Pass(
        store_info,
        organizationName='Test Retail',
        passTypeIdentifier='pass.com.testretail.storecard',
        teamIdentifier='AB12CD34EF'
    )
    passfile.barcode = barcode
    passfile.serialNumber = 'CARD123456'
    passfile.description = 'Test Retail Store Card'
    
    # Test the JSON structure
    pass_json = passfile.json_dict()
    
    # Check pass type
    assert 'storeCard' in pass_json
    
    # Check fields
    assert len(pass_json['storeCard']['headerFields']) == 1
    assert len(pass_json['storeCard']['primaryFields']) == 1
    assert len(pass_json['storeCard']['secondaryFields']) == 1
    assert len(pass_json['storeCard']['auxiliaryFields']) == 2
    assert len(pass_json['storeCard']['backFields']) == 1
    
    # Check specific field values
    assert pass_json['storeCard']['headerFields'][0]['key'] == 'balance'
    assert pass_json['storeCard']['headerFields'][0]['value'] == '$250.00'
    assert pass_json['storeCard']['primaryFields'][0]['key'] == 'name'
    assert pass_json['storeCard']['primaryFields'][0]['value'] == 'John Doe'

def test_transit_types():
    """Test different transit types for boarding passes."""
    # Test all transit types
    transit_types = [
        TransitType.AIR,
        TransitType.TRAIN,
        TransitType.BUS,
        TransitType.BOAT,
        TransitType.GENERIC
    ]
    
    for transit_type in transit_types:
        # Create a boarding pass
        boarding_info = BoardingPass(transit_type)
        boarding_info.addPrimaryField('route', 'Route 1', 'Route')
        
        # Create pass instance
        passfile = Pass(
            boarding_info,
            organizationName='Test Transit',
            passTypeIdentifier='pass.com.testtransit.boardingpass',
            teamIdentifier='AB12CD34EF'
        )
        passfile.serialNumber = f'TRANSIT{transit_type}'
        passfile.description = f'Test Transit {transit_type} Pass'
        
        # Test the JSON structure
        pass_json = passfile.json_dict()
        
        # Check transit type
        assert pass_json['boardingPass']['transitType'] == transit_type 