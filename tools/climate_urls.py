#!/usr/bin/env python3
"""
Climate Economy Ecosystem URL Structure
This file contains the structured URLs for ingestion into the climate economy knowledge base.
"""

# Organized URL structure for strategic ingestion
URL_STRUCTURE = {
    "Tiered Content Approach": {
        "Primary Tier": [
            # Company main pages
            "https://tps-energy.com/",
            "https://www.ulem.org/",
            "https://myheadlamp.com/",
            "https://africanbn.org/",
            "https://franklincummings.edu/",
            "https://www.mass.gov/masshire-career-centers",
            "https://www.masscec.com/",
            "https://www.joinact.org/",
            "https://www.greentownlabs.com/",
            
            # Key resource pages
            "https://tps-energy.com/careers/",
            "https://www.ulem.org/workforce-development",
            "https://myheadlamp.com/career-paths/",
            "https://africanbn.org/programs/",
            "https://franklincummings.edu/academics/academic-programs/renewable-energy-technology/",
            "https://www.masscec.com/workforce-development",
            "https://www.masscec.com/reports/industry-2023/",
            "https://www.greentownlabs.com/startups/"
        ],
        "Secondary Tier": [
            # Supporting content
            "https://tps-energy.com/projects/",
            "https://www.ulem.org/events/",
            "https://myheadlamp.com/blog/",
            "https://africanbn.org/success-stories/",
            "https://franklincummings.edu/academics/cewp/",
            "https://www.masscec.com/programs/equity",
            "https://joinact.org/our-work/community-initiatives",
            "https://www.greentownlabs.com/membership/"
        ],
        "Tertiary Tier": [
            # Link-discovered content (none in predefined resources)
        ]
    },
    "Organization-Specific Strategies": {
        "Government/Large Organizations": [
            "https://www.mass.gov/masshire-career-centers",
            "https://www.masscec.com/",
            "https://www.masscec.com/workforce-development",
            "https://www.masscec.com/reports/industry-2023/",
            "https://www.masscec.com/offshore-wind"
        ],
        "Education Institutions": [
            "https://franklincummings.edu/academics/academic-programs/",
            "https://franklincummings.edu/academics/academic-programs/renewable-energy-technology/",
            "https://franklincummings.edu/academics/academic-programs/hvacr/",
            "https://franklincummings.edu/academics/academic-programs/building-energy-management/"
        ],
        "Startup/Innovation Organizations": [
            "https://www.greentownlabs.com/startups/",
            "https://www.greentownlabs.com/membership/",
            "https://www.greentownlabs.com/careers/"
        ]
    },
    "Content Extraction Methods": {
        "PDF Documents": [
            "https://www.masscec.com/reports/industry-2023/"
        ],
        "JavaScript-Heavy Sites": [
            "https://myheadlamp.com/",
            "https://www.greentownlabs.com/"
        ]
    }
}

# Implementation Notes
"""
Implementation Notes:

1. Tier Classification:
   - Primary Tier: Main domains + paths containing `careers|programs|reports|academic-programs`
   - Secondary Tier: Supporting pages like `/projects/`, `/events/`, `/success-stories/`
   - Tertiary Tier: Left empty as we only have predefined resources

2. Organization Strategies:
   - Government: Focused on MassCEC and Mass.gov resources
   - Education: Franklin Cummings program pages with curriculum details
   - Startups: Greentown Labs startup-focused content

3. Special Handling:
   - PDFs identified by `.pdf` extension or content type
   - JavaScript sites flagged based on known complex frameworks
"""

# Helper functions for working with the URL structure
def get_all_urls():
    """Get a flattened list of all URLs"""
    all_urls = []
    
    # Add tiered content approach URLs
    for tier, urls in URL_STRUCTURE["Tiered Content Approach"].items():
        all_urls.extend(urls)
    
    # Add organization-specific URLs
    for org_type, urls in URL_STRUCTURE["Organization-Specific Strategies"].items():
        all_urls.extend(urls)
    
    # Add content extraction method URLs
    for method, urls in URL_STRUCTURE["Content Extraction Methods"].items():
        all_urls.extend(urls)
    
    # Return deduplicated list
    return list(dict.fromkeys(all_urls))

def get_urls_by_company(domain):
    """Get all URLs for a specific company domain"""
    return [url for url in get_all_urls() if domain in url]

def get_primary_tier_urls():
    """Get primary tier URLs"""
    return URL_STRUCTURE["Tiered Content Approach"]["Primary Tier"]

def get_secondary_tier_urls():
    """Get secondary tier URLs"""
    return URL_STRUCTURE["Tiered Content Approach"]["Secondary Tier"]

def get_organization_urls(org_type):
    """Get URLs for a specific organization type"""
    return URL_STRUCTURE["Organization-Specific Strategies"].get(org_type, [])

if __name__ == "__main__":
    # Print URL counts when run directly
    print(f"Total unique URLs: {len(get_all_urls())}")
    print(f"Primary Tier URLs: {len(get_primary_tier_urls())}")
    print(f"Secondary Tier URLs: {len(get_secondary_tier_urls())}")
    for org_type in URL_STRUCTURE["Organization-Specific Strategies"]:
        print(f"{org_type} URLs: {len(get_organization_urls(org_type))}") 