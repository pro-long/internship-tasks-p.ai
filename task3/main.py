import os
import requests
import argparse
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def load_file(file_path: str, client):
    ext = file_path.split('.')[-1].lower()

    if ext in ("jpg","jpeg"):
        mime = "image/jpeg"
    elif ext == "png":
        mime = "image/png"
    elif ext == "pdf":
        mime = "application/pdf"
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    if file_path.startswith("http"):
        file_data = requests.get(file_path).content
    else:
        with open(file_path, "rb") as f:
            file_data = f.read()

    return types.Part.from_bytes(data=file_data, mime_type=mime)

def test_process_w2():
    fields = {
        "employee": {
            "name": {"first": "Jesan", "last": "Rahaman"},
            "address": {"street": "Katham Dorbosto, Kashiani, Gopalganj", "city": "Gopalganj", "state": "AK", "zip": "8133"},
            "masked_ssn": "XXX-XX-5787"
        },
        "employer": {
            "name": "DesignNext",
            "address": {"street": "Katham Dorbosto, Kashiani, Gopalganj", "city": "Gopalganj", "state": "AK", "zip": "8133"},
            "masked_ein": "XX-XXXX8788"
        },
        "federal_boxes": {
            "1_wages_tips_other_comp": 80000.00,
            "2_federal_income_tax_withheld": 10368.00,
            "3_social_security_wages": 80000.00,
            "4_social_security_tax_withheld": 4960.00,
            "5_medicare_wages_tips": 80000.00,
            "6_medicare_tax_withheld": 1160.00,
            "7_social_security_tips": None,
            "8_allocated_tips": None,
            "9_advance_eic_payment": None,
            "10_dependent_care_benefits": None,
            "11_nonqualified_plans": None,
            "14_other": None
        },
        "other_boxes": {
            "control_number": "9",
            "box_12": [],
            "box_13": {
            "statutory_employee": False,
            "retirement_plan": False,
            "third_party_sick_pay": False
            },
            "box_14": []
        },
        "state_local": {
            "states": [
            {
                "code": "AL",
                "employer_id": "877878878",
                "wages": 80000.00,
                "income_tax": 3835.00
            }
            ],
            "localities": []
        },
            "quality": ["None"]
        }
    insights = "insite: All wages are below the Social Security wage base limit, so no cap was applied."
    return {
        "fields": fields,
        "insights": insights,
    }

def process_w2(file_path: str, test_mode: bool = False) -> dict:
    if test_mode:
        fake = { "fields":{}, "insights":[], "quality":["test_mode_mock"] }
        return fake

    file_part= load_file(file_path, client)
    ext_prompt = open("extraction_prompt.txt").read()
    extract_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[file_part, ext_prompt]
    )
    raw_fields = extract_response.text
    fields = json.loads(raw_fields)

    insight_prompt = open("insight_prompt.txt").read()
    insights_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[ raw_fields, insight_prompt ]
    )
    insights = insights_response.text

    return {
        "fields": fields,
        "insights": insights,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--test_mode")
    args = parser.parse_args()

    if args.test_mode:
        result = test_process_w2()
    elif args.input:
        result = process_w2(args.input)
    print(json.dumps(result))

if __name__ == "__main__":
    main()