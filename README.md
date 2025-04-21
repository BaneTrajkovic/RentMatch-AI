# RentMatch AI

RentMatch AI is an intelligent property rental search and matching platform that helps users find their ideal rental properties in California.

## Features

- **Smart Property Search**: Search for rental properties by location, price range, bedrooms, bathrooms, and other criteria
- **Natural Language Processing**: Use conversational queries to find properties (e.g., "Show me 3-bedroom apartments in San Francisco under $4,000/month")
- **Lease Analysis**: Upload and analyze lease agreements to identify key terms and potential issues
- **Negotiation Assistance**: Get personalized strategies for negotiating with landlords or tenants

## Getting Started

### Prerequisites

- Python 3.10+
- Django 5.2+
- Required packages (see requirements.txt)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/RentMatch-AI.git
cd RentMatch-AI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the development server:
```bash
./run_server.sh
```

4. Access the application at http://127.0.0.1:8001/

### Dataset

The application uses a comprehensive dataset of California rental properties. Due to its size, the dataset file is not included in the repository. Contact the repository owner for access to the dataset file.

## Usage Examples

Here are some example queries you can use with the chatbot:

- "Show me apartments in Napa under $3,000/month"
- "Find 3-bedroom rentals in San Francisco"
- "What condos are available for rent in Sonoma?"
- "Show me waterfront rental properties in California"
- "Find luxury rentals with at least 4 bedrooms"

## Components

- **Chatbot**: Intelligent conversational interface for property search
- **Property Search**: Advanced filtering and matching system
- **User Management**: Account creation and preferences
- **Negotiation Tools**: Templates and strategies for rental negotiations

## Development

For development without API keys, the system will use the local JSON dataset.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Zillow for property data structure inspiration
- Django and Channels for the web framework
- The open-source community for various libraries and tools 