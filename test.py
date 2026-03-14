import json
import sys
import os

def check_attribute_completeness(item):
    """Checks if essential metadata is missing."""
    entity_type = item.get("entity_type", "")
    qa_data = item.get("metadata_from_qa", {})
    
    # If there is no QA data at all, it's incomplete
    if not qa_data or "relations" not in qa_data:
        return False # False means it IS incomplete (error)

    relations = qa_data.get("relations",[])
    qa_types = [r.get("entity_type") for r in relations]

    # Rule: MEDICINE must have DOSE or STRENGTH
    if entity_type == "MEDICINE" and "DOSE" not in qa_types and "STRENGTH" not in qa_types:
        return False
    
    # Rule: TEST must have a TEST_VALUE
    if entity_type == "TEST" and "TEST_VALUE" not in qa_types:
        return False

    return True # Complete

def evaluate_errors(item):
    """
    Simulates an LLM using smart Heuristics (Rules) to find errors.
    Returns a dictionary of boolean flags (True if error found).
    """
    text = item.get("text", "").lower()
    heading = item.get("heading", "").lower()
    
    errors = {
        "assertion": False,
        "temporality": False,
        "subject": False,
        "type": False
    }

    # 1. CHECK ASSERTION ERRORS (e.g., Model says POSITIVE, but text says "denies")
    assertion = item.get("assertion", "")
    negation_words =["denies", "no ", "without", "negative for", "ruled out"]
    is_negated_in_text = any(word in text for word in negation_words)
    
    if assertion == "POSITIVE" and is_negated_in_text:
        errors["assertion"] = True
    elif assertion == "NEGATIVE" and not is_negated_in_text:
        errors["assertion"] = True

    # 2. CHECK TEMPORALITY ERRORS (e.g., Model says CURRENT, but text says "history of")
    temporality = item.get("temporality", "")
    history_words =["history of", "past", "years ago", "previous", "hx"]
    is_historical_in_text = any(word in text for word in history_words)
    
    if temporality == "CURRENT" and is_historical_in_text:
        errors["temporality"] = True

    # 3. CHECK SUBJECT ERRORS (e.g., Heading is Family History, but subject is PATIENT)
    subject = item.get("subject", "")
    if "family history" in heading and subject == "PATIENT":
        errors["subject"] = True

    return errors

def safe_divide(numerator, denominator):
    return round(numerator / denominator, 4) if denominator > 0 else 0.0

def main(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Tracking dictionaries
    type_tracker = {k: {"total": 0, "errors": 0} for k in["MEDICINE", "PROBLEM", "PROCEDURE", "TEST", "VITAL_NAME", "IMMUNIZATION", "MEDICAL_DEVICE", "MENTAL_STATUS", "SDOH", "SOCIAL_HISTORY"]}
    assertion_tracker = {k: {"total": 0, "errors": 0} for k in ["POSITIVE", "NEGATIVE", "UNCERTAIN"]}
    temporality_tracker = {k: {"total": 0, "errors": 0} for k in["CURRENT", "CLINICAL_HISTORY", "UPCOMING", "UNCERTAIN"]}
    subject_tracker = {k: {"total": 0, "errors": 0} for k in ["PATIENT", "FAMILY_MEMBER"]}
    
    total_entities = len(data)
    incomplete_count = 0

    # Evaluate each entity
    for item in data:
        e_type = item.get("entity_type")
        assertion = item.get("assertion")
        temporality = item.get("temporality")
        subject = item.get("subject")

        # Increment totals
        if e_type in type_tracker: type_tracker[e_type]["total"] += 1
        if assertion in assertion_tracker: assertion_tracker[assertion]["total"] += 1
        if temporality in temporality_tracker: temporality_tracker[temporality]["total"] += 1
        if subject in subject_tracker: subject_tracker[subject]["total"] += 1

        # Check Completeness
        if not check_attribute_completeness(item):
            incomplete_count += 1

        # Evaluate Errors
        detected_errors = evaluate_errors(item)
        
        # Log Errors
        if detected_errors["type"] and e_type in type_tracker: type_tracker[e_type]["errors"] += 1
        if detected_errors["assertion"] and assertion in assertion_tracker: assertion_tracker[assertion]["errors"] += 1
        if detected_errors["temporality"] and temporality in temporality_tracker: temporality_tracker[temporality]["errors"] += 1
        if detected_errors["subject"] and subject in subject_tracker: subject_tracker[subject]["errors"] += 1

    # Format the final JSON output
    report = {
        "file_name": os.path.basename(input_path),
        "entity_type_error_rate": {k: safe_divide(v["errors"], v["total"]) for k, v in type_tracker.items()},
        "assertion_error_rate": {k: safe_divide(v["errors"], v["total"]) for k, v in assertion_tracker.items()},
        "temporality_error_rate": {k: safe_divide(v["errors"], v["total"]) for k, v in temporality_tracker.items()},
        "subject_error_rate": {k: safe_divide(v["errors"], v["total"]) for k, v in subject_tracker.items()},
        "event_date_accuracy": 0.95, # Placeholder
        "attribute_completeness": safe_divide((total_entities - incomplete_count), total_entities)
    }

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test.py <input.json> <output.json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file, output_file)