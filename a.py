import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')  # Replace 'mysite' with your project name
django.setup()

# Now import your models and run your code
from django.contrib.auth.models import User
from negotiation.models import Property, PropertyChat, PropertyChatMessage

# Rest of your code here...
from django.contrib.auth.models import User
from negotiation.models import Property, PropertyChat, PropertyChatMessage

# Create a test property
property = Property.objects.create(
    title="2-Bedroom Downtown Apartment",
    address="123 Main Street, New York, NY"
)

# Create another test property
property2 = Property.objects.create(
    title="Studio Apartment with Bay View",
    address="456 Ocean Drive, San Francisco, CA"
)

# Make sure you have at least one landlord and one renter user
# If they don't exist, create them
landlord = User.objects.filter(is_staff=True).first()
if not landlord:
    landlord = User.objects.create_user(
        username="landlord",
        email="landlord@example.com",
        password="password123",
        is_staff=True
    )

renter = User.objects.filter(is_staff=False).exclude(id=landlord.id).first()
if not renter:
    renter = User.objects.create_user(
        username="renter",
        email="renter@example.com",
        password="password123"
    )

# Create a test chat
chat = PropertyChat.objects.create(
    property=property,
    landlord=landlord,
    renter=renter,
    title="Discussion about 2-Bedroom Downtown Apartment"
)

# Add some test messages
PropertyChatMessage.objects.create(
    chat=chat,
    sender_type="landlord",
    user=landlord,
    content="Hello! I'm interested in discussing the rent for this apartment."
)

PropertyChatMessage.objects.create(
    chat=chat,
    sender_type="renter",
    user=renter,
    content="Hi there! Thanks for reaching out. What would you like to know?"
)

PropertyChatMessage.objects.create(
    chat=chat,
    sender_type="bot",
    content="Welcome to your negotiation chat! I'm here to help facilitate your conversation about the property."
)

print("Test data created successfully!")