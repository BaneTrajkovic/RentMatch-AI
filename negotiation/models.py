from django.db import models
from django.contrib.auth.models import User
import json

class Property(models.Model):
    """Property model based on Zillow-like rental property data"""
    # Basic identifiers
    zpid = models.CharField(max_length=50, primary_key=True)
    provider_listing_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Status
    status_type = models.CharField(max_length=50, blank=True)  # FOR_RENT, FOR_SALE, etc.
    status_text = models.CharField(max_length=100, blank=True)
    market_status = models.CharField(max_length=50, blank=True)  # "For Rent", "For Sale"
    
    # Price
    price = models.CharField(max_length=50, blank=True)  # Formatted price
    unformatted_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default="$")
    
    # Address
    address = models.TextField(blank=True)
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=20, blank=True)
    zipcode = models.CharField(max_length=20, blank=True)
    is_undisclosed_address = models.BooleanField(default=False)
    unit = models.CharField(max_length=100, blank=True, null=True)
    
    # Geolocation
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Property details
    beds = models.IntegerField(null=True, blank=True)
    baths = models.FloatField(null=True, blank=True)
    home_type = models.CharField(max_length=50, blank=True, null=True)
    
    # Images
    main_image_url = models.URLField(blank=True, null=True)
    has_image = models.BooleanField(default=False)
    has_video = models.BooleanField(default=False)
    has_3d_model = models.BooleanField(default=False)
    
    # Listing URLs
    detail_url = models.URLField(blank=True, null=True)
    
    # Features
    has_fireplace = models.BooleanField(default=False)
    has_air_conditioning = models.BooleanField(default=False)
    has_spa = models.BooleanField(default=False)
    has_pool = models.BooleanField(default=False)
    
    # Listing metadata
    days_on_market = models.IntegerField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_showcase = models.BooleanField(default=False)
    
    # Storage for additional data
    raw_json_data = models.JSONField(blank=True, null=True)
    carousel_photos = models.JSONField(blank=True, null=True)
    
    def __str__(self):
        address_text = self.address if self.address else f"{self.city}, {self.state}"
        return f"{address_text} - {self.price}"
    
    @classmethod
    def from_json(cls, json_data):
        """Create a Property instance from JSON data"""
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
            
        property_data = {
            'zpid': data.get('zpid', ''),
            'provider_listing_id': data.get('providerListingId', ''),
            'status_type': data.get('statusType', ''),
            'status_text': data.get('statusText', ''),
            'market_status': data.get('marketingStatusSimplifiedCd', ''),
            'price': data.get('price', ''),
            'unformatted_price': data.get('unformattedPrice'),
            'currency': data.get('countryCurrency', '$'),
            'address': data.get('address', ''),
            'street_address': data.get('addressStreet', ''),
            'city': data.get('addressCity', ''),
            'state': data.get('addressState', ''),
            'zipcode': data.get('addressZipcode', ''),
            'is_undisclosed_address': data.get('isUndisclosedAddress', False),
            'beds': data.get('beds'),
            'baths': data.get('baths'),
            'detail_url': data.get('detailUrl', ''),
            'has_image': data.get('hasImage', False),
            'has_video': data.get('hasVideo', False),
            'has_3d_model': data.get('has3DModel', False),
            'is_featured': data.get('isFeaturedListing', False),
            'is_showcase': data.get('isShowcaseListing', False),
            'main_image_url': data.get('imgSrc', ''),
            'raw_json_data': data,
            'carousel_photos': data.get('carouselPhotos', []),
        }
        
        # Extract lat/long from nested structure
        if 'latLong' in data and data['latLong']:
            property_data['latitude'] = data['latLong'].get('latitude')
            property_data['longitude'] = data['latLong'].get('longitude')
            
        # Extract from hdpData if available
        if 'hdpData' in data and 'homeInfo' in data['hdpData']:
            home_info = data['hdpData']['homeInfo']
            property_data['days_on_market'] = home_info.get('daysOnZillow')
            property_data['home_type'] = home_info.get('homeType', '').title()
            property_data['unit'] = home_info.get('unit', '')
            
            # If latitude/longitude wasn't found earlier
            if not property_data.get('latitude') and 'latitude' in home_info:
                property_data['latitude'] = home_info.get('latitude')
            if not property_data.get('longitude') and 'longitude' in home_info:
                property_data['longitude'] = home_info.get('longitude')
        
        # Extract features
        if 'factsAndFeatures' in data:
            facts = data['factsAndFeatures']
            property_data['has_fireplace'] = facts.get('hasFireplace', False)
            property_data['has_air_conditioning'] = facts.get('hasAirConditioning', False)
            property_data['has_spa'] = facts.get('hasSpa', False)
            property_data['has_pool'] = facts.get('hasPool', False)
            
        return cls(**property_data)

class PropertyChat(models.Model):
    """Chat between landlord and renter about a specific property"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='chats')
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='landlord_chats')
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='renter_chats')
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Chat about {self.property} between {self.landlord.username} and {self.renter.username}"
    
    def save(self, *args, **kwargs):
        # Auto-generate title if not provided
        if not self.title:
            self.title = f"Discussion about property in {self.property.city}"
        super().save(*args, **kwargs)

class PropertyChatMessage(models.Model):
    """Individual message in a property chat"""
    SENDER_TYPES = [
        ('landlord', 'Landlord'),
        ('renter', 'Renter'),
        ('bot', 'AI Assistant')
    ]
    
    chat = models.ForeignKey(PropertyChat, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_chat_messages', null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        if self.sender_type == 'bot':
            sender = 'AI Assistant'
        else:
            sender = self.user.username if self.user else 'Unknown'
        return f"{sender} in {self.chat}"