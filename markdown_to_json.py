import os
import json
import re

# Define a custom exception for markdown parsing errors
class MarkdownParsingError(Exception):
    """Exception raised for errors in the markdown parsing process."""
    def __init__(self, message):
        super().__init__(message)

def parse_markdown_to_json(markdown_content):
    """
    Parses the given markdown content into a JSON-compatible dictionary.
    
    The expected markdown format includes titles and dialogues between speakers.
    """
    dialogues = []
    
    # Split the content into sections based on '### Example'
    sections = re.split(r'\n###\s+Example\s+\d+:\s+.*\n', markdown_content)
    
    # Extract titles for each dialogue
    titles = re.findall(r'###\s+Example\s+\d+:\s+(.*)\n', markdown_content)
    
    if len(sections) - 1 != len(titles):
        raise MarkdownParsingError("Mismatch between number of dialogues and titles.")
    
    for idx, section in enumerate(sections[1:], start=0):  # Skip the first split part before the first Example
        title = titles[idx].strip()
        dialogue = []
        
        # Find all speaker turns using regex
        # This pattern matches '**Speaker:** Text'
        speaker_turns = re.findall(r'\*\*(Patient|Doctor):\*\*\s*(.*?)\n(?=\*\*(Patient|Doctor):\*\*|---|$)', section, re.DOTALL)
        
        for turn in speaker_turns:
            speaker = turn[0]
            text = turn[1].strip()
            # Clean up any markdown formatting within the text if necessary
            # For simplicity, we'll keep the text as-is
            dialogue.append({
                "speaker": speaker,
                "text": text
            })
        
        if not dialogue:
            raise MarkdownParsingError(f"No dialogue found in section titled '{title}'.")
        
        dialogues.append({
            "title": title,
            "dialogue": dialogue
        })
    
    return {"dialogues": dialogues}

def process_tasks(tasks_folder, json_folder):
    # Create the JSON folder if it doesn't exist
    os.makedirs(json_folder, exist_ok=True)

    # Get a list of all markdown files in the tasks folder
    md_files = [f for f in os.listdir(tasks_folder) if f.endswith('.md')]

    for md_file in md_files:
        # Construct full paths for markdown and json files
        md_path = os.path.join(tasks_folder, md_file)
        json_file = md_file.replace('.md', '.json')
        json_path = os.path.join(json_folder, json_file)

        # Check if JSON file needs to be created or updated
        if not os.path.exists(json_path) or os.path.getmtime(md_path) > os.path.getmtime(json_path):
            print(f"Processing {md_file}...")

            try:
                # Read the markdown file
                with open(md_path, 'r', encoding='utf-8') as md_file_obj:
                    markdown_content = md_file_obj.read()

                # Parse markdown to JSON
                json_content = parse_markdown_to_json(markdown_content)

                # Write the JSON content to file
                with open(json_path, 'w', encoding='utf-8', newline='\n') as json_file_obj:
                    json.dump(json_content, json_file_obj, indent=2, ensure_ascii=False)
                    json_file_obj.write('\n')  # Add a final newline

                print(f"Successfully converted and saved {json_file}")
            except MarkdownParsingError as e:
                # Handle specific markdown parsing errors
                print(f"Error processing {md_file}: {str(e)}")
            except Exception as e:
                # Handle any other unexpected errors
                print(f"Unexpected error processing {md_file}: {str(e)}")
        else:
            # Skip processing if JSON file is up to date
            print(f"Skipping {md_file} - JSON file already up to date")

if __name__ == "__main__":
    # Define folder paths
    tasks_folder = "tasks"
    json_folder = "tasks-json"

    # Run the main processing function
    process_tasks(tasks_folder, json_folder)
