import os
import time
import logging
import shutil
import subprocess
from pathlib import Path
import trimesh
from multiprocessing import Pool, cpu_count
from glb_checker.glb_validator import GLBMeshValidator
from glb_checker.utils import load_json, save_json
from pbr_extraction.texture_extractor import extract_pbr_textures
import objaverse


def setup_logging():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        handlers=[logging.FileHandler("glb_processing.log"), logging.StreamHandler()],
    )


def download_glb_file(args):
    """
    Downloads a GLB file from the Objaverse dataset and saves it to a specified directory.

    Args:
        args (tuple): A tuple containing three elements:
            - index (str): The index identifier for the GLB file.
            - objaverse_id (str): The Objaverse ID for the GLB file.
            - save_dir (str): The directory where the file should be saved.

    Returns:
        tuple: A tuple containing the following elements:
            - index (str): The index identifier for the GLB file.
            - objaverse_id (str): The Objaverse ID for the GLB file.
            - output_path (Path or None): The path to the downloaded file, or None if download failed.
            - success (bool): True if the download was successful, False otherwise.
            - error_message (str): An empty string if successful, or the error message if failed.
    """

    index, objaverse_id, save_dir = args
    output_dir = Path(save_dir) / index.replace("/", "_")
    output_path = output_dir / Path(objaverse_id).name
    url = f"https://huggingface.co/datasets/allenai/objaverse/resolve/main/glbs/{objaverse_id}"

    output_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["wget", "-q", "-c", url, "-O", str(output_path)],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return index, objaverse_id, output_path, True, ""
    else:
        shutil.rmtree(output_dir, ignore_errors=True)
        return index, objaverse_id, None, False, result.stderr


def validate_and_convert_glb(args):
    """
    Validates a GLB file and converts it to OBJ format.

    Args:
        args (tuple): A tuple containing four elements:
            - index (str): The index identifier for the GLB file.
            - objaverse_id (str): The Objaverse ID for the GLB file.
            - file_path (Path): The path to the GLB file to be processed.
            - save_dir (str): The directory where the processed file should be saved.

    Returns:
        tuple: A tuple containing the following elements:
            - index (str): The index identifier for the GLB file.
            - objaverse_id (str): The Objaverse ID for the GLB file.
            - success (bool): True if the file was successfully validated and converted, False otherwise.
            - error_message (str): An empty string if successful, or the error message if failed.
    """
    index, objaverse_id, file_path, save_dir = args
    output_dir = Path(save_dir) / index.replace("/", "_")
    if file_path and file_path.exists():
        validator = GLBMeshValidator(str(file_path))
        is_valid, reasons = validator.validate()

        if is_valid:
            logging.info(f"Valid GLB: {file_path}, exporting to OBJ...")

            # Extract PBR textures and save to JSON
            pbr_textures_info = extract_pbr_textures(file_path)
            save_json(f"{output_dir}/pbr_textures.json", pbr_textures_info)

            try:
                mesh = trimesh.load(file_path)
                output_obj_path = output_dir / (file_path.stem + ".obj")
                mesh.export(output_obj_path)
                return index, objaverse_id, True, ""
            except Exception as e:
                logging.error(f"Error converting {file_path} to OBJ: {e}")
                shutil.rmtree(output_dir)
                return index, objaverse_id, False, str(e)
        else:
            logging.warning(
                f"Invalid GLB: {file_path}, deleting folder... Reasons: {reasons}"
            )
            shutil.rmtree(output_dir)
            return index, objaverse_id, False, reasons
    return index, objaverse_id, False, "File does not exist"


def download_and_filter_models(num_models=100, save_dir="datasets"):
    """
    Downloads and filters models from the Objaverse dataset based on the availability of texture information.

    Args:
        num_models (int, optional): The number of models to download and filter. Defaults to 100.
        save_dir (str, optional): The directory where the downloaded and filtered models should be saved. Defaults to "datasets".

    Returns:
        dict: A dictionary where the keys are the UIDs of the downloaded models and the values are dictionaries containing the local paths of the downloaded files.
    """
    all_uids = objaverse.load_uids()  # Download all models
    selected_uids = all_uids

    annotations = objaverse.load_annotations(selected_uids)

    textured_uids = [
        uid
        for uid in selected_uids
        if any(
            archive.get("textureCount", 0) and archive["textureCount"] > 0
            for archive in annotations[uid]["archives"].values()
        )
    ]

    downloaded_objects = {}
    for uid in textured_uids:
        model_download_path = Path(save_dir) / uid
        model_download_path.mkdir(parents=True, exist_ok=True)

        logging.info(f"Downloading model {uid} to {model_download_path}...")
        downloaded_objects[uid] = objaverse.load_objects(
            uids=[uid],
            download_processes=os.cpu_count(),
        )

        for object_uid, local_path in downloaded_objects[uid].items():
            new_path = model_download_path / Path(local_path).name
            shutil.move(local_path, new_path)

    return downloaded_objects


def main():
    """
    Executes the GLB processing pipeline.

    This function sets up logging, creates necessary directories, loads JSON files, and processes GLB files
    by downloading, validating, and converting them. It handles GLB files from both the gobjaverse_index_to_objaverse.json
    and the Objaverse framework, and calculates the number of valid GLB files processed from each source. Finally, it logs
    the results including the count of valid GLB files and the elapsed time.

    Args:
        None

    Returns:
        None
    """

    setup_logging()
    logging.info("Starting the GLB processing pipeline...")

    save_dir = "datasets"
    os.makedirs(save_dir, exist_ok=True)

    non_monotonous_ids = list(load_json("non-monotonous_images_all.json"))
    index_to_objaverse = load_json("gobjaverse_index_to_objaverse.json")

    save_json("all_ids.json", non_monotonous_ids)  # Store all IDs

    start_time = time.time()

    download_args = [
        (index, objaverse_id, save_dir)
        for index, objaverse_id in index_to_objaverse.items()
        if index in non_monotonous_ids  # Process all models
    ]

    with Pool(processes=cpu_count()) as pool:
        download_results = pool.map(download_glb_file, download_args)

        valid_glb_files = [
            (index, objaverse_id, path, save_dir)
            for index, objaverse_id, path, success, _ in download_results
            if success
        ]

        validation_results = pool.map(validate_and_convert_glb, valid_glb_files)

        objaverse_models = download_and_filter_models(num_models=30, save_dir=save_dir)
        valid_objaverse_models = []
        for uid, local_path in objaverse_models.items():
            model_dir = Path(save_dir) / uid
            glb_path = list(model_dir.glob("*.glb"))[0]
            _, _, success, _ = validate_and_convert_glb((uid, uid, glb_path, save_dir))
            if success:
                valid_objaverse_models.append(uid)

    valid_gobjaverse_count = sum(
        1 for _, _, success, _ in validation_results if success
    )
    valid_objaverse_count = len(valid_objaverse_models)

    elapsed_time = int(time.time() - start_time)
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)

    logging.info(
        f"Download process completed. Valid GLBs from gobjaverse_index_to_objaverse.json: {valid_gobjaverse_count}"
    )
    logging.info(f"Valid GLBs from Objaverse framework: {valid_objaverse_count}")
    logging.info(f"Elapsed time: {hours:02d}h {minutes:02d}min {seconds:02d}s")


if __name__ == "__main__":
    main()
