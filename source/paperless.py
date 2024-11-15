import requests
import re
import json

def search_documents(access_token, base_url, search_string):
     
    url = f"{base_url}/api/documents/?query=({search_string})"

    headers = {
        "Authorization": f"Token {access_token}",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
    
    
        if response.status_code == 200:
            
            search_data = response.json()
            document_ids = search_data.get('all', [])
            print(f"Search Results: {document_ids}")

            return document_ids

        else:
            print(f"Search was raising HTTP error: {response.status_code}")

    except Exception as e:
        print(f"Error connecting to paperless-ngx, is it running? Error: {e}")

    

def filter_documents_by_tags(access_token, base_url, tags:list):
    tags_string= ",".join(str(tag) for tag in tags)
    
    url = f"{base_url}/api/documents/?tags__id__all={tags_string}"

    headers = {
        "Authorization": f"Token {access_token}",
        "Accept": "application/json",
    }
 
    try:
        response = requests.get(url, headers=headers)
    
    
        if response.status_code == 200:
            
            search_data = response.json()
            document_ids = search_data.get('all', [])
            print(f"Search Results: {document_ids}")

            return document_ids
        else:
            print(f"Search was raising HTTP error: {response.status_code}")

    except Exception as e:
        print(f"Error connecting to paperless-ngx, is it running? Error: {e}")


def download_document(access_token, base_url, id):
    url = f'{base_url}/api/documents/{id}/download/?original=true'
    
    headers = {
        "Authorization": f"Token {access_token}",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code == 200:
            # Extrahiere den Dateinamen aus dem Content-Disposition-Header
            content_disposition = response.headers.get('Content-Disposition', '')
            filename = "document.pdf"  # Fallback-Name, falls der Header nicht gesetzt ist
            match = re.search(r'filename="([^"]+)"', content_disposition)
            if match:
                filename = match.group(1)

            # Speichere den Inhalt in einer Datei mit dem extrahierten Dateinamen
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Überspringt leere Chunks
                        f.write(chunk)
            
            print(f"Document #{id} downloaded successfully as {filename}.")
            return filename
        else:
            print(f"Failed to download document. Status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error connecting to paperless-ngx, is it running? Error: {e}")
        return None

def set_custom_field(access_token, base_url, document_id, field_id, field_value):
    url = f'{base_url}/api/documents/{document_id}/'

    headers = {
        "Authorization": f"Token {access_token}",
        "Content-Type": "application/json",
    }

    payload = json.dumps({
        "custom_fields": [
            {
            "value": field_value,
            "field": field_id
            }
        ]
    })  
    
    try:
        response = requests.request("PATCH", url, headers=headers, data=payload)

    except Exception as e:
        print(f"Error connecting to paperless-ngx, is it running? Error: {e}")
    
    

def remove_tag(access_token, base_url, document_id, tag_ids):
    url = f'{base_url}/api/documents/{document_id}/'

    headers = {
        "Authorization": f"Token {access_token}",
        "Content-Type": "application/json",
    }


    # Get document

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            
            document_data = response.json()
            current_tags = document_data.get('tags', [])
            
            
            # Remove tags
            for tag_id in tag_ids:
                current_tags.remove(int(tag_id))

            new_tags = current_tags

            payload = json.dumps({"tags": new_tags})
            

            response = requests.request("PATCH", url, headers=headers, data=payload)
            print(f"Removed tag IDs {tag_ids} from document #{document_id} after successful upload to lexoffice.")
            
            
            
        else:
            print(f"Failed to fetch document data. Status code: {response.status_code}")

    except Exception as e:
        print(f"Error connecting to paperless-ngx, is it running? Error: {e}")


   