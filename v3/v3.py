import requests
import string

# v3 API settings
API_URL_V3 = "http://34.47.238.26:8000/v3/autocomplete?query={}"
MAX_RESULTS_V3 = 15
allowed_chars_v3 = list(string.ascii_lowercase) + list(string.digits) + ['.', '+', '-', ' ']

def get_suggestions_v3(query):
    url = API_URL_V3.format(query)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("results", []), data.get("count", 0)
        else:
            print(f"Non-200 response for query '{query}': {response.status_code}")
            return [], 0
    except Exception as e:
        print(f"Exception during request for query '{query}': {e}")
        return [], 0

def bfs_search_v3():
    discovered = set()
    queue = allowed_chars_v3.copy()
    total_requests = 0

    while queue:
        query = queue.pop(0)
        suggestions, count = get_suggestions_v3(query)
        total_requests += 1
        print(f"v3 Query '{query}' returned {count} suggestions")
        
        for name in suggestions:
            discovered.add(name)
        
        # Extend query only if exactly 15 results are returned.
        if count == MAX_RESULTS_V3:
            for char in allowed_chars_v3:
                new_query = query + char
                queue.append(new_query)
    return discovered, total_requests

def write_results_v3(names, total_requests, filename="final_result_v3.txt"):
    with open(filename, "w") as f:
        f.write("Total names found: " + str(len(names)) + "\n")
        f.write("Total API requests made: " + str(total_requests) + "\n")
        f.write("Names:\n")
        for name in sorted(names):
            f.write(f"{name}\n")

if __name__ == "__main__":
    names, total_requests = bfs_search_v3()
    print("v3 Total names found:", len(names))
    print("v3 Total API requests made:", total_requests)
    write_results_v3(names, total_requests)
