import requests

url = "https://api.deepgram.com/v1/listen"
headers = {
    "Authorization": "Token f110c9c9665db50ecf74cca688ee96bddf7a10d6",
    "Content-Type": "application/json"
}
data = {
    "url": "https://static.deepgram.com/examples/Bueller-Life-moves-pretty-fast.wav"
}
params = {
    "model": "nova",
    "punctuate": "true"
}

response = requests.post(url, headers=headers, json=data, params=params)

print(response.json())
# curl -X POST \
#   -H "Authorization: Token f110c9c9665db50ecf74cca688ee96bddf7a10d6" \
#   -H 'content-type: application/json' \
#   -d '{"url":"https://static.deepgram.com/examples/Bueller-Life-moves-pretty-fast.wav"}' \
#   "https://api.deepgram.com/v1/listen?model=nova&punctuate=true"