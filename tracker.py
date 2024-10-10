import requests
import gradio as gr
from decouple import config
import plotly.graph_objects as go
import plotly.express as px
from functools import lru_cache
import pandas as pd
from ratelimit import limits, sleep_and_retry
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API key from environment variables
UCN_API_KEY = config("IUCN_API_KEY", default=None)
if not UCN_API_KEY:
    logger.error("IUCN_API_KEY is not set. Please set the API key in the environment variables.")
    raise ValueError("IUCN_API_KEY is not set")

# IUCN Red List API endpoint
IUCN_API_URL = "https://apiv3.iucnredlist.org/api/v3/"

# Rate limiting: 10 calls per second
@sleep_and_retry
@limits(calls=10, period=1)  # 10 calls per second
@lru_cache(maxsize=1000)  # Cache up to 1000 calls


def api_call(endpoint, params=None):
    """
    Make an API call to the IUCN Red List API with rate limiting and caching.

    :param endpoint: The API endpoint to call
    :param params: Optional parameters to pass in the query string
    :return: The JSON response from the API, or None if the call failed
    """
    try:
        url = f"{IUCN_API_URL}{endpoint}"
        params = params or {}
        params['token'] = UCN_API_KEY
        response = requests.get(url, params=params, timeout=10)  # Added timeout
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.exception(f"API call failed: {e}")  # Changed to logger.exception
        return None
    except ValueError as e:
        logger.exception(f"Invalid JSON response: {e}")
        return None



def fetch_species_list(page=0):
    """
    Fetch a list of species from the IUCN Red List API.

    The IUCN Red List API returns a list of species in the following format:

    {
        "result": [
            {
                "scientific_name": "<scientific name>",
                "category": "<conservation status>",
                "population_trend": "<population trend>",
                "habitat": "<habitat>",
                "threats": "<threats>",
                "conservationmeasures": "<conservation measures>",
            },
            ...
        ]
    }

    :param page: The page number to fetch (0-indexed)
    :return: A list of species dictionaries
    """
    endpoint = "species/page"
    params = {"page": page}
    data = api_call(endpoint, params)
    return data['result'] if data else []

def fetch_species_data(species_name):
    """
    Fetch detailed data for a given species.

    :param species_name: The scientific name of the species to fetch data for
    :return: A dictionary containing the species data
    """
    # Fetch the species data
    species_endpoint = f"species/{species_name}"
    species_data = api_call(species_endpoint)

    # If the species data is not found, return None
    if not species_data or 'result' not in species_data or len(species_data['result']) == 0:
        return None

    species_info = species_data['result'][0]

    # Fetch additional data
    threats_endpoint = f"species/narrative/{species_name}/threats"
    threats_data = api_call(threats_endpoint)

    conservation_endpoint = f"species/narrative/{species_name}/conservationmeasures"
    conservation_data = api_call(conservation_endpoint)

    # Return the species data in a dictionary
    return {
        'scientific_name': species_info['scientific_name'],
        'common_name': species_info.get('main_common_name', 'Not Available'),
        'category': species_info.get('category', 'Not Available'),
        'population_trend': species_info.get('population_trend', 'Not Available'),
        'habitat': species_info.get('habitat', 'Not Available'),
        # Fetch the threats data if available
        'threats': threats_data['result'][0]['threats'] if threats_data and threats_data['result'] else 'Not Available',
        # Fetch the conservation measures data if available
        'conservation_measures': conservation_data['result'][0]['conservationmeasures'] if conservation_data and conservation_data['result'] else 'Not Available'
    }

