import requests
import json
import time
from collections import Counter
from multiprocessing.dummy import Pool
from multiprocessing import cpu_count
from multiprocessing import set_start_method

BASE_URL = "http://72.60.221.150:8080"
STUDENT_ID = "MDS202522"


def login(student_id):
    login_url = f"{BASE_URL}/login"
    payload = {"student_id": student_id}
    
    try:
        response = requests.post(login_url, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get('secret_key')
        return None
    except:
        return None

def get_publication_title(secret_key, filename):
    lookup_url = f"{BASE_URL}/lookup"
    payload = {"secret_key": secret_key, "filename": filename}
    
    try:
        response = requests.post(lookup_url, json=payload)
        if response.status_code == 200:
            return response.json().get('title')
        return None
    except:
        return None


def extract_first_word(title):
    if not title:
        return None
    
    # Remove leading/trailing whitespace
    title = title.strip()
    
    # Split by whitespace and get first word
    words = title.split()
    
    if words:
        first_word = words[0]
        
        # Remove common leading punctuation (quotes, parentheses)
        first_word = first_word.lstrip('("\'')
        
        return first_word
    
    return None

def mapper(file_chunk):
    local_counter = Counter()

    # Each worker logs in separately
    secret_key = login(STUDENT_ID)
    if not secret_key:
        return local_counter

    for filename in file_chunk:
        retries = 3

        while retries > 0:
            title = get_publication_title(secret_key, filename)

            if title:
                first_word = extract_first_word(title)
                if first_word:
                    local_counter[first_word] += 1
                break

            retries -= 1
            time.sleep(0.05)  # retry backoff

        # Rate limiting control
        time.sleep(0.015)

    return local_counter

def create_chunks(file_list, n_chunks):
    chunk_size = len(file_list) // n_chunks
    chunks = []

    for i in range(n_chunks):
        start = i * chunk_size
        end = None if i == n_chunks - 1 else (i + 1) * chunk_size
        chunks.append(file_list[start:end])

    return chunks


def main():
    files = [f"pub_{i}.txt" for i in range(1000)]
    num_workers = min(6, cpu_count())
    chunks = create_chunks(files, num_workers)

    with Pool(processes=num_workers) as pool:
        results = pool.map(mapper, chunks)

    final_counter = Counter()
    for c in results:
        final_counter.update(c)

    top_10 = [word for word, _ in final_counter.most_common(10)]
    print("Top 10 words:", top_10)
    return top_10


def verify_solution(top_10):
    secret_key = login(STUDENT_ID)
    if not secret_key:
        return

    verify_url = f"{BASE_URL}/verify"

    payload = {
        "secret_key": secret_key,
        "top_10": top_10
    }

    try:
        response = requests.post(verify_url, json=payload)


        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=4))
        else:
            print(response.text)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    try:
        set_start_method("spawn")
    except RuntimeError:
        pass

    top_10_words = main()
    verify_solution(top_10_words)