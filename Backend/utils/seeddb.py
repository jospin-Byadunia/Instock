import requests

url = "http://127.0.0.1:8000/api/v1/items/categories/"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY2MzI1OTEzLCJpYXQiOjE3NjYzMjUwMTMsImp0aSI6ImY2N2FkOGVlNTZlZTQ1YTdiNDcxNWVkMDkwZmFmZDFjIiwidXNlcl9pZCI6IjEiLCJyb2xlIjoiYWRtaW4ifQ.cgVsz7ocUUq2GaZFQ5EoSHR_lPrbSfKTu_p9T7cWGpo"
categories = [
  {"name": "Computer Accessories", "description": "Peripherals and accessories for computers, such as keyboards, mice, webcams, headphones, and laptop chargers."},
  {"name": "Networking Equipment", "description": "Devices for network connectivity including routers, switches, access points, network cables, and firewalls."},
  {"name": "Mobile Devices", "description": "Smartphones, tablets, and related accessories such as power banks and protective cases."},
  {"name": "Printers & Scanners", "description": "Printing and scanning equipment, including laser and inkjet printers, scanners, and consumables like toner and ink cartridges."},
  {"name": "Storage Devices", "description": "Internal and external storage solutions including SSDs, HDDs, USB flash drives, and memory cards."},
  {"name": "Servers & Data Center", "description": "Server hardware and infrastructure components including rack servers, tower servers, UPS systems, and server accessories."},
  {"name": "Software & Licenses", "description": "Operating systems, productivity software, security software, and other licensed applications."},
  {"name": "Home & Office Electronics", "description": "Electronic devices for home or office use, such as monitors, speakers, projectors, and smart TVs."},
  {"name": "Power & Electrical", "description": "Power management and electrical devices including UPS systems, voltage stabilizers, surge protectors, and power strips."}
]


for cat in categories:
    res = requests.post(url, json=cat, headers={"Authorization": f"Bearer {token}"})
    print(res.status_code, res.json())
