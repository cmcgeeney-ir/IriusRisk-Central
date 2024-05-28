import requests
import requests
import base64
import json
import config
import ADOSetup

#-------------INITIALISE ENVIRONMENT-----------------#
#----IriusRisk----
domain = config.domain
sub_url = config.sub_url
apitoken = config.apitoken
head = config.head

url = domain + sub_url

#----ADO----
organization = config.organization
project = config.project
personal_access_token = config.personal_access_token

issue_tracker = ADOSetup.AzureDevOpsIssueTracker(organization, project, personal_access_token)
#--------/end INITIALISE ENVIRONMENT-------------#

#Hit the GET Products endpoint
response = requests.get(url, headers=head)
if response.status_code == 200: #if successful response
    data = response.json()
    for item in data:
        product_id = item['ref']
        #update url
        sub_url = '/api/v1/products/' + str(product_id)  #if required, get the CM's
        url = domain + sub_url

        #------------ LOGIC --------------------------#
        #GET request
        response = requests.get(url, headers=head)
        data3 = response.json()
        
        #for every component in the project
        for components in data3['components']:
            component_id = components['ref']
            #print(component_id)
            
            #for every countermeasure in the component                         
            for control in components['controls']:
                #print(control)
                # Check if there is not already an issue created
                if control['issueId'] in (None, ''):
                    print('No Issues')
                    
                    # If the countermeasure state is required
                    if control['state'] == 'Required':
                        print('met')
                        
                        # Store details from countermeasure to be sent to ADO                                    
                        control_ref = str(control['ref'])  # Countermeasure reference
                        control_name = str(control['name'])  # Countermeasure name
                        control_desc = str(control['desc'])  # Countermeasure description
                        control_state = str(control['state']).upper()  # Countermeasure state
                        control_platform = str(control['platform'])  # Countermeasure platform value
                        control_cost = str(control['cost'])  # Countermeasure cost rating
                        control_costRating = ''  # Initialise
                        
                        # Logic to convert control cost to control rating
                        if control_cost == '0':
                            control_costRating = 'low'
                        elif control_cost == '1':
                            control_costRating = 'medium'
                        elif control_cost == '2':
                            control_costRating = 'high'
                        
                        # ADO body to send in the POST request to create issue
                        title = control_ref  # Pass the countermeasure reference
                        description = control_desc  # Pass the countermeasure description
                        assigned_to = ""  # Optional
                        priority = 2  # Optional
                        #ADO_CF = "<Insert_Custom_Field_Value>"
                        
                        response = issue_tracker.create_issue(title, description, assigned_to, priority) #add ADO_CF as a parameter if used in config.py
                        
                        # PUT issue to link new issue
                        if response['status_code'] == 200:  # If successful
                            new_issue_id = response['data']['id']  # Take the new issue id
                            
                            # PUT new data
                            sub_url = '/api/v1/products/' + str(product_id) + '/components/' + str(component_id) + '/controls/' + control_ref
                            url = domain + sub_url
                            
                            # JSON Body to pass to PUT request
                            myobj = {
                                "ref": control_ref,
                                "name": control_name,
                                "desc": control_desc,
                                "state": control_state,
                                "platform": control_platform,
                                "issueId": new_issue_id,
                                "costRating": control_costRating
                            }
                            
                            # Send PUT request
                            response = requests.put(url, headers=head, json=myobj)
                            print(response.json())  # And print the response
                                                    
                
            
            
            

    
                                
                                
                                
                            
                            
                            

