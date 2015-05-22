from stravalib import Client
client = Client()

CLIENT_ID = "CLIENT ID"
CLIENT_SECRET = "CLIENT SECRET"

url = client.authorization_url(
    client_id=CLIENT_ID,
    scope="write",
    redirect_uri='http://localhost')
# Go to that URL and retrieve the code
print(url)

CODE = "PUT THE CODE HERE"

access_token = client.exchange_code_for_token(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    code=CODE)

print(access_token)
