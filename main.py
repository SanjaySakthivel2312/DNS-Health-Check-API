from fastapi import FastAPI, HTTPException
import dns.resolver
import subprocess
import json
import uvicorn
import pymongo
import uuid

app = FastAPI()

# MongoDB client setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["dns_health_db"]
collection = db["domain_data"]

def get_record_data(domain: str, record_type: str):
    try:
        answers = dns.resolver.resolve(domain, record_type)
        ttl = answers.rrset.ttl
        return {"status": "OK", "ttl": ttl, "address": [rdata.to_text() for rdata in answers]}
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return {"status": "No records found"}
    except dns.exception.DNSException as e:
        return {"status": "Error", "error": str(e)}

def check_dnssec_with_analyzer(domain: str):
    try:
        result = subprocess.run(
            ["./dnssec-analyzer", "-json", domain],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return {"status": "Error", "error": result.stderr}
        output = json.loads(result.stdout)
        return {"status": "OK", "dnssec_analysis": output}
    except Exception as e:
        return {"status": "Error", "error": str(e)}

def get_soa_data(domain: str):
    try:
        answers = dns.resolver.resolve(domain, 'SOA')
        soa_data = answers[0]
        return {
            "status": "OK",
            "ttl": answers.rrset.ttl,
            "mname": soa_data.mname.to_text(),
            "rname": soa_data.rname.to_text(),
            "serial": soa_data.serial,
            "refresh": soa_data.refresh,
            "retry": soa_data.retry,
            "expire": soa_data.expire,
            "minimum": soa_data.minimum
        }
    except dns.exception.DNSException as e:
        return {"status": "Error", "error": str(e)}

def get_ns_data(domain: str):
    try:
        answers = dns.resolver.resolve(domain, 'NS')
        ttl = answers.rrset.ttl
        return {
            "status": "OK",
            "ttl": ttl,
            "nameservers": [rdata.to_text() for rdata in answers]
        }
    except dns.exception.DNSException as e:
        return {"status": "Error", "error": str(e)}

def get_mx_data(domain: str):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        ttl = answers.rrset.ttl
        return {
            "status": "OK",
            "ttl": ttl,
            "preference": answers[0].preference,
            "exchange": answers[0].exchange.to_text()
        }
    except dns.exception.DNSException as e:
        return {"status": "Error", "error": str(e)}

@app.get("/dns-health/{domain}")
async def get_dns_health(domain: str):
    try:
        # Generate a unique ID for this domain check
        unique_id = str(uuid.uuid4())
        data = {
            "domain": domain,
            "dns_health": {
                "A": get_record_data(domain, 'A'),
                "AAAA": get_record_data(domain, 'AAAA'),
                "DNSSEC": check_dnssec_with_analyzer(domain),
                "SOA": get_soa_data(domain),
                "NS": get_ns_data(domain),
                "MX": get_mx_data(domain),
            }
        }
        
        # Store the result in MongoDB
        collection.insert_one({"_id": unique_id, "data": data})
        
        return {"unique_id": unique_id, "result": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
