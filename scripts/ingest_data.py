import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv
from supabase import create_client, Client
from constants import PARTNER_ORGANIZATIONS, SECTORS, DOMAINS

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("NEXT_PUBLIC_SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

def ingest_partner_organizations():
    """Ingest partner organizations data"""
    for org in PARTNER_ORGANIZATIONS:
        try:
            # Insert into profiles table
            profile_data = {
                "id": org["id"],
                "email": f"contact@{org['name'].lower().replace(' ', '')}.org",
                "full_name": org["name"],
                "persona": "partner",
                "skills": org["skills"],
                "interests": org["interests"],
                "location": org["location"],
                "background": org["description"],
                "will_relocate": False,
                "in_ej_community": org.get("in_ej_community", False),
                "consent_to_share": True,
                "consent_to_email": True
            }
            
            supabase.table("profiles").upsert(profile_data).execute()
            print(f"Successfully ingested partner organization: {org['name']}")
            
        except Exception as e:
            print(f"Error ingesting partner organization {org['name']}: {str(e)}")

def ingest_sectors():
    """Ingest sectors data"""
    for sector in SECTORS:
        try:
            # Insert into climate_memories table
            memory_data = {
                "content": sector["description"],
                "metadata": {
                    "type": "sector",
                    "name": sector["name"],
                    "opportunities": sector["opportunities"]
                },
                "source_type": "sector",
                "sector": sector["name"]
            }
            
            supabase.table("climate_memories").insert(memory_data).execute()
            print(f"Successfully ingested sector: {sector['name']}")
            
        except Exception as e:
            print(f"Error ingesting sector {sector['name']}: {str(e)}")

def ingest_domains():
    """Ingest domains data"""
    for domain in DOMAINS:
        try:
            # Insert into climate_memories table
            memory_data = {
                "content": domain["description"],
                "metadata": {
                    "type": "domain",
                    "name": domain["name"],
                    "skills": domain["skills"],
                    "certifications": domain["certifications"]
                },
                "source_type": "domain",
                "domain": domain["name"]
            }
            
            supabase.table("climate_memories").insert(memory_data).execute()
            print(f"Successfully ingested domain: {domain['name']}")
            
        except Exception as e:
            print(f"Error ingesting domain {domain['name']}: {str(e)}")

def main():
    """Main function to run data ingestion"""
    print("Starting data ingestion...")
    
    # Ingest partner organizations
    print("\nIngesting partner organizations...")
    ingest_partner_organizations()
    
    # Ingest sectors
    print("\nIngesting sectors...")
    ingest_sectors()
    
    # Ingest domains
    print("\nIngesting domains...")
    ingest_domains()
    
    print("\nData ingestion completed!")

if __name__ == "__main__":
    main() 