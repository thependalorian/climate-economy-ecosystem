#!/usr/bin/env python3
"""
EJ Geospatial Tool for Massachusetts Clean Energy Ecosystem

This tool provides geospatial analysis capabilities for Environmental Justice communities
in Massachusetts, with a focus on Gateway Cities and clean energy opportunities.
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests
from dotenv import load_dotenv

from tools.base_tool import BaseTool, ToolError, ToolConfigurationError, ToolExecutionError

# Load environment variables
load_dotenv()

# Constants
GATEWAY_CITIES = [
    "Attleboro", "Barnstable", "Brockton", "Chelsea", "Chicopee", "Everett",
    "Fall River", "Fitchburg", "Haverhill", "Holyoke", "Lawrence", "Leominster",
    "Lowell", "Lynn", "Malden", "Methuen", "New Bedford", "Peabody", "Pittsfield",
    "Quincy", "Revere", "Salem", "Springfield", "Taunton", "Westfield", "Worcester"
]

EJ_CRITERIA = {
    "income": "Median household income is at or below 65% of the statewide median",
    "minority": "Minority population is 40% or greater",
    "english_isolation": "25% or more of households lack English language proficiency",
    "combination": "Meets any combination of the above criteria"
}

@dataclass
class Location:
    """Location data structure"""
    latitude: float
    longitude: float
    city: str
    state: str = "MA"
    zip_code: Optional[str] = None
    census_tract: Optional[str] = None

@dataclass
class TransportationOption:
    """Transportation option data structure"""
    mode: str  # "transit", "driving", "walking", "cycling"
    duration_minutes: int
    distance_miles: float
    cost: float
    transfers: int = 0
    accessibility_score: float = 0.0

class EJGeospatialTool(BaseTool):
    """Tool for geospatial analysis of EJ communities"""

    def requires_supabase(self) -> bool:
        """This tool requires Supabase for data storage"""
        return True

    async def initialize(self):
        """Initialize the EJ Geospatial Tool"""
        await super().initialize()

        # Get API key from environment or config
        self.ipstack_api_key = os.getenv("IPSTACK_API_KEY") or self.config.get("ipstack_api_key")
        if not self.ipstack_api_key:
            self.logger.warning("IPSTACK_API_KEY not found in environment variables or config")

        # Load data
        try:
            self.gateway_cities_data = self._load_gateway_cities_data()
            self.ej_communities_data = self._load_ej_communities_data()
            self.logger.info("EJ Geospatial Tool initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing EJ Geospatial Tool: {str(e)}")
            raise ToolConfigurationError(f"Error initializing EJ Geospatial Tool: {str(e)}")

    async def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Run the tool with the specified action"""
        self._check_availability()
        self.logger.info(f"Running {action} with {kwargs}")

        try:
            if action == "geocode":
                if "address" not in kwargs:
                    raise ToolExecutionError("Address is required for geocode action")
                return await self.geocode_location(kwargs.get("address"))

            elif action == "is_ej_community":
                if "location" not in kwargs:
                    raise ToolExecutionError("Location is required for is_ej_community action")
                return await self.is_ej_community(kwargs.get("location"))

            elif action == "find_opportunities":
                if "location" not in kwargs:
                    raise ToolExecutionError("Location is required for find_opportunities action")
                return await self.find_nearby_opportunities(
                    kwargs.get("location"),
                    kwargs.get("radius_miles", 5.0),
                    kwargs.get("opportunity_types")
                )

            elif action == "analyze_transportation":
                if "location" not in kwargs or "opportunity_location" not in kwargs:
                    raise ToolExecutionError("Location and opportunity_location are required for analyze_transportation action")
                return await self.analyze_transportation_access(
                    kwargs.get("location"),
                    kwargs.get("opportunity_location")
                )

            elif action == "get_community_projects":
                if "location" not in kwargs:
                    raise ToolExecutionError("Location is required for get_community_projects action")
                return await self.get_community_projects(kwargs.get("location"))

            elif action == "get_community_profile":
                if "city" not in kwargs:
                    raise ToolExecutionError("City is required for get_community_profile action")
                return await self.get_ej_community_profile(kwargs.get("city"))

            else:
                raise ToolExecutionError(f"Unknown action: {action}")

        except ToolError:
            # Re-raise tool errors
            raise
        except Exception as e:
            self.logger.error(f"Error executing {action}: {str(e)}")
            raise ToolExecutionError(f"Error executing {action}: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the tool"""
        health = await super().health_check()

        # Add tool-specific health information
        health.update({
            "ipstack_api_key_available": self.ipstack_api_key is not None,
            "gateway_cities_count": len(self.gateway_cities_data) if hasattr(self, "gateway_cities_data") else 0,
            "ej_communities_count": len(self.ej_communities_data) if hasattr(self, "ej_communities_data") else 0
        })

        return health

    def _load_gateway_cities_data(self) -> Dict[str, Any]:
        """Load Gateway Cities data"""
        try:
            # In a real implementation, this would load from a database or API
            # For now, we'll use a simplified version with hardcoded data
            data = {}
            for city in GATEWAY_CITIES:
                data[city] = {
                    "name": city,
                    "is_gateway_city": True,
                    "clean_energy_opportunities": self._get_mock_opportunities(city),
                    "transportation_hubs": self._get_mock_transportation_hubs(city)
                }
            return data
        except Exception as e:
            self.logger.error(f"Error loading Gateway Cities data: {str(e)}")
            return {}

    def _load_ej_communities_data(self) -> Dict[str, Any]:
        """Load EJ communities data"""
        try:
            # In a real implementation, this would load from a database or API
            # For now, we'll return a simplified version with hardcoded data
            return {
                "Lawrence": {
                    "ej_criteria": ["income", "minority", "english_isolation"],
                    "census_tracts": ["25009201100", "25009201200", "25009201300"],
                    "demographics": {
                        "total_population": 80028,
                        "minority_percentage": 87.6,
                        "median_household_income": 44613,
                        "english_isolation_percentage": 31.2
                    }
                },
                "Chelsea": {
                    "ej_criteria": ["income", "minority", "english_isolation"],
                    "census_tracts": ["25025050100", "25025050200", "25025050300"],
                    "demographics": {
                        "total_population": 40160,
                        "minority_percentage": 87.3,
                        "median_household_income": 56802,
                        "english_isolation_percentage": 34.5
                    }
                },
                # Add more EJ communities as needed
            }
        except Exception as e:
            self.logger.error(f"Error loading EJ communities data: {str(e)}")
            return {}

    def _get_mock_opportunities(self, city: str) -> List[Dict[str, Any]]:
        """Get mock clean energy opportunities for a city"""
        # In a real implementation, this would query a database
        if city == "Lawrence":
            return [
                {
                    "id": "opp-1",
                    "title": "Solar Installation Technician",
                    "company": "Lawrence Community Solar",
                    "type": "job",
                    "location": {"latitude": 42.7070, "longitude": -71.1631},
                    "description": "Entry-level position installing solar panels on residential properties."
                },
                {
                    "id": "opp-2",
                    "title": "Community Solar Project",
                    "organization": "Groundwork Lawrence",
                    "type": "community_project",
                    "location": {"latitude": 42.7012, "longitude": -71.1651},
                    "description": "Community-owned solar array providing clean energy to local residents."
                },
                {
                    "id": "opp-3",
                    "title": "Energy Efficiency Training",
                    "organization": "Lawrence CommunityWorks",
                    "type": "training",
                    "location": {"latitude": 42.7082, "longitude": -71.1637},
                    "description": "Free 8-week training program in home energy efficiency assessments."
                }
            ]
        elif city == "Chelsea":
            return [
                {
                    "id": "opp-4",
                    "title": "Green Infrastructure Maintenance",
                    "company": "Chelsea GreenRoots",
                    "type": "job",
                    "location": {"latitude": 42.3917, "longitude": -71.0328},
                    "description": "Maintaining green infrastructure installations throughout Chelsea."
                },
                {
                    "id": "opp-5",
                    "title": "Chelsea Microgrid Project",
                    "organization": "GreenRoots Chelsea",
                    "type": "community_project",
                    "location": {"latitude": 42.3925, "longitude": -71.0333},
                    "description": "Community microgrid providing resilient power to critical facilities."
                }
            ]
        else:
            # Return a smaller set of generic opportunities for other cities
            return [
                {
                    "id": f"opp-{city.lower()}-1",
                    "title": "Clean Energy Opportunity",
                    "organization": f"{city} Clean Energy Initiative",
                    "type": "community_project",
                    "description": f"Clean energy initiative in {city}."
                }
            ]

    def _get_mock_transportation_hubs(self, city: str) -> List[Dict[str, Any]]:
        """Get mock transportation hubs for a city"""
        # In a real implementation, this would query a transportation API
        if city == "Lawrence":
            return [
                {
                    "id": "hub-1",
                    "name": "Lawrence Station",
                    "type": "commuter_rail",
                    "location": {"latitude": 42.7070, "longitude": -71.1631}
                },
                {
                    "id": "hub-2",
                    "name": "Buckley Transportation Center",
                    "type": "bus_terminal",
                    "location": {"latitude": 42.7082, "longitude": -71.1637}
                }
            ]
        elif city == "Chelsea":
            return [
                {
                    "id": "hub-3",
                    "name": "Chelsea Station",
                    "type": "commuter_rail",
                    "location": {"latitude": 42.3917, "longitude": -71.0328}
                }
            ]
        else:
            # Return a generic transportation hub for other cities
            return [
                {
                    "id": f"hub-{city.lower()}-1",
                    "name": f"{city} Transit Center",
                    "type": "transit_center",
                    "description": f"Main transit center in {city}."
                }
            ]

    async def geocode_location(self, address: str) -> Optional[Location]:
        """Geocode an address to get latitude and longitude"""
        try:
            if not self.ipstack_api_key:
                self.logger.warning("IPStack API key not found, using mock geocoding")
                return self._mock_geocode(address)

            # In a real implementation, this would use a geocoding API
            # For now, we'll use IPStack API for demonstration
            response = requests.get(
                f"http://api.ipstack.com/check",
                params={
                    "access_key": self.ipstack_api_key,
                    "format": 1
                }
            )

            if response.status_code == 200:
                data = response.json()
                return Location(
                    latitude=data.get("latitude"),
                    longitude=data.get("longitude"),
                    city=data.get("city"),
                    state=data.get("region_code"),
                    zip_code=data.get("zip")
                )
            else:
                self.logger.error(f"Geocoding API error: {response.status_code}")
                return self._mock_geocode(address)

        except Exception as e:
            self.logger.error(f"Error geocoding address: {str(e)}")
            return self._mock_geocode(address)

    def _mock_geocode(self, address: str) -> Location:
        """Mock geocoding for testing"""
        # Extract city from address if possible
        address_lower = address.lower()

        for city in GATEWAY_CITIES:
            if city.lower() in address_lower:
                if city == "Lawrence":
                    return Location(
                        latitude=42.7070,
                        longitude=-71.1631,
                        city="Lawrence",
                        state="MA",
                        zip_code="01840"
                    )
                elif city == "Chelsea":
                    return Location(
                        latitude=42.3917,
                        longitude=-71.0328,
                        city="Chelsea",
                        state="MA",
                        zip_code="02150"
                    )
                else:
                    # Return mock coordinates for other Gateway Cities
                    return Location(
                        latitude=42.0000,
                        longitude=-71.0000,
                        city=city,
                        state="MA"
                    )

        # Default to Boston if no city is found
        return Location(
            latitude=42.3601,
            longitude=-71.0589,
            city="Boston",
            state="MA",
            zip_code="02108"
        )

    async def is_ej_community(self, location: Location) -> Dict[str, Any]:
        """Check if a location is in an EJ community"""
        try:
            # In a real implementation, this would query a database or API
            # For now, we'll use our hardcoded data
            if location.city in self.ej_communities_data:
                ej_data = self.ej_communities_data[location.city]
                return {
                    "is_ej_community": True,
                    "city": location.city,
                    "ej_criteria": ej_data["ej_criteria"],
                    "demographics": ej_data["demographics"]
                }

            # Check if it's a Gateway City (which may have EJ census tracts)
            if location.city in GATEWAY_CITIES:
                return {
                    "is_ej_community": "partial",
                    "city": location.city,
                    "is_gateway_city": True,
                    "note": "This Gateway City contains Environmental Justice census tracts. More specific location information is needed to determine EJ status."
                }

            return {
                "is_ej_community": False,
                "city": location.city,
                "is_gateway_city": location.city in GATEWAY_CITIES
            }

        except Exception as e:
            self.logger.error(f"Error checking EJ community status: {str(e)}")
            return {"is_ej_community": False, "error": str(e)}

    async def find_nearby_opportunities(self, location: Location, radius_miles: float = 5.0,
                                       opportunity_types: List[str] = None) -> List[Dict[str, Any]]:
        """Find clean energy opportunities near a location"""
        try:
            # Set default opportunity types if None
            opportunity_types = opportunity_types or ["job", "training", "community_project"]

            # In a real implementation, this would query a spatial database using radius_miles
            # For now, we'll use our hardcoded data
            self.logger.info(f"Finding opportunities within {radius_miles} miles of {location.city}")

            # Get opportunities for the city
            city_opportunities = []
            if location.city in self.gateway_cities_data:
                city_data = self.gateway_cities_data[location.city]
                city_opportunities = city_data["clean_energy_opportunities"]

            # Filter by type
            filtered_opportunities = [
                opp for opp in city_opportunities
                if opp.get("type") in opportunity_types
            ]

            # Add distance information (mock)
            for opp in filtered_opportunities:
                opp["distance_miles"] = 2.0  # Mock distance
                opp["transportation_options"] = self._get_mock_transportation_options(location, opp)

            return filtered_opportunities

        except Exception as e:
            self.logger.error(f"Error finding nearby opportunities: {str(e)}")
            return []

    def _get_mock_transportation_options(self, from_location: Location,
                                        to_opportunity: Dict[str, Any]) -> List[TransportationOption]:
        """Get mock transportation options between locations"""
        # In a real implementation, this would use a transportation API with from_location and to_opportunity
        # parameters to calculate real routes and distances
        self.logger.debug(f"Getting transportation options from {from_location.city} to opportunity {to_opportunity.get('name', 'Unknown')}")
        return [
            TransportationOption(
                mode="transit",
                duration_minutes=30,
                distance_miles=3.5,
                cost=2.40,
                transfers=1,
                accessibility_score=0.8
            ),
            TransportationOption(
                mode="driving",
                duration_minutes=15,
                distance_miles=4.2,
                cost=1.50,  # Gas estimate
                accessibility_score=0.9
            ),
            TransportationOption(
                mode="walking",
                duration_minutes=60,
                distance_miles=3.0,
                cost=0.0,
                accessibility_score=0.7
            )
        ]

    async def analyze_transportation_access(self, location: Location,
                                           opportunity_location: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze transportation access between locations"""
        try:
            # In a real implementation, this would use a transportation API
            # For now, we'll return mock data

            options = self._get_mock_transportation_options(location, {"location": opportunity_location})

            # Calculate overall accessibility score
            transit_option = next((opt for opt in options if opt.mode == "transit"), None)
            transit_score = transit_option.accessibility_score if transit_option else 0.0

            walking_option = next((opt for opt in options if opt.mode == "walking"), None)
            walking_score = walking_option.accessibility_score if walking_option else 0.0

            overall_score = (transit_score * 0.7) + (walking_score * 0.3)

            return {
                "transportation_options": [vars(opt) for opt in options],
                "best_option": vars(min(options, key=lambda x: x.duration_minutes)),
                "lowest_cost_option": vars(min(options, key=lambda x: x.cost)),
                "accessibility_score": overall_score,
                "has_public_transit": any(opt.mode == "transit" for opt in options),
                "walkable": any(opt.mode == "walking" and opt.duration_minutes <= 30 for opt in options)
            }

        except Exception as e:
            self.logger.error(f"Error analyzing transportation access: {str(e)}")
            return {"error": str(e)}

    async def get_community_projects(self, location: Location) -> List[Dict[str, Any]]:
        """Get community-based clean energy projects"""
        try:
            # In a real implementation, this would query a database
            # For now, we'll filter our hardcoded opportunities

            opportunities = await self.find_nearby_opportunities(
                location,
                radius_miles=10.0,
                opportunity_types=["community_project"]
            )

            return opportunities

        except Exception as e:
            self.logger.error(f"Error getting community projects: {str(e)}")
            return []

    async def get_ej_community_profile(self, city: str) -> Dict[str, Any]:
        """Get detailed profile of an EJ community"""
        try:
            if city in self.ej_communities_data:
                ej_data = self.ej_communities_data[city]
                gateway_data = self.gateway_cities_data.get(city, {})

                # Combine data for a comprehensive profile
                return {
                    "city": city,
                    "is_ej_community": True,
                    "is_gateway_city": city in GATEWAY_CITIES,
                    "ej_criteria": ej_data["ej_criteria"],
                    "demographics": ej_data["demographics"],
                    "clean_energy_opportunities": gateway_data.get("clean_energy_opportunities", []),
                    "transportation_hubs": gateway_data.get("transportation_hubs", []),
                    "community_resources": self._get_mock_community_resources(city)
                }
            elif city in GATEWAY_CITIES:
                gateway_data = self.gateway_cities_data.get(city, {})
                return {
                    "city": city,
                    "is_ej_community": False,
                    "is_gateway_city": True,
                    "clean_energy_opportunities": gateway_data.get("clean_energy_opportunities", []),
                    "transportation_hubs": gateway_data.get("transportation_hubs", []),
                    "community_resources": self._get_mock_community_resources(city)
                }
            else:
                return {
                    "city": city,
                    "is_ej_community": False,
                    "is_gateway_city": False,
                    "note": "This location is not identified as an Environmental Justice community or Gateway City."
                }

        except Exception as e:
            self.logger.error(f"Error getting EJ community profile: {str(e)}")
            return {"error": str(e)}

    def _get_mock_community_resources(self, city: str) -> List[Dict[str, Any]]:
        """Get mock community resources for a city"""
        # In a real implementation, this would query a database
        if city == "Lawrence":
            return [
                {
                    "id": "res-1",
                    "name": "Lawrence CommunityWorks",
                    "type": "community_organization",
                    "services": ["job training", "financial education", "community development"],
                    "website": "https://www.lawrencecommunityworks.org/"
                },
                {
                    "id": "res-2",
                    "name": "Groundwork Lawrence",
                    "type": "environmental_organization",
                    "services": ["environmental education", "green jobs", "community gardens"],
                    "website": "https://groundworklawrence.org/"
                }
            ]
        elif city == "Chelsea":
            return [
                {
                    "id": "res-3",
                    "name": "GreenRoots Chelsea",
                    "type": "environmental_justice_organization",
                    "services": ["environmental advocacy", "community organizing", "climate resilience"],
                    "website": "https://www.greenrootschelsea.org/"
                }
            ]
        else:
            # Return generic resources for other cities
            return [
                {
                    "id": f"res-{city.lower()}-1",
                    "name": f"{city} Community Development",
                    "type": "community_organization",
                    "services": ["community development", "housing assistance"]
                }
            ]

# Example usage
async def main():
    """Example usage of the EJ Geospatial Tool"""
    tool = EJGeospatialTool()

    # Geocode an address
    location = await tool.geocode_location("Lawrence, MA")
    print(f"Geocoded location: {location}")

    # Check if it's an EJ community
    ej_status = await tool.is_ej_community(location)
    print(f"EJ community status: {ej_status}")

    # Find nearby opportunities
    opportunities = await tool.find_nearby_opportunities(location)
    print(f"Found {len(opportunities)} opportunities")

    # Get community profile
    profile = await tool.get_ej_community_profile(location.city)
    print(f"Community profile: {profile}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
