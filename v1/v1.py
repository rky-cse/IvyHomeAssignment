import requests
import time
import string
import json

# Base API endpoint for version v1 with a placeholder for the query string
API_URL = "http://34.47.238.26:8000/v1/autocomplete?query={}"
# Assume the API returns a maximum of 15 results if the query is too broad.
MAX_RESULTS = 10  

# Allowed characters: only lowercase letters a-z
allowed_chars = list(string.ascii_lowercase)

def get_suggestions(query):
    """
    Makes a GET request to the autocomplete API using the provided query.
    Returns a tuple of (suggestions_list, count) if successful.
    """
    url = API_URL.format(query)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # data should contain "version", "count", and "results"
            return data.get("results", []), data.get("count", 0)
        else:
            print(f"Non-200 response: {response.status_code} for query: {query}")
            return [], 0
    except Exception as e:
        print(f"Exception during request for query {query}: {e}")
        return [], 0

def is_prefix_truncated(count):
    """
    Heuristic: if we get the maximum number of results (15),
    then the query might be too generic.
    """
    return count == MAX_RESULTS

def search_all_names():
    discovered = set()  # to store unique names
    seen_responses = set()  # to store seen responses to avoid duplicate expansion
    
    # Use only allowed characters as the initial query prefixes
    queue = allowed_chars.copy()
    total_requests = 0

    while queue:
        query = queue.pop(0)
        suggestions, count = get_suggestions(query)
        total_requests += 1
        # Uncomment the sleep if rate limiting is an issue
        # time.sleep(0.2)
        print(f"Query '{query}' returned {count} suggestions")

        # Add suggestions to the discovered set
        for name in suggestions:
            discovered.add(name)
        
        # Create an immutable representation of the suggestions list for pruning
        response_signature = frozenset(suggestions)
        
        # If this response has been seen before, skip further expansion of this query branch
        if response_signature in seen_responses:
            continue
        else:
            seen_responses.add(response_signature)
        
        # If the response count is maximal, extend the query by appending each allowed character
        if is_prefix_truncated(count):
            for char in allowed_chars:
                new_query = query + char
                queue.append(new_query)
    return discovered, total_requests

def write_results_to_file(names, total_requests, filename="final_result.txt"):
    """
    Writes the final results to a file without the length of each name.
    """
    with open(filename, "w") as f:
        f.write("Total names found: " + str(len(names)) + "\n")
        f.write("Total API requests made: " + str(total_requests) + "\n")
        f.write("Names:\n")
        for name in sorted(names):
            f.write(f"{name}\n")

if __name__ == "__main__":
    names, total_requests = search_all_names()
    print("Total names found:", len(names))
    print("Total API requests made:", total_requests)
    print("Names:")
    for name in sorted(names):
        print(name)
    
    # Write the final result in a file without printing name lengths
    write_results_to_file(names, total_requests)
