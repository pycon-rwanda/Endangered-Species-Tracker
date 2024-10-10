import gradio as gr
import plotly.graph_objects as go
from functools import lru_cache
import requests
from decouple import config
import logging
from ratelimit import limits, sleep_and_retry

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API key from environment variables
IUCN_API_KEY = config("IUCN_API_KEY")
IUCN_API_URL = "https://apiv3.iucnredlist.org/api/v3/"

# Rate limiting: 10 calls per second
@sleep_and_retry
@limits(calls=10, period=1)
@lru_cache(maxsize=1000)
def api_call(endpoint, params=None):
    try:
        url = f"{IUCN_API_URL}{endpoint}"
        params = params or {}
        params['token'] = IUCN_API_KEY
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API call failed: {e}")
        return None

# Fetch species data
def fetch_species_data(species_name):
    species_endpoint = f"species/{species_name}"
    species_data = api_call(species_endpoint)
    
    if not species_data or 'result' not in species_data or len(species_data['result']) == 0:
        return None

    species_info = species_data['result'][0]
    return {
        'scientific_name': species_info['scientific_name'],
        'common_name': species_info.get('main_common_name', 'Not Available'),
        'category': species_info.get('category', 'Not Available'),
        'population_trend': species_info.get('population_trend', 'Not Available'),
        'habitat': species_info.get('habitat', 'Not Available')
    }

# Create UI Charts
def create_status_chart(species_list):
    status_counts = {}
    for species in species_list:
        status = species['category']
        status_counts[status] = status_counts.get(status, 0) + 1

    fig = go.Figure(data=[go.Pie(labels=list(status_counts.keys()), values=list(status_counts.values()))])
    fig.update_layout(title="Conservation Status Distribution", title_font_size=20)
    return fig

def create_trend_chart(species_list):
    trend_counts = {}
    for species in species_list:
        trend = species['population_trend']
        trend_counts[trend] = trend_counts.get(trend, 0) + 1

    fig = go.Figure(data=[go.Bar(x=list(trend_counts.keys()), y=list(trend_counts.values()))])
    fig.update_layout(title="Population Trend Distribution", xaxis_title="Trend", yaxis_title="Count", title_font_size=20)
    return fig

# Gradio interface function
def interface(species_name, conservation_status, page):
    if species_name:
        species_data = fetch_species_data(species_name)
        if species_data:
            formatted_output = f"""
            ### Species Information:
            - **Scientific Name:** {species_data['scientific_name']}
            - **Common Name:** {species_data['common_name']}
            - **Conservation Status:** {species_data['category']}
            - **Population Trend:** {species_data['population_trend']}
            - **Habitat:** {species_data['habitat']}
            """
            return formatted_output, create_status_chart([species_data]), create_trend_chart([species_data])
        else:
            return "Species not found or error fetching data.", None, None
    else:
        # Assuming this would list and filter species, the code should be here as per original logic.
        return "No species found or invalid input.", None, None

# UI Layout
with gr.Blocks() as demo:
    gr.Markdown("# 🌿 Endangered Species Tracker")
    gr.Markdown("Search for endangered species and view their conservation status and population trends.")

    with gr.Row():
        with gr.Column():
            species_input = gr.Textbox(label="🔍 Enter Species Name", placeholder="e.g., Panthera leo (for Lion)")
            conservation_status = gr.Radio(
                label="📊 Filter by Conservation Status:",
                choices=["Vulnerable", "Endangered", "Critically Endangered", "Least Concern", "Not Available", None],
                value=None
            )
            page_number = gr.Slider(label="📖 Page Number", minimum=1, maximum=10, step=1)

    submit_btn = gr.Button("Search 🔍")

    output = gr.Markdown()
    status_chart = gr.Plot()
    trend_chart = gr.Plot()

    # Footer for navigation and page controls
    gr.Markdown("Use the page slider to navigate through species data.")

    # Link search button to the interface function
    submit_btn.click(
        interface, 
        inputs=[species_input, conservation_status, page_number], 
        outputs=[output, status_chart, trend_chart]
    )

# Launch the Gradio app
demo.launch(share=True)
