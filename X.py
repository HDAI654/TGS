import requests
import zlib
import json

#url = "https://tvgarden.world/api/tv/countries_metadata.json"
#url = "https://tvgarden.world/api/tv/countries/ye.json"
url = "https://tvgarden.world/api/tv/categories/music.json"

# Get the raw response
response = requests.get(url)

# Check the raw content (it should be binary/compressed)
print(f"First 20 bytes: {response.content[:20]}")

try:
    # Try to decompress with gzip/zlib
    # 16 + zlib.MAX_WBITS handles both gzip and zlib formats
    decompressed_data = zlib.decompress(response.content, 16 + zlib.MAX_WBITS)
    json_string = decompressed_data.decode('utf-8')
    data = json.loads(json_string)
    print(json.dumps(data, indent=2))  # Print first 500 chars
except zlib.error as e:
    print(f"Decompression failed: {e}")
    # If decompression fails, maybe the content is already plain text
    try:
        data = response.json()
        print("It was already JSON!")
    except:
        print("Could not parse response")