def filter_species_by_status(conservation_status, page=1, per_page=10):
    """
    Filter species by conservation status.

    Args:
        conservation_status (str): The conservation status to filter by. If None, all species are returned.
        page (int): The page number to return. Defaults to 1.
        per_page (int): The number of items to return per page. Defaults to 10.

    Returns:
        A tuple containing a list of filtered species and the total number of pages.
    """
    all_species = fetch_species_list()
    filtered_species = []
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    
    # Iterate over the species in the current page
    for species in all_species[start_index:end_index]:
        species_data = fetch_species_data(species['scientific_name'])
        if species_data:
            # If the conservation status matches, add it to the filtered list
            if conservation_status is None or species_data['category'] == conservation_status:
                filtered_species.append(species_data)
    
    # Calculate the total number of pages
    total_pages = -(-len(all_species) // per_page)
    return filtered_species, total_pages


def create_conservation_status_chart(species_list):
    """
    Create a pie chart of conservation statuses from the provided list of species.

    Args:
        species_list (list): A list of species dictionaries as returned by fetch_species_data() or fetch_species_list().

    Returns:
        A Plotly figure object representing a pie chart of conservation status distribution.
    """
    # Initialize an empty dictionary to store the count of each conservation status
    status_counts = {}
    
    # Iterate over the species in the list and count the conservation status of each
    for species in species_list:
        status = species['category']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Create the pie chart figure using the counts
    fig = go.Figure(data=[go.Pie(labels=list(status_counts.keys()), values=list(status_counts.values()))])
    fig.update_layout(title_text="Conservation Status Distribution")
    return fig


def create_population_trend_chart(species_list):
    """
    Create a bar chart of population trends.

    Args:
        species_list (list): A list of species dictionaries as returned by fetch_species_data() or fetch_species_list().

    Returns:
        A Plotly figure object representing a bar chart of population trend distribution.
    """
    # Initialize an empty dictionary to store the count of each population trend
    trend_counts = {}
    
    # Iterate over the species in the list and count the population trend of each
    for species in species_list:
        trend = species['population_trend']
        trend_counts[trend] = trend_counts.get(trend, 0) + 1
    
    # Create the bar chart figure using the counts
    fig = go.Figure(data=[go.Bar(x=list(trend_counts.keys()), y=list(trend_counts.values()))])
    fig.update_layout(title_text="Population Trends", xaxis_title="Trend", yaxis_title="Count")
    return fig


def interface(species_name, conservation_status, page):
    """
    Interface function for the Gradio app.

    Args:
        species_name (str): The scientific name of a species to fetch data for.
        conservation_status (str): The conservation status to filter by.
        page (int): The page number of species to return.

    Returns:
        A tuple containing a formatted string of species data (if species_name is not None),
        a conservation status distribution chart, a population trend distribution chart,
        and two Gradio update objects to control the visibility of the charts and the page number input.
    """
    if species_name:
        species_data = fetch_species_data(species_name)
        if species_data:
            formatted_output = f"""
            **Scientific Name:** {species_data['scientific_name']}
            **Common Name:** {species_data['common_name']}
            **Conservation Status:** {species_data['category']}
            **Population Trend:** {species_data['population_trend']}
            **Habitat:** {species_data['habitat']}
            **Threats:** {species_data['threats']}
            **Conservation Measures:** {species_data['conservation_measures']}
            """
            status_chart = create_conservation_status_chart([species_data])
            trend_chart = create_population_trend_chart([species_data])
            return formatted_output, status_chart, trend_chart, gr.update(visible=False), gr.update(visible=False)
        else:
            return "Species not found or error fetching data.", None, None, gr.update(visible=False), gr.update(visible=False)
    else:
        species_list, total_pages = filter_species_by_status(conservation_status, page)
        if species_list:
            formatted_list = "\n\n".join([
                f"**Scientific Name:** {s['scientific_name']}\n**Common Name:** {s['common_name']}\n**Conservation Status:** {s['category']}\n**Population Trend:** {s['population_trend']}"
                for s in species_list])
            status_chart = create_conservation_status_chart(species_list)
            trend_chart = create_population_trend_chart(species_list)
            return formatted_list, status_chart, trend_chart, gr.update(visible=True), gr.update(visible=True, maximum=total_pages)
        else:
            return "No species found with the selected conservation status.", None, None, gr.update(visible=False), gr.update(visible=False)

def change_page(direction, current_page):
    """
    Change the page number by the given direction.

    Args:
        direction (int): 1 to go to the next page, -1 to go to the previous page.
        current_page (int): The current page number.

    Returns:
        int: The new page number.
    """
    return max(1, current_page + direction)

with gr.Blocks() as demo:
    gr.Markdown("# Endangered Species Tracker")
    gr.Markdown("## Search for Endangered Species and Their Conservation Status")

    with gr.Row():
        with gr.Column(scale=2):
            species_input = gr.Textbox(label="Enter Species Name:")
        with gr.Column(scale=1):
            conservation_status_filter = gr.Radio(
                label="Filter by Conservation Status:",
                choices=["Vulnerable", "Endangered", "Critically Endangered", "Least Concern", "Not Available", None],
                value=None
            )

    submit_btn = gr.Button("Submit")
    output = gr.Markdown()
    status_chart = gr.Plot()
    trend_chart = gr.Plot()
    
    with gr.Row():
        prev_btn = gr.Button("Previous Page", visible=False)
        page_number = gr.Number(value=1, label="Page", visible=False)
        next_btn = gr.Button("Next Page", visible=False)

    submit_btn.click(
        interface,
        inputs=[species_input, conservation_status_filter, page_number],
        outputs=[output, status_chart, trend_chart, prev_btn, next_btn]
    )

    prev_btn.click(
        change_page,
        inputs=[gr.Number(value=-1, visible=False), page_number],
        outputs=page_number
    ).then(
        interface,
        inputs=[species_input, conservation_status_filter, page_number],
        outputs=[output, status_chart, trend_chart, prev_btn, next_btn]
    )

    next_btn.click(
        change_page,
        inputs=[gr.Number(value=1, visible=False), page_number],
        outputs=page_number
    ).then(
        interface,
        inputs=[species_input, conservation_status_filter, page_number],
        outputs=[output, status_chart, trend_chart, prev_btn, next_btn]
    )

    page_number.change(
        interface,
        inputs=[species_input, conservation_status_filter, page_number],
        outputs=[output, status_chart, trend_chart, prev_btn, next_btn]
    )

demo.launch(share=True)
