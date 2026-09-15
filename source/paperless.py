import requests
import json
from urllib.parse import urljoin, urlsplit


def _get_document_ids(access_token, base_url, params):
    """Read all document pages before returning IDs."""
    url = f"{base_url.rstrip('/')}/api/documents/"
    origin = urlsplit(url)
    headers = {
        "Authorization": f"Token {access_token}",
        "Accept": "application/json",
    }
    document_ids = []
    visited = set()

    while url:
        target = urlsplit(url)
        # A reverse proxy can leave HTTP URLs in an HTTPS response.
        # Keep TLS when the next page has the same host and port.
        if origin.scheme == "https" and target.scheme == "http" and target.netloc == origin.netloc:
            url = target._replace(scheme="https").geturl()
            target = urlsplit(url)
        if (target.scheme, target.netloc) != (origin.scheme, origin.netloc):
            raise ValueError("The next page has a different origin.")
        if url in visited:
            raise ValueError("The document API repeated a page URL.")
        visited.add(url)

        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        page = response.json()
        # A missing results field is an error, not an empty document list.
        results = page["results"]
        if not isinstance(results, list):
            raise ValueError("The document API results must be a list.")
        for document in results:
            document_id = document["id"]
            if type(document_id) is not int:
                raise ValueError("The document ID must be an integer.")
            document_ids.append(document_id)

        next_page = page["next"]
        if next_page is not None and not isinstance(next_page, str):
            raise ValueError("The next page must be a URL or null.")
        url = urljoin(response.url, next_page) if next_page else None
        params = None

    # Do not upload the same ID twice if pages overlap.
    return list(dict.fromkeys(document_ids))


def search_documents(access_token, base_url, search_string):
    try:
        document_ids = _get_document_ids(
            access_token, base_url, {"query": f"({search_string})"}
        )
        print(f"Search Results: {document_ids}")
        return document_ids
    except Exception as e:
        print(f"Error retrieving Paperless documents: {e}")


def filter_documents_by_tags(access_token, base_url, tags: list):
    try:
        document_ids = _get_document_ids(
            access_token,
            base_url,
            {"tags__id__all": ",".join(str(tag) for tag in tags)},
        )
        print(f"Search Results: {document_ids}")
        return document_ids
    except Exception as e:
        print(f"Error retrieving Paperless documents: {e}")


def download_document(access_token, base_url, id):
    url = f'{base_url}/api/documents/{id}/download/'
   

    headers = {
        "Authorization": f"Token {access_token}",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, stream=True)
        document_binary = b''
        if response.status_code == 200:
            
            for chunk in response.iter_content(chunk_size=8192):
                    document_binary+=chunk
                
            print(f"Document #{id} downloaded successfully.")
            return document_binary
        else:
            print(f"Failed to download document. Status code: {response.status_code}")

    except Exception as e:
        print(f"Error connecting to paperless-ngx, is it running? Error: {e}")

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


   