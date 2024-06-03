import sys
import requests
import os
import json

class GetProjectList:


    def __init__(self, api_token_path='~/ir/.ir_user_token', instance_domain_path='~/ir/ir_instance_domain'):
        self.api_token_path = os.path.expanduser(api_token_path)
        self.instance_domain_path = os.path.expanduser(instance_domain_path)
        self.api_token, self.instance_domain = self.read_credentials()

    def read_credentials(self):
        try:
            with open(self.api_token_path, 'r') as token_file:
                api_token = token_file.read().strip()
            with open(self.instance_domain_path, 'r') as domain_file:
                instance_domain = domain_file.read().strip()
            return api_token, instance_domain
        except FileNotFoundError as e:
            print(f"Error: {e}. Make sure the paths are correct.")
            sys.exit(1)  # Exit if credentials cannot be read

    def get_all_projects(self):
        url = f'https://{self.instance_domain}.iriusrisk.com/api/v2/projects'
        headers = {
            'Accept': 'application/hal+json',  # Match the MIME type used in curl
            'api-token': self.api_token
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raises HTTPError for bad responses
            data = response.json()
            # Write to a file
            with open('projectList.json', 'w') as file:
                json.dump(data, file, indent=4)

            print("Project list saved to projectList.json")
            print(" ")

        except requests.HTTPError as e:
            print(f"HTTP Error: {e}")
        except requests.RequestException as e:
            print(f"Error fetching project details: {e}")

def main():
    project_list_instance = GetProjectList()  # Initialize the class
    project_list_instance.get_all_projects()  # Call the method to print out all projects

# Proper entry point check
if __name__ == "__main__":
    if len(sys.argv) != 1:
        print(" ")
        print("Usage: python3 getProjectList.py")
        print(" ")
        sys.exit(1)
    else:
        main()  # Call main function
