#!/usr/bin/env python3
"""
Simple test script for the MA Clean Tech Ecosystem Assistant.
This script only tests components that don't require external dependencies.
"""

import os
import sys
import json

# Add the current directory to the path so we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

print("===== MA Clean Tech Ecosystem Local Functionality Test =====")

# Test international prompts
print("\n1. Testing International Prompts...")
try:
    from prompts.international_prompts import (
        get_credential_equivalency_prompt, 
        CREDENTIAL_EVALUATION_SYSTEM_PROMPT
    )
    
    # Test system prompt
    if CREDENTIAL_EVALUATION_SYSTEM_PROMPT and len(CREDENTIAL_EVALUATION_SYSTEM_PROMPT) > 100:
        print("✅ System prompt available and valid")
    
    # Test prompt generation function
    prompt = get_credential_equivalency_prompt(
        country="Germany", 
        credential="Diplom-Ingenieur in Electrical Engineering", 
        field="Renewable Energy"
    )
    
    if prompt and isinstance(prompt, str) and len(prompt) > 100:
        print("✅ Prompt generation function works correctly")
        print(f"   Sample prompt snippet: '{prompt[:100]}...'")
    else:
        print("❌ Prompt generation function error")
except Exception as e:
    print(f"❌ International prompts error: {str(e)}")

# Test military prompts
print("\n2. Testing Military Prompts...")
try:
    from prompts.military_prompts import (
        get_skill_translation_prompt,
        MILITARY_TRANSITION_SYSTEM_PROMPT
    )
    
    # Test system prompt
    if MILITARY_TRANSITION_SYSTEM_PROMPT and len(MILITARY_TRANSITION_SYSTEM_PROMPT) > 100:
        print("✅ Military system prompt available and valid")
    
    # Test prompt generation function
    prompt = get_skill_translation_prompt(
        mos="11B Infantry", 
        branch="Army", 
        years_experience=4
    )
    
    if prompt and isinstance(prompt, str) and len(prompt) > 100:
        print("✅ Military prompt generation function works correctly")
        print(f"   Sample prompt snippet: '{prompt[:100]}...'")
    else:
        print("❌ Military prompt generation function error")
except Exception as e:
    print(f"❌ Military prompts error: {str(e)}")

# Test constants and configuration
print("\n3. Testing Constants...")
try:
    # Test loading constants
    if os.path.exists(os.path.join(current_dir, "constants.py")):
        print("✅ Constants file exists")
        
        # Try importing constants
        try:
            sys.path.insert(0, current_dir)
            from constants import ACT_COMPANIES
            if ACT_COMPANIES and len(ACT_COMPANIES) > 0:
                print(f"✅ ACT_COMPANIES data available ({len(ACT_COMPANIES)} companies)")
            else:
                print("⚠️ ACT_COMPANIES is empty")
        except ImportError as e:
            print(f"⚠️ Could not import constants: {e}")
    else:
        print("❌ Constants file not found")
except Exception as e:
    print(f"❌ Constants test error: {str(e)}")

# Test file structure
print("\n4. Testing File Structure...")
try:
    # Check key directories
    directories = ["app", "components", "lib", "prompts", "tools"]
    for directory in directories:
        if os.path.exists(os.path.join(current_dir, directory)):
            print(f"✅ {directory}/ directory exists")
        else:
            print(f"⚠️ {directory}/ directory not found")
            
    # Check key files
    files = ["app.py", "utils.py", "requirements.txt"]
    for file in files:
        if os.path.exists(os.path.join(current_dir, file)):
            print(f"✅ {file} exists")
        else:
            print(f"⚠️ {file} not found")
except Exception as e:
    print(f"❌ File structure test error: {str(e)}")

print("\n===== Test Complete =====") 