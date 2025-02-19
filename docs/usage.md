# Usage Instructions

## **Overview**

This pipeline processes GLB files from the Objaverse dataset by downloading, validating, extracting PBR textures, and converting to OBJ format.

## **Running the Pipeline**

1. Ensure that **`gobjaverse_index_to_objaverse.json`**, **`non-monotonous_images_all.json`**, and **`all_ids.json`** are in the `datasets/` directory.
2. Run the pipeline:

   ```bash
   python src/main.py
   ```

This will download and process the models, extracting textures and converting valid GLBs to OBJ format.

## **Logs**

Pipeline logs are saved in **`glb_processing.log`** for monitoring progress.

## **Testing**

To run tests:

```bash
python -m unittest discover tests
```

Test files include validation checks for GLB files, texture extraction, and the main pipeline.
