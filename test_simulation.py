import requests

BASE_URL = "http://127.0.0.1:8000/api/recovery"

def run_simulation():
    print("🚀 Starting Heirloom 10-Step Simulation Test...\n")

    files = {
        'file': ('Important_Document.pdf', b'%PDF-1.4 dummy encrypted content...', 'application/pdf')
    }
    data = {
        "owner_name": "Prachi",
        "beneficiary_name": "Aditya",
        "guardian_a": "Guardian A",
        "guardian_b": "Guardian B",
        "guardian_c": "Guardian C",
        "threshold": 2
    }
    
    response = requests.post(f"{BASE_URL}/setup", data=data, files=files)
    print(f"✅ Step 1-5 Setup Response: {response.json()}")

    response = requests.post(f"{BASE_URL}/trigger")
    print(f"✅ Step 6 Trigger Response: {response.json()}")
    
    for g in ["Guardian A", "Guardian B"]:
        res = requests.post(f"{BASE_URL}/approve", json={"guardian_name": g, "approved": True})
        print(f"✅ Step 7-8 Approval ({g}): {res.json()}")

    response = requests.get(f"{BASE_URL}/status")
    print(f"\n✨ Step 9-10 Final System Status:\n{response.json()}\n")

if __name__ == "__main__":
    run_simulation()