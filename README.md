# Endangered Species Tracker

## Table of Contents
- [Overview](#overview)
- [Objectives](#objectives)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [API Key Setup](#api-key-setup)
  - [Running the Project](#running-the-project)
- [Contributing](#contributing)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [License](#license)

## Overview
**Endangered Species Tracker** is a Python tool that provides real-time information on endangered species around the world using the **IUCN Red List API**. It allows users to search for species and retrieve data on their conservation status, population trends, and habitat.

This project is part of **Hacktoberfest 2024**, encouraging contributors to enhance the platform and raise awareness about endangered species.

## Objectives
- Track endangered species with real-time data from the IUCN Red List API.
- Provide information on species conservation status, population trends, and habitats.
- Foster open-source collaboration during Hacktoberfest 2024.

## Target Audience:
- Python developers (beginner to intermediate).
- Environmental and conservation enthusiasts.
- Hacktoberfest participants interested in contributing to a meaningful cause.

## Features
- Search for species by name.
- Display species' conservation status (e.g., Vulnerable, Endangered).
- Show population trends and habitat information.
- Fetch real-time data from the IUCN Red List API.

## Getting Started

### Prerequisites
- Python 3.7 or higher
- Basic knowledge of APIs and JSON

### Installation
Install the required dependencies:

```bash
pip install requests python-decouple gradio
```

For testing, install `pytest`:

```bash
pip install pytest
```

### API Key Setup
1. Get a free API key from the [IUCN Red List website](https://apiv3.iucnredlist.org/).
2. Create a `.env` file in the project root and add your API key:

```bash
IUCN_API_KEY=your-api-key-here
```

### Running the Project
1. Clone the repository:

```bash
git clone https://github.com/pycon-rwanda/Endangered-Species-Tracker
cd Endangered-Species-Tracker
```

2. Run the tracker:

```bash
python tracker.py
```

### Example Usage
Search for a species:

```bash
Enter species name: Panthera leo
```

Example output:

```
Conservation Status: Vulnerable
Population Trend: Decreasing
Habitat: Savannas, grasslands, forests
```

## Contributing
Contributions are welcome! Please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to get involved.

## API Reference
This project uses the IUCN Red List API. To retrieve species data, make a request as shown below:

```python
import requests
from decouple import config
from dotenv import load_dotenv

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
```
endangered-species-tracker/
│
├── tracker.py          # Main script
├── README.md           # Project documentation
├── CONTRIBUTING.md     # Contribution guidelines
├── requirements.txt    # Python dependencies
├── .env.example        # API key placeholder
└── tests/              # Unit tests
```

## License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/pycon-rwanda/Endangered-Species-Tracker/blob/main/LICENSE) file for details.