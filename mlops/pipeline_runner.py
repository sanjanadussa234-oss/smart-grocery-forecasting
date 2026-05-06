import os
import subprocess
import time

def run_pipeline():
    print("\n🚀 STARTING MLOPS PIPELINE...\n")

    # Step 1: Generate actuals
    print("📊 Generating actuals...")
    subprocess.run(["python", "mlops/generate_actuals.py"])

    # Step 2: Monitor drift
    print("\n📈 Running drift monitoring...")
    result = subprocess.run(
        ["python", "mlops/monitor.py"],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    # Step 3: Check drift condition
    if "RETRAIN" in result.stdout or "🚨" in result.stdout:
        print("\n🚨 Drift detected → Starting retraining...\n")
        subprocess.run(["python", "mlops/retrain.py"])
        print("\n✅ Retraining completed")

    else:
        print("\n✅ No drift detected. System stable.")

if __name__ == "__main__":
    run_pipeline()