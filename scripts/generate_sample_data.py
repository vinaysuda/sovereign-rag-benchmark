import os


def create_synthetic_directives() -> None:
    """Generates fake EASA directives to test the ingestion pipeline safely."""
    output_dir = "data/raw"
    os.makedirs(output_dir, exist_ok=True)

    sample_text = """
    EUROPEAN UNION AVIATION SAFETY AGENCY (EASA)
    AIRWORTHINESS DIRECTIVE
    
    AD No.: 2024-0015
    Issued: 15 May 2024
    Design Approval Holder: Airbus
    Type/Model designation(s): A320 family aeroplanes
    
    Subject: Landing Gear - Main Landing Gear (MLG) Torque Specifications
    
    Reason:
    During routine maintenance, it was discovered that the torque values applied to the 
    MLG hinge pins may degrade over 10,000 flight cycles. This condition, if not detected 
    and corrected, could lead to MLG collapse during landing.
    
    Required Action(s) and Compliance Time(s):
    Within 500 flight cycles after the effective date of this AD, perform a detailed 
    inspection of the MLG hinge pins. Re-torque the retaining nuts to a strict 
    specification of 145 Nm (Newton meters). 
    
    Supplier Qualification:
    All replacement titanium fasteners must be sourced from suppliers holding a 
    valid EASA Part-21 Subpart G approval.
    """

    file_path = os.path.join(output_dir, "AD_2024_0015_Synthetic.txt")
    with open(file_path, "w") as f:
        f.write(sample_text.strip())

    print(f"✅ Generated synthetic regulatory data at: {file_path}")
    print("You can now run `uv run python src/engine/ingest.py` to embed this document.")


if __name__ == "__main__":
    create_synthetic_directives()
