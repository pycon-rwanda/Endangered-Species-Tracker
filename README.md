# Endangered Species Tracker

## Table of Contents
- [Overview](#overview)
- [Objectives](#objectives)
- [Features](#features)
- [Getting Started](#getting-started)
- [Contributing](#contributing)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [License](#license)


## Overview
The Endangered Species Tracker is a Python-based tool designed to provide information on endangered species worldwide. Using the **IUCN Red List API**, this project pulls real-time data on various species and presents details such as their current population, habitat, and conservation status.

This project is part of **Hacktoberfest 2024**, where contributors from around the world can participate in open-source development to improve the platform and raise awareness about endangered species.

## Objectives
- Create a simple yet effective tool to track endangered species.
- Pull real-time data from the IUCN Red List API.
- Provide species information, including conservation status, population trends, and habitat details.
- Engage developers and environmental enthusiasts in open-source collaboration during Hacktoberfest.

## Target Audience:
- Python developers (beginner to intermediate).
- Environmental and conservation enthusiasts.
- Hacktoberfest participants interested in contributing to a meaningful cause.

## Features
- Search for species by name.
- Display species' conservation status (e.g., Vulnerable, Endangered, Critically Endangered).
- Show population trends and habitat information.
- Retrieve data in real-time from the IUCN Red List API.

## Getting Started

### Prerequisites
- Python 3.7 or higher
- A basic understanding of working with APIs and JSON data

### Dependencies
To run this project, you’ll need to install the following libraries:

```bash
pip install requests python-decouple gradio
```

### Tests
Optional, for running tests:
```bash
pip install pytest
```

### API Key
To use the IUCN Red List API, you will need an API key. Follow these steps to obtain one:

- Visit the [IUCN Red List website](https://apiv3.iucnredlist.org/).
- Sign up for a free API key.
- Create a `.env` file in the root directory of the project with the following content:

```bash 
IUCN_API_KEY=your-api-key-here
```

### Running the Project
Clone the repository and navigate to the project folder:

```
git clone https://github.com/pycon-rwanda/Endangered-Species-Tracker
cd Endangered-Species-Tracker
```

### Run the Python script:
```bash
python tracker.py
```

### Example Usage
Once running, you can search for a species by entering its name. For example:
```bash 
Enter species name: Panthera leo
```

### This will return data such as:
- Conservation Status: Vulnerable
- Population Trend: Decreasing
- sHabitat: Savannas, grasslands, and forests

## Contributing
We welcome contributions to improve the project! Check out the CONTRIBUTING.md for details on how to get involved, contribute code, suggest ideas, and help build new features for the community.

## API Reference
This project uses the IUCN Red List API. For more details on the available endpoints, see the [official documentation](https://apiv3.iucnredlist.org/api/v3/docs).

To retrieve species data, the following example shows how to make a simple request:

```bash
import requests
import os
from decouple import config 
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = config("IUCN_API_KEY")

species_name = 'Panthera leo'

url = f'https://apiv3.iucnredlist.org/api/v3/species/{species_name}?token={API_KEY}'
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print("Error: Unable to fetch data.")
```

## Project Structure
```graphql
endangered-species-tracker/
│
├── tracker.py          # Main script to run the application
├── README.md           # Project documentation
├── CONTRIBUTING.md     # Contribution guidelines
├── requirements.txt    # Python dependencies
├── .env.example        # API key placeholder file
└── tests/              # Unit tests for the project
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.

