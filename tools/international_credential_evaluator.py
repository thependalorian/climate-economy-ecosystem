#!/usr/bin/env python3
"""
International Credential Evaluator for Massachusetts Clean Energy Ecosystem

This tool evaluates international credentials and provides guidance for
international professionals seeking to work in the Massachusetts clean energy sector.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

from tools.base_tool import BaseTool, ToolError, ToolConfigurationError, ToolExecutionError

# Load environment variables
load_dotenv()

# Constants
MASSACHUSETTS_LICENSING_BOARDS = {
    "engineering": "Board of Registration of Professional Engineers and Professional Land Surveyors",
    "architecture": "Board of Registration of Architects",
    "electrical": "Board of State Examiners of Electricians",
    "plumbing": "Board of State Examiners of Plumbers and Gas Fitters",
    "hvac": "Bureau of Pipefitters, Refrigeration Technicians and Sprinklerfitters",
    "construction_supervisor": "Board of Building Regulations and Standards",
    "energy_auditor": "Department of Energy Resources"
}

@dataclass
class Credential:
    """International credential data structure"""
    name: str
    type: str  # degree, certification, license
    institution: str
    country: str
    year_obtained: int
    field: str
    description: Optional[str] = None
    documentation: Optional[List[str]] = None

@dataclass
class CredentialEvaluation:
    """Credential evaluation result"""
    original_credential: Credential
    massachusetts_equivalent: Optional[str] = None
    recognition_status: str = "unknown"  # "full", "partial", "not recognized", "unknown"
    gaps: List[str] = None
    required_steps: List[Dict[str, Any]] = None
    licensing_board: Optional[str] = None
    estimated_timeline_months: Optional[int] = None

    def __post_init__(self):
        if self.gaps is None:
            self.gaps = []
        if self.required_steps is None:
            self.required_steps = []

class InternationalCredentialEvaluator(BaseTool):
    """Tool for evaluating international credentials for Massachusetts equivalency"""

    def requires_openai(self) -> bool:
        """This tool requires OpenAI for credential analysis"""
        return True

    def requires_supabase(self) -> bool:
        """This tool requires Supabase for data storage"""
        return True

    async def initialize(self):
        """Initialize the International Credential Evaluator"""
        await super().initialize()

        # Check if OpenAI API key is available
        if not self.openai:
            self.logger.warning("OpenAI client not available, some functionality will be limited")

        # Load data
        try:
            self.credential_mappings = self._load_credential_mappings()
            self.licensing_requirements = self._load_licensing_requirements()
            self.logger.info("International Credential Evaluator initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing International Credential Evaluator: {str(e)}")
            raise ToolConfigurationError(f"Error initializing International Credential Evaluator: {str(e)}")

    async def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Run the tool with the specified action"""
        self._check_availability()
        self.logger.info(f"Running {action} with {kwargs}")

        try:
            if action == "evaluate_credential":
                if "credential" not in kwargs:
                    raise ToolExecutionError("Credential is required for evaluate_credential action")
                return await self.evaluate_credential(kwargs.get("credential"), kwargs.get("target_field"))

            elif action == "generate_regulatory_roadmap":
                if "credentials" not in kwargs or "target_field" not in kwargs or "origin_country" not in kwargs:
                    raise ToolExecutionError("Credentials, target_field, and origin_country are required for generate_regulatory_roadmap action")
                return await self.generate_regulatory_roadmap(
                    kwargs.get("credentials"),
                    kwargs.get("target_field"),
                    kwargs.get("origin_country")
                )

            elif action == "translate_experience":
                if "experience" not in kwargs or "target_field" not in kwargs or "origin_country" not in kwargs:
                    raise ToolExecutionError("Experience, target_field, and origin_country are required for translate_experience action")
                return await self.translate_experience(
                    kwargs.get("experience"),
                    kwargs.get("target_field"),
                    kwargs.get("origin_country")
                )

            elif action == "get_cultural_integration_guide":
                if "origin_country" not in kwargs:
                    raise ToolExecutionError("Origin country is required for get_cultural_integration_guide action")
                return await self.get_cultural_integration_guide(kwargs.get("origin_country"))

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
            "credential_mappings_count": len(self.credential_mappings) if hasattr(self, "credential_mappings") else 0,
            "licensing_requirements_count": len(self.licensing_requirements) if hasattr(self, "licensing_requirements") else 0
        })

        return health

    async def run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Run the tool with the specified action"""
        self._check_availability()
        self.logger.info(f"Running {action} with {kwargs}")

        try:
            if action == "evaluate_credential":
                if "credential" not in kwargs:
                    raise ToolExecutionError("Credential is required for evaluate_credential action")
                return await self.evaluate_credential(kwargs.get("credential"), kwargs.get("target_field"))

            elif action == "generate_regulatory_roadmap":
                if "credentials" not in kwargs or "target_field" not in kwargs or "origin_country" not in kwargs:
                    raise ToolExecutionError("Credentials, target_field, and origin_country are required for generate_regulatory_roadmap action")
                return await self.generate_regulatory_roadmap(
                    kwargs.get("credentials"),
                    kwargs.get("target_field"),
                    kwargs.get("origin_country")
                )

            elif action == "translate_experience":
                if "experience" not in kwargs or "target_field" not in kwargs or "origin_country" not in kwargs:
                    raise ToolExecutionError("Experience, target_field, and origin_country are required for translate_experience action")
                return await self.translate_experience(
                    kwargs.get("experience"),
                    kwargs.get("target_field"),
                    kwargs.get("origin_country")
                )

            elif action == "get_cultural_integration_guide":
                if "origin_country" not in kwargs:
                    raise ToolExecutionError("Origin country is required for get_cultural_integration_guide action")
                return await self.get_cultural_integration_guide(kwargs.get("origin_country"))

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
            "credential_mappings_count": len(self.credential_mappings) if hasattr(self, "credential_mappings") else 0,
            "licensing_requirements_count": len(self.licensing_requirements) if hasattr(self, "licensing_requirements") else 0
        })

        return health

    def _load_credential_mappings(self) -> Dict[str, Any]:
        """Load credential mappings data"""
        try:
            # In a real implementation, this would load from a database or API
            # For now, we'll use a simplified version with hardcoded data
            mappings = {
                "engineering": {
                    "Brazil": {
                        "Bacharel em Engenharia": {
                            "massachusetts_equivalent": "Bachelor of Science in Engineering",
                            "recognition_status": "partial",
                            "gaps": ["State-specific code knowledge", "Professional Engineer (PE) licensing"],
                            "licensing_board": "Board of Registration of Professional Engineers and Professional Land Surveyors"
                        }
                    },
                    "India": {
                        "Bachelor of Technology": {
                            "massachusetts_equivalent": "Bachelor of Science in Engineering",
                            "recognition_status": "partial",
                            "gaps": ["State-specific code knowledge", "Professional Engineer (PE) licensing"],
                            "licensing_board": "Board of Registration of Professional Engineers and Professional Land Surveyors"
                        }
                    },
                    "Nigeria": {
                        "Bachelor of Engineering": {
                            "massachusetts_equivalent": "Bachelor of Science in Engineering",
                            "recognition_status": "partial",
                            "gaps": ["State-specific code knowledge", "Professional Engineer (PE) licensing"],
                            "licensing_board": "Board of Registration of Professional Engineers and Professional Land Surveyors"
                        }
                    }
                },
                "electrical": {
                    "Brazil": {
                        "Técnico em Eletrotécnica": {
                            "massachusetts_equivalent": "Journeyman Electrician (partial)",
                            "recognition_status": "partial",
                            "gaps": ["Massachusetts Electrical Code", "Supervised work experience in Massachusetts"],
                            "licensing_board": "Board of State Examiners of Electricians"
                        }
                    },
                    "Nigeria": {
                        "National Diploma in Electrical Engineering": {
                            "massachusetts_equivalent": "Journeyman Electrician (partial)",
                            "recognition_status": "partial",
                            "gaps": ["Massachusetts Electrical Code", "Supervised work experience in Massachusetts"],
                            "licensing_board": "Board of State Examiners of Electricians"
                        }
                    }
                },
                "solar_installation": {
                    "multiple_countries": {
                        "NABCEP PV Installation Professional": {
                            "massachusetts_equivalent": "NABCEP PV Installation Professional",
                            "recognition_status": "full",
                            "gaps": [],
                            "licensing_board": None
                        }
                    }
                }
            }
            self.logger.info(f"Loaded credential mappings for {len(mappings)} fields")
            return mappings
        except Exception as e:
            self.logger.error(f"Error loading credential mappings: {str(e)}")
            return {}

    def _load_licensing_requirements(self) -> Dict[str, Any]:
        """Load licensing requirements data"""
        try:
            # In a real implementation, this would load from a database or API
            # For now, we'll use a simplified version with hardcoded data
            requirements = {
                "engineering": {
                    "professional_engineer": {
                        "education": "ABET-accredited engineering degree or equivalent",
                        "experience": "4 years of qualifying engineering experience",
                        "exams": ["Fundamentals of Engineering (FE)", "Principles and Practice of Engineering (PE)"],
                        "application_fee": 150,
                        "renewal": "Every 2 years",
                        "continuing_education": "30 PDHs every 2 years",
                        "board": "Board of Registration of Professional Engineers and Professional Land Surveyors",
                        "website": "https://www.mass.gov/orgs/board-of-registration-of-professional-engineers-and-professional-land-surveyors"
                    }
                },
                "electrical": {
                    "journeyman_electrician": {
                        "education": "600 hours of electrical code and theory instruction",
                        "experience": "4 years (8,000 hours) of work experience under master electrician",
                        "exams": ["Massachusetts Journeyman Electrician Exam"],
                        "application_fee": 100,
                        "renewal": "Every 3 years",
                        "continuing_education": "21 hours every 3 years",
                        "board": "Board of State Examiners of Electricians",
                        "website": "https://www.mass.gov/orgs/board-of-state-examiners-of-electricians"
                    },
                    "master_electrician": {
                        "education": "Journeyman electrician license",
                        "experience": "1 year (2,000 hours) as journeyman electrician",
                        "exams": ["Massachusetts Master Electrician Exam"],
                        "application_fee": 150,
                        "renewal": "Every 3 years",
                        "continuing_education": "21 hours every 3 years",
                        "board": "Board of State Examiners of Electricians",
                        "website": "https://www.mass.gov/orgs/board-of-state-examiners-of-electricians"
                    }
                },
                "solar_installation": {
                    "solar_pv_installer": {
                        "note": "Massachusetts does not have a specific solar installer license. Work falls under electrical or construction supervisor licenses depending on scope.",
                        "related_licenses": ["Journeyman Electrician", "Master Electrician", "Construction Supervisor"],
                        "certifications": ["NABCEP PV Installation Professional (recommended but not required)"]
                    }
                }
            }
            self.logger.info(f"Loaded licensing requirements for {len(requirements)} fields")
            return requirements
        except Exception as e:
            self.logger.error(f"Error loading licensing requirements: {str(e)}")
            return {}

    async def evaluate_credential(self, credential: Credential, target_field: str) -> CredentialEvaluation:
        """Evaluate an international credential for Massachusetts equivalency"""
        try:
            # Check if we have a direct mapping
            field_mappings = self.credential_mappings.get(target_field, {})
            country_mappings = field_mappings.get(credential.country, field_mappings.get("multiple_countries", {}))
            credential_mapping = country_mappings.get(credential.name, None)

            if credential_mapping:
                # We have a direct mapping
                return CredentialEvaluation(
                    original_credential=credential,
                    massachusetts_equivalent=credential_mapping.get("massachusetts_equivalent"),
                    recognition_status=credential_mapping.get("recognition_status", "unknown"),
                    gaps=credential_mapping.get("gaps", []),
                    licensing_board=credential_mapping.get("licensing_board"),
                    required_steps=self._generate_required_steps(credential, target_field, credential_mapping)
                )
            else:
                # No direct mapping, use AI to generate an evaluation
                return await self._generate_ai_evaluation(credential, target_field)

        except Exception as e:
            self.logger.error(f"Error evaluating credential: {str(e)}")
            return CredentialEvaluation(
                original_credential=credential,
                recognition_status="error",
                gaps=["Error processing credential evaluation"],
                required_steps=[{"step": "Contact a credential evaluation service", "details": "Due to system limitations, please contact a professional credential evaluation service."}]
            )

    def _generate_required_steps(self, credential: Credential, target_field: str,
                               credential_mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate required steps for credential recognition"""
        steps = []

        # Get licensing requirements if applicable
        licensing_board = credential_mapping.get("licensing_board")
        if licensing_board:
            field_requirements = self.licensing_requirements.get(target_field, {})
            license_types = list(field_requirements.keys())

            if license_types:
                # Add credential evaluation step
                steps.append({
                    "step": "Get credential evaluated",
                    "details": "Have your credentials evaluated by a recognized evaluation service such as World Education Services (WES) or Educational Credential Evaluators (ECE).",
                    "timeline_months": 2,
                    "estimated_cost": "$200-400",
                    "resources": ["https://www.wes.org/", "https://www.ece.org/"]
                })

                # Add education gap fulfillment if needed
                if "education" in credential_mapping.get("gaps", []):
                    steps.append({
                        "step": "Complete additional education",
                        "details": "Enroll in courses to fulfill educational requirements.",
                        "timeline_months": 6,
                        "estimated_cost": "$1,000-3,000",
                        "resources": ["https://www.mass.edu/", "https://www.bhcc.edu/"]
                    })

                # Add experience requirements
                for license_type in license_types:
                    license_info = field_requirements.get(license_type, {})
                    if license_info.get("experience"):
                        steps.append({
                            "step": f"Gain required experience for {license_type}",
                            "details": license_info.get("experience"),
                            "timeline_months": 12,
                            "resources": [license_info.get("website")]
                        })

                # Add exam requirements
                for license_type in license_types:
                    license_info = field_requirements.get(license_type, {})
                    if license_info.get("exams"):
                        for exam in license_info.get("exams", []):
                            steps.append({
                                "step": f"Pass {exam} exam",
                                "details": f"Register and prepare for the {exam} examination.",
                                "timeline_months": 3,
                                "estimated_cost": "$200-500",
                                "resources": [license_info.get("website")]
                            })

                # Add license application step
                steps.append({
                    "step": "Apply for Massachusetts license",
                    "details": f"Submit application to {licensing_board}.",
                    "timeline_months": 1,
                    "estimated_cost": "$100-200",
                    "resources": [field_requirements.get(license_types[0], {}).get("website")]
                })
        else:
            # No licensing board, but may still need credential evaluation
            steps.append({
                "step": "Get credential evaluated",
                "details": "Have your credentials evaluated by a recognized evaluation service such as World Education Services (WES) or Educational Credential Evaluators (ECE).",
                "timeline_months": 2,
                "estimated_cost": "$200-400",
                "resources": ["https://www.wes.org/", "https://www.ece.org/"]
            })

            # Add job search step
            steps.append({
                "step": "Apply for positions with evaluated credentials",
                "details": "Include your credential evaluation with job applications to help employers understand your qualifications.",
                "timeline_months": 3,
                "resources": ["https://www.masscec.com/jobs"]
            })

        return steps

    async def _generate_ai_evaluation(self, credential: Credential, target_field: str) -> CredentialEvaluation:
        """Generate credential evaluation using AI"""
        try:
            if not self.openai:
                self.logger.warning("OpenAI client not available, using mock evaluation")
                return self._mock_evaluation(credential, target_field)

            import openai
            client = openai.OpenAI(api_key=self.openai_api_key)

            # Create prompt for OpenAI
            prompt = f"""
            Evaluate the following international credential for Massachusetts equivalency in the {target_field} field:

            Credential: {credential.name}
            Type: {credential.type}
            Institution: {credential.institution}
            Country: {credential.country}
            Year Obtained: {credential.year_obtained}
            Field: {credential.field}
            Description: {credential.description or 'Not provided'}

            Please provide:
            1. Massachusetts equivalent (if any)
            2. Recognition status (full, partial, not recognized)
            3. Gaps that need to be addressed
            4. Licensing board in Massachusetts (if applicable)
            5. Required steps for recognition
            6. Estimated timeline in months

            Format the response as JSON.
            """

            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a credential evaluation expert specializing in Massachusetts professional licensing requirements."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            # Parse response
            result = json.loads(response.choices[0].message.content)

            # Create evaluation object
            evaluation = CredentialEvaluation(
                original_credential=credential,
                massachusetts_equivalent=result.get("massachusetts_equivalent"),
                recognition_status=result.get("recognition_status", "unknown"),
                gaps=result.get("gaps", []),
                required_steps=result.get("required_steps", []),
                licensing_board=result.get("licensing_board"),
                estimated_timeline_months=result.get("estimated_timeline_months")
            )

            return evaluation

        except Exception as e:
            self.logger.error(f"Error generating AI evaluation: {str(e)}")
            return self._mock_evaluation(credential, target_field)

    def _mock_evaluation(self, credential: Credential, target_field: str) -> CredentialEvaluation:
        """Generate a mock evaluation for testing"""
        if target_field == "engineering":
            return CredentialEvaluation(
                original_credential=credential,
                massachusetts_equivalent="Bachelor of Science in Engineering (evaluation needed)",
                recognition_status="partial",
                gaps=["State-specific code knowledge", "Professional Engineer (PE) licensing"],
                licensing_board="Board of Registration of Professional Engineers and Professional Land Surveyors",
                required_steps=[
                    {
                        "step": "Get credential evaluated by WES or ECE",
                        "timeline_months": 2,
                        "estimated_cost": "$200-400"
                    },
                    {
                        "step": "Pass the Fundamentals of Engineering (FE) exam",
                        "timeline_months": 3,
                        "estimated_cost": "$175"
                    },
                    {
                        "step": "Gain 4 years of qualifying engineering experience",
                        "timeline_months": 48
                    },
                    {
                        "step": "Pass the Principles and Practice of Engineering (PE) exam",
                        "timeline_months": 3,
                        "estimated_cost": "$375"
                    },
                    {
                        "step": "Apply for PE license",
                        "timeline_months": 1,
                        "estimated_cost": "$150"
                    }
                ],
                estimated_timeline_months=57
            )
        elif target_field == "solar_installation":
            return CredentialEvaluation(
                original_credential=credential,
                massachusetts_equivalent="Solar PV Installer (requires electrical license)",
                recognition_status="partial",
                gaps=["Massachusetts Electrical Code", "Supervised work experience in Massachusetts"],
                licensing_board="Board of State Examiners of Electricians",
                required_steps=[
                    {
                        "step": "Get credential evaluated by WES or ECE",
                        "timeline_months": 2,
                        "estimated_cost": "$200-400"
                    },
                    {
                        "step": "Complete 600 hours of electrical code and theory instruction",
                        "timeline_months": 12,
                        "estimated_cost": "$5,000-8,000"
                    },
                    {
                        "step": "Gain 4 years (8,000 hours) of work experience under master electrician",
                        "timeline_months": 48
                    },
                    {
                        "step": "Pass Massachusetts Journeyman Electrician Exam",
                        "timeline_months": 3,
                        "estimated_cost": "$100"
                    },
                    {
                        "step": "Consider NABCEP PV Installation Professional certification",
                        "timeline_months": 6,
                        "estimated_cost": "$500-1,000"
                    }
                ],
                estimated_timeline_months=71
            )
        else:
            return CredentialEvaluation(
                original_credential=credential,
                massachusetts_equivalent="Evaluation needed",
                recognition_status="unknown",
                gaps=["Specific evaluation needed"],
                required_steps=[
                    {
                        "step": "Get credential evaluated by WES or ECE",
                        "timeline_months": 2,
                        "estimated_cost": "$200-400"
                    },
                    {
                        "step": "Consult with Massachusetts licensing board",
                        "timeline_months": 1
                    }
                ],
                estimated_timeline_months=3
            )

    async def generate_regulatory_roadmap(self, credentials: List[Credential],
                                        target_field: str, origin_country: str) -> Dict[str, Any]:
        """Generate a regulatory roadmap for an international professional"""
        try:
            # Evaluate each credential
            evaluations = []
            for credential in credentials:
                evaluation = await self.evaluate_credential(credential, target_field)
                evaluations.append(evaluation)

            # Determine the most relevant licensing board
            licensing_boards = [eval.licensing_board for eval in evaluations if eval.licensing_board]
            relevant_board = licensing_boards[0] if licensing_boards else MASSACHUSETTS_LICENSING_BOARDS.get(target_field)

            # Combine all required steps
            all_steps = []
            for evaluation in evaluations:
                all_steps.extend(evaluation.required_steps)

            # Remove duplicate steps
            unique_steps = []
            step_descriptions = set()
            for step in all_steps:
                step_desc = step.get("step")
                if step_desc not in step_descriptions:
                    step_descriptions.add(step_desc)
                    unique_steps.append(step)

            # Sort steps by timeline
            sorted_steps = sorted(unique_steps, key=lambda x: x.get("timeline_months", 0))

            # Calculate total timeline
            total_timeline = sum(step.get("timeline_months", 0) for step in sorted_steps)

            # Generate document checklist
            document_checklist = self._generate_document_checklist(credentials, target_field, origin_country)

            # Check for reciprocity agreements
            reciprocity = self._check_reciprocity(target_field, origin_country)

            # Generate roadmap
            roadmap = {
                "target_field": target_field,
                "origin_country": origin_country,
                "credentials_evaluated": [vars(eval) for eval in evaluations],
                "licensing_board": relevant_board,
                "regulatory_steps": sorted_steps,
                "document_checklist": document_checklist,
                "estimated_timeline_months": total_timeline,
                "reciprocity_agreements": reciprocity,
                "support_resources": self._get_support_resources(target_field, origin_country)
            }

            return roadmap

        except Exception as e:
            self.logger.error(f"Error generating regulatory roadmap: {str(e)}")
            return {
                "error": str(e),
                "target_field": target_field,
                "origin_country": origin_country,
                "regulatory_steps": [
                    {
                        "step": "Consult with a professional credential evaluation service",
                        "details": "Due to the complexity of your situation, please consult with a professional credential evaluation service."
                    }
                ]
            }

    def _generate_document_checklist(self, credentials: List[Credential],
                                   target_field: str, origin_country: str) -> List[Dict[str, Any]]:
        """Generate a document checklist for credential evaluation"""
        checklist = [
            {
                "document": "Original diploma/certificate",
                "requirements": "Original document with official seal/signature",
                "translation_needed": True,
                "notarization_needed": True
            },
            {
                "document": "Official transcripts",
                "requirements": "Sealed envelope from institution or sent directly",
                "translation_needed": True,
                "notarization_needed": True
            },
            {
                "document": "Course descriptions",
                "requirements": "Official descriptions of all relevant courses",
                "translation_needed": True,
                "notarization_needed": False
            },
            {
                "document": "Proof of identity",
                "requirements": "Passport or government-issued ID",
                "translation_needed": False,
                "notarization_needed": True
            }
        ]

        # Add field-specific documents
        if target_field == "engineering":
            checklist.append({
                "document": "Engineering license/registration from home country",
                "requirements": "If applicable",
                "translation_needed": True,
                "notarization_needed": True
            })
        elif target_field == "electrical":
            checklist.append({
                "document": "Proof of work experience",
                "requirements": "Letters from employers detailing specific electrical work performed",
                "translation_needed": True,
                "notarization_needed": True
            })

        return checklist

    def _check_reciprocity(self, target_field: str, origin_country: str) -> Dict[str, Any]:
        """Check for reciprocity agreements between Massachusetts and origin country"""
        # In a real implementation, this would check a database of reciprocity agreements
        # For now, we'll return mock data

        if target_field == "engineering" and origin_country == "Canada":
            return {
                "has_reciprocity": True,
                "agreement_name": "MRA between NCEES and Engineers Canada",
                "details": "Licensed Canadian engineers may qualify for expedited PE licensing through this agreement.",
                "requirements": ["Must be licensed in a Canadian province", "Must have graduated from an accredited program"],
                "website": "https://ncees.org/records/international-registry/"
            }
        elif target_field == "solar_installation" and origin_country in ["Germany", "Australia"]:
            return {
                "has_reciprocity": "partial",
                "details": "NABCEP recognizes certain international solar certifications for partial credit.",
                "requirements": ["Must provide proof of certification", "Must complete additional NABCEP requirements"],
                "website": "https://www.nabcep.org/"
            }
        else:
            return {
                "has_reciprocity": False,
                "details": "No formal reciprocity agreement exists between Massachusetts and " + origin_country + " for " + target_field + "."
            }

    def _get_support_resources(self, target_field: str, origin_country: str) -> List[Dict[str, Any]]:
        """Get support resources for international professionals"""
        # Common resources for all fields and countries
        resources = [
            {
                "name": "Massachusetts Office for Refugees and Immigrants",
                "type": "government",
                "website": "https://www.mass.gov/orgs/office-for-refugees-and-immigrants",
                "services": ["Professional licensing guidance", "Referrals to credential evaluation services"]
            },
            {
                "name": "World Education Services (WES)",
                "type": "credential_evaluation",
                "website": "https://www.wes.org/",
                "services": ["Credential evaluation", "Educational equivalency reports"]
            },
            {
                "name": "Educational Credential Evaluators (ECE)",
                "type": "credential_evaluation",
                "website": "https://www.ece.org/",
                "services": ["Credential evaluation", "Course-by-course analysis"]
            },
            {
                "name": "Massachusetts Immigrant and Refugee Advocacy Coalition (MIRA)",
                "type": "nonprofit",
                "website": "https://www.miracoalition.org/",
                "services": ["Advocacy", "Legal resources", "Community connections"]
            }
        ]

        # Add field-specific resources
        if target_field == "engineering":
            resources.append({
                "name": "Board of Registration of Professional Engineers and Professional Land Surveyors",
                "type": "licensing_board",
                "website": "https://www.mass.gov/orgs/board-of-registration-of-professional-engineers-and-professional-land-surveyors",
                "services": ["Licensing information", "Application processing"]
            })
            resources.append({
                "name": "National Council of Examiners for Engineering and Surveying (NCEES)",
                "type": "professional_organization",
                "website": "https://ncees.org/",
                "services": ["Exam information", "Credential verification", "Records program"]
            })
        elif target_field == "electrical":
            resources.append({
                "name": "Board of State Examiners of Electricians",
                "type": "licensing_board",
                "website": "https://www.mass.gov/orgs/board-of-state-examiners-of-electricians",
                "services": ["Licensing information", "Application processing"]
            })
        elif target_field == "solar_installation":
            resources.append({
                "name": "North American Board of Certified Energy Practitioners (NABCEP)",
                "type": "certification_organization",
                "website": "https://www.nabcep.org/",
                "services": ["Certification information", "Exam preparation"]
            })
            resources.append({
                "name": "Interstate Renewable Energy Council (IREC)",
                "type": "nonprofit",
                "website": "https://irecusa.org/",
                "services": ["Training program accreditation", "Workforce development resources"]
            })

        # Add country-specific resources
        if origin_country == "Brazil":
            resources.append({
                "name": "Brazilian Association of Massachusetts",
                "type": "community_organization",
                "website": "https://brazilianassociationma.org/",
                "services": ["Community support", "Cultural integration", "Networking"]
            })
        elif origin_country == "India":
            resources.append({
                "name": "India Association of Greater Boston",
                "type": "community_organization",
                "website": "https://iagb.org/",
                "services": ["Community support", "Cultural integration", "Networking"]
            })
        elif origin_country == "Nigeria":
            resources.append({
                "name": "Nigerian American Multi-Service Association",
                "type": "community_organization",
                "website": "https://www.namsa.org/",
                "services": ["Community support", "Cultural integration", "Networking"]
            })

        return resources

# Example usage
async def main():
    """Example usage of the International Credential Evaluator"""
    evaluator = InternationalCredentialEvaluator()

    # Create a sample credential
    credential = Credential(
        name="Bachelor of Engineering",
        type="degree",
        institution="Federal University of Rio de Janeiro",
        country="Brazil",
        year_obtained=2015,
        field="Electrical Engineering",
        description="5-year engineering program with focus on power systems"
    )

    # Evaluate the credential
    evaluation = await evaluator.evaluate_credential(credential, "electrical")
    print(f"Credential evaluation: {evaluation}")

    # Generate a regulatory roadmap
    roadmap = await evaluator.generate_regulatory_roadmap([credential], "electrical", "Brazil")
    print(f"Regulatory roadmap: {roadmap}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
