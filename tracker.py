import requests
import gradio as gr
from decouple import config
import plotly.graph_objects as go
from functools import lru_cache

# Load API key from environment variables
IUCN_API_KEY = config("IUCN_API_KEY")

# IUCN Red List API endpoint
IUCN_API_URL = "https://apiv3.iucnredlist.org/api/v3/species/"


@lru_cache(maxsize=100)
def fetch_species_data(species_name):
    """
    Fetches data for a given species name from the IUCN Red List API using the cached LRU decorator.
    """
    try:
        response = requests.get(f"{IUCN_API_URL}{species_name}?token={IUCN_API_KEY}")
        if response.status_code == 200:
            data = response.json()
            if "result" in data and len(data["result"]) > 0:
                species_info = data["result"][0]
                conservation_status = species_info.get("category", "Not Available")
                population_trend = species_info.get("population_trend", "Not Available")
                habitat = species_info.get("habitat", "Not Available")
                return (
                    species_info["scientific_name"],
                    conservation_status,
                    population_trend,
                    habitat,
                )
            else:
                return None
        else:
            return None
    except Exception as e:
        return None


def filter_species_by_status(conservation_status, page=1, per_page=10):
    """
    Filters a list of species by their conservation status and returns a paginated response.
    """
    all_species = [
        "Puma concolor", "Panthera leo", "Elephas maximus",
        "Gorilla beringei", "Panthera tigris", "Rhinoceros unicornis",
        "Ailuropoda melanoleuca", "Balaenoptera musculus", "Diceros bicornis", "Panthera onca",
    ]
    
    filtered_species = []
    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    for species in all_species[start_index:end_index]:
        species_data = fetch_species_data(species)
        if species_data:
            if conservation_status is None or species_data[1] == conservation_status:
                filtered_species.append(species_data)

    total_pages = -(-len(all_species) // per_page)
    return filtered_species, total_pages


def create_conservation_status_chart(species_list):
    """
    Creates a pie chart showing the distribution of conservation statuses from a list of species.
    """
    status_counts = {}
    for species in species_list:
        status = species[1]
        status_counts[status] = status_counts.get(status, 0) + 1

    fig = go.Figure(
        data=[go.Pie(labels=list(status_counts.keys()), values=list(status_counts.values()))]
    )
    fig.update_layout(title_text="Conservation Status Distribution")
    return fig


def interface(species_name, conservation_status, page):
    """
    Interface function for the Gradio demo.
    """
    if species_name:
        species_data = fetch_species_data(species_name)
        if species_data:
            formatted_output = f"""
            ### **{species_data[0]}**  
            **Conservation Status:** {species_data[1]}  
            **Population Trend:** {species_data[2]}  
            **Habitat:** {species_data[3]}  
            """
            chart = create_conservation_status_chart([species_data])
            return formatted_output, chart, gr.update(visible=False), gr.update(visible=False)
        else:
            return "Species not found or error fetching data.", None, gr.update(visible=False), gr.update(visible=False)
    else:
        species_list, total_pages = filter_species_by_status(conservation_status, page)
        if species_list:
            formatted_list = "\n\n".join([
                f"""
                ### **{s[0]}**  
                **Conservation Status:** {s[1]}  
                **Population Trend:** {s[2]}  
                **Habitat:** {s[3]}  
                """ for s in species_list
            ])
            chart = create_conservation_status_chart(species_list)
            return formatted_list, chart, gr.update(visible=True), gr.update(visible=True, maximum=total_pages)
        else:
            return "No species found with the selected conservation status.", None, gr.update(visible=False), gr.update(visible=False)


def change_page(direction, current_page):
    """
    Changes the current page by the given direction.
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
                value=None,
            )

    submit_btn = gr.Button("Submit")
    output = gr.Markdown()
    chart = gr.Plot()

    with gr.Row():
        prev_btn = gr.Button("Previous Page", visible=False)
        page_number = gr.Number(value=1, label="Page", visible=False)
        next_btn = gr.Button("Next Page", visible=False)

    submit_btn.click(
        interface,
        inputs=[species_input, conservation_status_filter, page_number],
        outputs=[output, chart, prev_btn, next_btn],
    )

    prev_btn.click(
        change_page,
        inputs=[gr.Number(value=-1, visible=False), page_number],
        outputs=page_number,
    ).then(
        interface,
        inputs=[species_input, conservation_status_filter, page_number],
        outputs=[output, chart, prev_btn, next_btn],
    )

    next_btn.click(
        change_page,
        inputs=[gr.Number(value=1, visible=False), page_number],
        outputs=page_number,
    ).then(
        interface,
        inputs=[species_input, conservation_status_filter, page_number],
        outputs=[output, chart, prev_btn, next_btn],
    )

    page_number.change(
        interface,
        inputs=[species_input, conservation_status_filter, page_number],
        outputs=[output, chart, prev_btn, next_btn],
    )

demo.launch(share=True)
