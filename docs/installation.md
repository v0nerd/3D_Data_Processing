# Installation Instructions

Follow these steps to set up the **GLB Processing Pipeline**:

## **1. Clone the Repository**

Clone the repository to your local machine:

```bash
git clone https://github.com/v0nerd/3D_Data_Processing.git
cd 3D_Data_Processing
```

## **2. Set Up Virtual Environment**

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## **3. Install Dependencies**

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## **4. Download Objaverse Data**

Place the following JSON files in the `datasets/` directory:

- **`gobjaverse_index_to_objaverse.json`**
- **`non-monotonous_images_all.json`**
- **`all_ids.json`**

## **5. Run the Pipeline**

Execute the main script to start processing:

```bash
python src/main.py
```

## **6. Run Tests (Optional)**

To verify the setup, run the tests:

```bash
python -m unittest discover tests
```
