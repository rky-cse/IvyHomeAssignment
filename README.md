## My Process and Observations
### Initial Exploration with Postman

I started by testing the API endpoints using Postman.


My first test was with version v1:

- v1 API Test:

  I made a call to:

  http://34.47.238.26:8000/v1/autocomplete?query=a

  The response I received was:

    ```
        {
            "version": "v1",
            "count": 10,
            "results": [
                "aa",
                "aabdknlvkc",
                "aabrkcd",
                "aadgdqrwdy",
                "aagqg",
                "aaiha",
                "aainmxg",
                "aajfebume",
                "aajwv",
                "aakfubvxv"
            ]
        }
    ```
    Observation:

    - The API returns at most 10 suggestions when queried with a prefix.

    - I also noticed that if I use a more specific prefix like "abc", the result count could be less (for example, only 1 result for http://34.47.238.26:8000/v1/autocomplete?query=abc). This indicated to me that if a query returns fewer than 10 suggestions, then that prefix is “complete” and no further names exist with that beginning.

Next, I explored version v2:

- v2 API Test:

    I made a call to:
    http://34.47.238.26:8000/v2/autocomplete?query=a

    The response was:
    ```

            {
                "version": "v2",
                "count": 12,
                "results": [
                    "a0",
                    "a09p36zjy",
                    "a0d2vhq3i",
                    "a0ft3ec1tl",
                    "a0lnv81gm",
                    "a0pnt1",
                    "a0qm",
                    "a0twzs6",
                    "a1nvj3fpg",
                    "a1x1",
                    "a2",
                    "a2cqmcc7"
                ]
            }
    ```
Observation:

- In v2, strings may include digits as well as letters.
- The maximum number of suggestions here is 12.

Again, if I got fewer than 12 suggestions, I could conclude that the prefix had been “fully explored.”

Then I moved on to version v3:

- v3 API Test:
 
    I tested by calling:
    http://34.47.238.26:8000/v3/autocomplete?query=a

    And I received:
    ```
    {
        "version": "v3",
        "count": 15,
        "results": [
            "a",
            "a e+skbrns",
            "a ifs1.-",
            "a+woz7",
            "a-.",
            "a-g z",
            "a-m.ffwo",
            "a-o80",
            "a.",
            "a.-gowx3d",
            "a..rmw83",
            "a.1kh g",
            "a.2xf",
            "a.c",
            "a.gi3m"
        ]
    }
    ```
Observation:

- v3 returns up to 15 suggestions.
- I also saw that strings in v3 can include not only lowercase letters and digits, but also symbols such as dot (.), plus (+), minus (-), and even spaces.

- The Challenge and How I Optimized the Search
- I realized that if I tried an exhaustive search for all possible strings, the number of potential queries would be exponential.
For instance:

- For v1 with only letters, if the maximum length is n, I’d have 26^n combinations.
- For v2, using letters plus digits, that’s 36^n.

- For v3, with letters, digits, and four additional symbols, it would be 40^n.

Despite the exponential nature of the search space, I knew the server’s database of names was finite.

Here’s where a critical observation came in:
Key Insight:

When I receive a response that returns fewer than the maximum count (i.e., less than 10 for v1, less than 12 for v2, or less than 15 for v3), I can safely assume that no further names exist with that prefix. This acts as a natural “base case” that allows me to prune my search.
So my strategy was:

Breadth-First Search (BFS):
Start with minimal queries (each allowed character) and then extend only those prefixes that return the maximum number of results.


If the response count equals the maximum, it implies that there might be additional names available by extending that prefix.
If it’s less than the maximum, I stop extending that branch.
Allowed Character Sets:


- v1: Only lowercase letters (a–z).

- v2: Lowercase letters plus digits (a–z and 0–9).

- v3: Lowercase letters, digits, and additional symbols (dot, plus, minus, space).

Additional Considerations:

- I even thought about pruning further by not expanding a prefix if I’d already seen the exact same set of results from another query, thereby avoiding redundant API calls.



Implementing the Final Solution
With all these insights, I built three separate solutions for v1, v2, and v3. Each solution follows a similar structure:

API Call:

 I send a GET request to the appropriate endpoint with the query string.


Response Processing:

- I parse the JSON to get the list of suggestions and the count.


- If the count equals the maximum for that version (10, 12, or 15), I extend the query by appending every allowed character.

- If the count is less than the maximum, I know that branch is complete.
BFS Implementation:

 I initialize a queue with each allowed character as a starting query. Then I use BFS to explore the query space. Unique suggestions are added to a set, ensuring that I only keep new names.


File Output:

 - I write the final results (the total number of names and the list of names) into a file, without including the length of each string.



My Final Implementations
Below are the final Python implementations and documentation for each version.

Version v1 Implementation and Documentation
API Endpoint:
 http://34.47.238.26:8000/v1/autocomplete?query={query}


Allowed Characters:
 Lowercase letters (a–z).


Maximum Count:
 10 suggestions.


Strategy:
 Begin with each letter from a to z. Extend the prefix only if exactly 10 suggestions are returned; if fewer than 10 are returned, stop extending that branch.


python
```
import requests
import string


# v1 API settings

API_URL_V1 = "http://34.47.238.26:8000/v1/autocomplete?query={}"
MAX_RESULTS_V1 = 10
allowed_chars_v1 = list(string.ascii_lowercase)


def get_suggestions_v1(query):
    url = API_URL_V1.format(query)
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


def bfs_search_v1():
    discovered = set()
    queue = allowed_chars_v1.copy()
    total_requests = 0


    while queue:
        query = queue.pop(0)
        suggestions, count = get_suggestions_v1(query)
        total_requests += 1
        print(f"v1 Query '{query}' returned {count} suggestions")
        
        for name in suggestions:
            discovered.add(name)
        
        # If the full 10 results are returned, extend the query.
        if count == MAX_RESULTS_V1:
            for char in allowed_chars_v1:
                new_query = query + char
                queue.append(new_query)
    return discovered, total_requests


def write_results_v1(names, total_requests, filename="final_result_v1.txt"):
    with open(filename, "w") as f:
        f.write("Total names found: " + str(len(names)) + "\n")
        f.write("Total API requests made: " + str(total_requests) + "\n")
        f.write("Names:\n")
        for name in sorted(names):
            f.write(f"{name}\n")


if __name__ == "__main__":
    names, total_requests = bfs_search_v1()
    print("v1 Total names found:", len(names))
    print("v1 Total API requests made:", total_requests)
    write_results_v1(names, total_requests)
```


Version v2 Implementation and Documentation
API Endpoint:

 http://34.47.238.26:8000/v2/autocomplete?query={query}


Allowed Characters:
 Lowercase letters and digits (a–z, 0–9).


Maximum Count:
 12 suggestions.


Strategy:
 Begin with each allowed character from the combined set. Extend the prefix only if exactly 12 suggestions are returned; if fewer than 12 are returned, that branch is complete.


python
```
import requests
import string


# v2 API settings


API_URL_V2 = "http://34.47.238.26:8000/v2/autocomplete?query={}"
MAX_RESULTS_V2 = 12
allowed_chars_v2 = list(string.ascii_lowercase) + list(string.digits)


def get_suggestions_v2(query):
    url = API_URL_V2.format(query)
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


def bfs_search_v2():
    discovered = set()
    queue = allowed_chars_v2.copy()
    total_requests = 0


    while queue:
        query = queue.pop(0)
        suggestions, count = get_suggestions_v2(query)
        total_requests += 1
        print(f"v2 Query '{query}' returned {count} suggestions")
        
        for name in suggestions:
            discovered.add(name)
        
        # Extend the query if the maximum (12) is reached.
        if count == MAX_RESULTS_V2:
            for char in allowed_chars_v2:
                new_query = query + char
                queue.append(new_query)
    return discovered, total_requests


def write_results_v2(names, total_requests, filename="final_result_v2.txt"):
    with open(filename, "w") as f:
        f.write("Total names found: " + str(len(names)) + "\n")
        f.write("Total API requests made: " + str(total_requests) + "\n")
        f.write("Names:\n")
        for name in sorted(names):
            f.write(f"{name}\n")


if __name__ == "__main__":
    names, total_requests = bfs_search_v2()
    print("v2 Total names found:", len(names))
    print("v2 Total API requests made:", total_requests)
    write_results_v2(names, total_requests)
```


Version v3 Implementation and Documentation
API Endpoint:
 http://34.47.238.26:8000/v3/autocomplete?query={query}


Allowed Characters:
 Lowercase letters, digits, dot (.), plus (+), minus (-), and space. (A total of 40 characters.)


Maximum Count:
 15 suggestions.


Strategy:
 Begin with each allowed character from the full set. Extend the prefix only if exactly 15 suggestions are returned; otherwise, stop exploring that branch.


python
```
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
        
        # If 15 suggestions are returned, it means there might be more names with that prefix.
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
```


Final Reflection
In summary, I approached the problem by:
Testing each API version and noting the maximum results per query.
Recognizing that if a query returned fewer results than the maximum, that branch was complete.
Using a breadth-first search strategy that only extended queries when the server indicated more results might exist.
Customizing the allowed character sets according to the specific API version.
Implementing separate solutions for v1, v2, and v3 while outputting the results to files without printing the lengths of the strings.
This structured and optimized approach allowed me to efficiently retrieve all names from the server without an exponential number of API calls, relying on the finite nature of the stored data and the natural pruning offered by the API responses.
