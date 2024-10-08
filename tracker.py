import requests
import gradio as gr
from decouple import config

# Load API key from environment variables
IUCN_API_KEY = config("IUCN_API_KEY")

# IUCN Red List API endpoint
IUCN_API_URL = "https://apiv3.iucnredlist.org/api/v3/species/"

# Function to fetch species data from the IUCN API
def fetch_species_data(species_name, conservation_status=None):
    try:
        response = requests.get(f"{IUCN_API_URL}{species_name}?token={IUCN_API_KEY}")
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and len(data['result']) > 0:
                species_info = data['result'][0]
                conservation_status = species_info.get("category", "Not Available")
                population_trend = species_info.get("population", "Not Available")
                habitat = species_info.get("habitat", "Not Available")
                return (species_info['scientific_name'], conservation_status, population_trend, habitat)
            else:
                return "Species not found.", "", "", ""
        else:
            return "Error fetching data from API.", "", "", ""
    except Exception as e:
        return f"An error occurred: {str(e)}", "", "", ""

# Function to filter species by conservation status
def filter_species_by_status(conservation_status):
    all_species = ["Puma concolor", "Panthera leo", "Elephas maximus"]  # Replace with actual species list
    filtered_species = []
    for species in all_species:
        scientific_name, status, population_trend, habitat = fetch_species_data(species)
        if conservation_status is None or status == conservation_status:
            filtered_species.append((scientific_name, status, population_trend, habitat))
    return filtered_species

# Gradio interface function
def interface(species_name, conservation_status):
    if species_name:
        species_data = fetch_species_data(species_name)
        if isinstance(species_data, tuple):
            formatted_output = f"**Scientific Name:** {species_data[0]}\n\n**Conservation Status:** {species_data[1]}\n\n**Population Trend:** {species_data[2]}\n\n**Habitat:** {species_data[3]}"
            return formatted_output
        else:
            return species_data  # In case of an error message (string)
    else:
        species_list = filter_species_by_status(conservation_status)
        if species_list:
            formatted_list = "\n\n".join([
                f"**Scientific Name:** {s[0]}\n**Conservation Status:** {s[1]}\n**Population Trend:** {s[2]}\n**Habitat:** {s[3]}"
                for s in species_list])
            return formatted_list
        else:
            return "No species found with the selected conservation status."

# Create Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Endangered Species Tracker")
    gr.Markdown("## Search for Endangered Species and Their Conservation Status")

    species_input = gr.Textbox(label="Enter Species Name:")
    conservation_status_filter = gr.Radio(
        label="Filter by Conservation Status:",
        choices=["Vulnerable", "Endangered", "Critically Endangered", "Least Concern", "Not Available"],
        value=None
    )

    submit_btn = gr.Button("Submit")
    output = gr.Markdown()

    submit_btn.click(interface, inputs=[species_input, conservation_status_filter], outputs=output)

# Launch the Gradio app
demo.launch(share=True)

