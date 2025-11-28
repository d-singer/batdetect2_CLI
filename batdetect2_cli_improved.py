import os
import math
import argparse
from pathlib import Path
from multiprocessing import get_context, cpu_count
from batdetect2 import api
import pandas as pd
from tqdm import tqdm
from datetime import datetime

# === CENTRAL CONFIGURATION ===

DETECTION_THRESHOLD = 0.1
TIME_EXPANSION_FACTOR = 1
DEFAULT_BATCH_SIZE = 100
PROCESSES_TO_USE = max(1, cpu_count() - 1)
PRINT_PREFIX = "🦇"

# === WORKER INITIALIZER ===

def init_worker():
    """Preload BatDetect2 configuration once per worker."""
    global CONFIG
    CONFIG = api.get_config(
        detection_threshold=DETECTION_THRESHOLD,
        time_expansion_factor=TIME_EXPANSION_FACTOR
    )

# === CORE PROCESSING FUNCTIONS ===

def process_single_file(file_path: Path):
    """Process one audio file using BatDetect2."""
    try:
        result = api.process_file(str(file_path), config=CONFIG)
        detections = result["pred_dict"]["annotation"]
        if detections:
            df = pd.DataFrame(detections)
            df["filename"] = file_path.name
        else:
            df = pd.DataFrame([{
                "filename": file_path.name,
                "class": "no_calls_detected"
            }])
        return df
    except Exception as e:
        print(f"❌ Error processing {file_path.name}: {e}")
        return pd.DataFrame([{
            "filename": file_path.name,
            "class": f"error: {str(e)}"
        }])

def process_batch(batch_index, batch_files, pad_width, plot_id, output_dir):
    """Process one batch of audio files."""
    print(f"\n{PRINT_PREFIX}🚀 Processing batch {batch_index + 1} for plot {plot_id}")
    with get_context("spawn").Pool(processes=PROCESSES_TO_USE, initializer=init_worker) as pool:
        results = list(tqdm(
            pool.imap_unordered(process_single_file, batch_files),
            total=len(batch_files),
            desc=f"{plot_id} batch {batch_index + 1}",
            leave=False
        ))

    all_detections = pd.concat([df for df in results if not df.empty], ignore_index=True)
    output_path = output_dir / f"temp_batch_{batch_index + 1:0{pad_width}d}_{plot_id}.csv"

    # --- Standard save (no atomic rename) ---
    all_detections.to_csv(output_path, index=False)

    print(f"✅ Saved batch {batch_index + 1} → {output_path}")
    return output_path

def merge_batches(plot_id, output_dir):
    print(f"\n🔗 Merging all batches for {plot_id}")
    batch_files = sorted(output_dir.glob(f"temp_batch_*_{plot_id}.csv"))
    if not batch_files:
        print(f"⚠️ No batch files found for {plot_id}")
        return
    combined = pd.concat([pd.read_csv(f) for f in batch_files], ignore_index=True)
    merged_path = output_dir / f"batdetect2_{plot_id}.csv"
    combined.to_csv(merged_path, index=False)
    print(f"✅ Merged into {merged_path}")
    for f in batch_files:
        try:
            f.unlink()
        except Exception as e:
            print(f"⚠️ Could not delete {f.name}: {e}")

def get_previously_processed_files(plot_id, output_dir):
    """
    Gather all filenames that were already processed,
    normalizing to base names only (handles absolute/relative paths).
    """
    processed = set()
    merged_file = output_dir / f"batdetect2_{plot_id}.csv"

    def read_filenames(csv_path):
        try:
            df = pd.read_csv(csv_path, usecols=["filename"])
            return {Path(f).name for f in df["filename"].dropna().unique()}
        except Exception:
            return set()

    if merged_file.exists():
        processed.update(read_filenames(merged_file))

    for f in output_dir.glob(f"temp_batch_*_{plot_id}.csv"):
        processed.update(read_filenames(f))

    return processed

def process_plot_folder(subfolder_path, batch_size, output_dir):
    """Process all WAV files in a single plot subfolder."""
    plot_id = subfolder_path.name
    print(f"\n{PRINT_PREFIX}📁 Starting processing for plot: {plot_id}")

    all_wavs = sorted(subfolder_path.rglob("*.wav"), key=lambda x: x.name)
    if not all_wavs:
        print(f"⚠️ No .wav files in {plot_id}, skipping.")
        return

    previously_processed = get_previously_processed_files(plot_id, output_dir)
    wav_files = [f for f in all_wavs if f.name not in previously_processed]

    if not wav_files:
        print(f"✅ All files already processed for {plot_id}, skipping.")
        return

    print(f"➡️ {len(wav_files)} files to process "
          f"(skipping {len(previously_processed)} already processed)")

    # --- NEW: detect how many temp batches already exist ---
    existing_batches = list(output_dir.glob(f"temp_batch_*_{plot_id}.csv"))
    if existing_batches:
        # Extract the numeric part of the batch filenames
        existing_indices = []
        for f in existing_batches:
            try:
                num_str = f.name.split("_")[2]  # e.g. temp_batch_03_HE_WZ_23.csv → '03'
                existing_indices.append(int(num_str))
            except Exception:
                continue
        start_batch_index = max(existing_indices)  # continue numbering after last
    else:
        start_batch_index = 0

    num_new_batches = math.ceil(len(wav_files) / batch_size)
    pad_width = len(str(start_batch_index + num_new_batches))

    for i in tqdm(range(num_new_batches), desc=f"🔄 {plot_id} batches"):
        start = i * batch_size
        end = start + batch_size
        batch_files = wav_files[start:end]

        # increment batch numbering after existing batches
        process_batch(start_batch_index + i, batch_files, pad_width, plot_id, output_dir)

    merge_batches(plot_id, output_dir)


# === CLI ENTRY POINT ===

def main():
    parser = argparse.ArgumentParser(description="Batch process bat calls with BatDetect2.")
    parser.add_argument("--audio-root", type=str, required=True,
                        help="Path to the folder containing (subfolders of) WAV files.")
    parser.add_argument("--output-dir", type=str, default="02_BATDETECT2",
                        help="Output folder for batdetect2 results.")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE,
                        help="Number of audio files to process per batch.")
    args = parser.parse_args()

    audio_root = Path(args.audio_root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not audio_root.exists():
        raise FileNotFoundError(f"Audio root not found: {audio_root}")

    plot_folders = sorted({
        f.parent.resolve()
        for f in audio_root.rglob("*.wav")
    }, key=lambda p: str(p).lower())

    print(f"{PRINT_PREFIX}🔍 Found {len(plot_folders)} plot folders with audio")

    for subfolder in plot_folders:
        process_plot_folder(subfolder, args.batch_size, output_dir)

if __name__ == "__main__":
    main()
