# GLB Processing Pipeline

## Overview

This project provides a **GLB (GL Transmission Format) processing pipeline** that:

- **Downloads** GLB models from Objaverse.
- **Validates** and **converts** GLB models to OBJ format.
- **Extracts** PBR (Physically Based Rendering) textures from GLB files.
- **Filters** and processes models based on metadata.

It utilizes **multiprocessing** for efficient batch processing of GLB files.

## Features

- **GLB File Validation**: Ensures GLB files meet predefined quality standards.
- **Texture Extraction**: Extracts PBR textures from GLB files.
- **GLB to OBJ Conversion**: Converts GLB models to the OBJ format.
- **Batch Processing**: Uses parallel execution for faster processing.

---

## Installation

### Prerequisites

Ensure you have the following installed:

- Python **3.8+**
- Required dependencies (see `requirements.txt`)
- `wget` (for downloading files)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/v0nerd/3D_Data_Processing.git
   cd 3D_Data_Processing
   ```

2. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Running the Pipeline

To run the GLB processing pipeline, execute:

```bash
python main.py
```

This will:

- Select a random sample of GLB models.
- Download models from Objaverse.
- Validate and convert models.
- Extract PBR texture data.

### Project Structure

```
│── glb_checker/
│   ├── __init__.py
│   ├── glb_validator.py  # Validates GLB files
│   ├── utils.py          # JSON utilities
│
│── pbr_extraction/
│   ├── __init__.py
│   ├── texture_extractor.py  # Extracts PBR textures from GLB files
│
│── main.py               # Main script to run the pipeline
│── gobjaverse_index_to_objaverse.json  # Mapping for dataset processing
│── non-monotonous_images_all.json  # Non-monotonous dataset metadata
│── requirements.txt      # Required dependencies
```

### Key Functionalities

#### **1. Downloading GLB Files**

The script downloads GLB files from Objaverse and saves them in the `datasets/` directory.

#### **2. GLB Validation**

Validation is performed using `glb_checker/glb_validator.py`, which:

- Checks **mesh quality** (e.g., face count, degenerate faces, normals).
- Detects **self-intersections** in meshes.
- Ensures models are suitable for conversion.

#### **3. GLB to OBJ Conversion**

Valid GLB models are converted to the OBJ format using `trimesh`.

#### **4. Extracting PBR Textures**

`pbr_extraction/texture_extractor.py` extracts PBR material data such as:

- Base color textures
- Metallic and roughness textures
- Normal maps

### Logging

All logs are stored in `glb_processing.log`.

---

## License

This project is **open-source**. Modify and distribute as needed.
