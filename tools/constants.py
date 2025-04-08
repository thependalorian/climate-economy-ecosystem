#!/usr/bin/env python3

import json
import os
from typing import Dict, List, Optional

# File to store company indexing status
INDEX_STATUS_FILE = "company_index_status.json"

# Load or initialize company index status
def load_company_index_status() -> Dict[str, bool]:
    if os.path.exists(INDEX_STATUS_FILE):
        with open(INDEX_STATUS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_company_index_status(status: Dict[str, bool] = None):
    if status is None:
        status = {}
    with open(INDEX_STATUS_FILE, 'w') as f:
        json.dump(status, f)

# Company indexing status
_company_index_status = load_company_index_status()

def is_company_indexed(company_name: str) -> bool:
    return _company_index_status.get(company_name, False)

def mark_company_as_indexed(company_name: str):
    _company_index_status[company_name] = True
    save_company_index_status(_company_index_status)

def get_unindexed_companies() -> List[Dict[str, Optional[str]]]:
    return [c for c in PARTNER_ORGANIZATIONS if not is_company_indexed(c["id"])]

# Climate report resources
CLIMATE_REPORT_RESOURCES = [
    "Powering_the_Future_A_Massachusetts_Clean_Energy_Workforce_Needs_Assessment_Final.pdf",
    "NECEC_2023_Annual_Report.pdf",
    "https://www.masscec.com/reports/industry-2023/",
]

# Required reports for database initialization
REQUIRED_REPORTS = CLIMATE_REPORT_RESOURCES

# Partner organizations data
PARTNER_ORGANIZATIONS = [
    {
        "id": "buffr",
        "name": "Buffr Inc.",
        "description": "A technology company focused on climate solutions and sustainability.",
        "location": "Waltham, MA",
        "skills": ["software development", "climate tech", "sustainability"],
        "interests": ["clean energy", "carbon reduction", "sustainable technology"],
        "community_involvement": True
    },
    {
        "id": "masscec",
        "name": "Massachusetts Clean Energy Center",
        "description": "State agency dedicated to accelerating clean energy and climate solutions.",
        "location": "Boston, MA",
        "skills": ["clean energy", "policy", "workforce development"],
        "interests": ["renewable energy", "energy efficiency", "climate action"],
        "community_involvement": True
    }
]

# Sectors data
SECTORS = [
    {
        "id": "clean_energy",
        "name": "Clean Energy",
        "description": "Renewable energy and energy efficiency solutions",
        "opportunities": [
            "Solar installation",
            "Wind energy development",
            "Energy storage",
            "Grid modernization"
        ]
    },
    {
        "id": "transportation",
        "name": "Transportation",
        "description": "Sustainable transportation solutions",
        "opportunities": [
            "Electric vehicles",
            "Public transit",
            "Bicycle infrastructure",
            "Smart mobility"
        ]
    },
    {
        "id": "buildings",
        "name": "Buildings",
        "description": "Energy-efficient building solutions",
        "opportunities": [
            "Building retrofits",
            "Smart building technology",
            "Green construction",
            "Energy management systems"
        ]
    }
]

# Domains data
DOMAINS = [
    {
        "id": "renewable_energy",
        "name": "Renewable Energy",
        "description": "Clean energy generation and distribution",
        "skills": [
            "Solar installation",
            "Wind turbine maintenance",
            "Energy storage systems",
            "Grid integration"
        ],
        "certifications": [
            "NABCEP Solar PV Installation Professional",
            "OSHA Safety Certification",
            "Electrical License"
        ]
    },
    {
        "id": "energy_efficiency",
        "name": "Energy Efficiency",
        "description": "Reducing energy consumption and waste",
        "skills": [
            "Energy auditing",
            "Building performance optimization",
            "HVAC systems",
            "Insulation and weatherization"
        ],
        "certifications": [
            "BPI Building Analyst",
            "LEED Green Associate",
            "Energy Auditor Certification"
        ]
    },
    {
        "id": "sustainable_transportation",
        "name": "Sustainable Transportation",
        "description": "Clean and efficient transportation solutions",
        "skills": [
            "EV charging infrastructure",
            "Public transit planning",
            "Bicycle infrastructure",
            "Smart mobility systems"
        ],
        "certifications": [
            "EV Infrastructure Installation",
            "Transportation Planning",
            "Smart City Technology"
        ]
    }
] 