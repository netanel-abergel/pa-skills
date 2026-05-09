# Code Examples

## Service-Specific Examples (Native API)

### Slack - Post Message (Native API)

```bash
# Native Slack API: POST https://slack.com/api/chat.postMessage
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'channel': 'C0123456', 'text': 'Hello!'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/slack/api/chat.postMessage', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json; charset=utf-8')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### HubSpot - Create Contact (Native API)

```bash
# Native HubSpot API: POST https://api.hubapi.com/crm/v3/objects/contacts
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'properties': {'email': 'john@example.com', 'firstname': 'John', 'lastname': 'Doe'}}).encode()
req = urllib.request.Request('https://gateway.maton.ai/hubspot/crm/v3/objects/contacts', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Google Sheets - Get Spreadsheet Values (Native API)

```bash
# Native Sheets API: GET https://sheets.googleapis.com/v4/spreadsheets/{id}/values/{range}
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/google-sheets/v4/spreadsheets/{spreadsheet_id}/values/Sheet1!A1:B2')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Salesforce - SOQL Query (Native API)

```bash
# Native Salesforce API: GET https://{instance}.salesforce.com/services/data/v64.0/query?q=...
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/salesforce/services/data/v64.0/query?q=SELECT+Id,Name+FROM+Contact+LIMIT+10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Airtable - List Tables (Native API)

```bash
# Native Airtable API: GET https://api.airtable.com/v0/meta/bases/{id}/tables
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/airtable/v0/meta/bases/{base_id}/tables')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Notion - Query Database (Native API)

```bash
# Native Notion API: POST https://api.notion.com/v1/data_sources/{id}/query
python <<'EOF'
import urllib.request, os, json
data = json.dumps({}).encode()
req = urllib.request.Request('https://gateway.maton.ai/notion/v1/data_sources/{data_source_id}/query', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
req.add_header('Notion-Version', '2025-09-03')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Stripe - List Customers (Native API)

```bash
# Native Stripe API: GET https://api.stripe.com/v1/customers
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/stripe/v1/customers?limit=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Language-Specific Examples

### JavaScript (Node.js)

```javascript
const response = await fetch('https://gateway.maton.ai/slack/api/chat.postMessage', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.MATON_API_KEY}`
  },
  body: JSON.stringify({ channel: 'C0123456', text: 'Hello!' })
});
```

### Python

```python
import os
import requests

response = requests.post(
    'https://gateway.maton.ai/slack/api/chat.postMessage',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    json={'channel': 'C0123456', 'text': 'Hello!'}
)
```
