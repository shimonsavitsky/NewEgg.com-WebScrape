import requests

# Test the staging credentials that Nivoda provided
username = "testaccount@sample.com"
password = "staging-nivoda-22"
endpoint = "https://intg-customer-staging.nivodaapi.net/api/diamonds"

query = '{ __schema { queryType { name } } }'

print("Testing Nivoda-provided staging credentials:")
print(f"Username: {username}")
print(f"Password: {password}")
print(f"Endpoint: {endpoint}")
print()

response = requests.post(
    endpoint,
    json={'query': query},
    headers={'Content-Type': 'application/json'},
    auth=(username, password),
    timeout=10
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print("\n✅ SUCCESS - Credentials work!")
else:
    print("\n❌ FAILED - Credentials don't work")
    print("\nThis means even the test account needs to be enabled for your use.")
