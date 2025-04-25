📸 Best Shot Finder
A lightweight, AI-powered tool to evaluate and rank photos based on multiple image quality metrics. Run it locally or deploy it as a Streamlit web app to easily compare photos and find the best shot.
✨ Features

Image Quality Metrics (normalized to 0–100):
Sharpness: Edge clarity using the Laplacian method.
Noise: Image grain (lower is better, inverted score).
Brightness: Overall light level via HSV analysis.
Contrast: Difference between dark and light areas.
Saturation: Color vividness using LAB color space.
Composition: Adherence to the rule of thirds via edge detection.
Composite Score: Weighted sum of all metrics, customizable via sliders.


Flexible Upload: Upload up to 10 individual images (JPG/PNG) or a ZIP file containing multiple images.
EXIF Metadata: Displays camera settings like exposure time, ISO, aperture, and focal length.
Export Options:
Download metrics as a CSV file.
Export top-ranked images as a ZIP file.


Streamlit Frontend: Intuitive UI with progress bars, expandable results, and customizable sorting by any metric.
High-Quality Processing: Images are saved with minimal compression (JPEG quality=95, PNG lossless) for sharp previews.

🚀 Getting Started
Prerequisites

Python 3.9 or 3.10
Git (for cloning and deploying)
A GitHub account (for Streamlit Community Cloud deployment)

Installation

Clone the repository:git clone https://github.com/your-username/best-shot-finder.git
cd best-shot-finder


Create and activate a virtual environment:python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:pip install -r requirements.txt



Local Usage

Run the Streamlit app:streamlit run app.py


Open your browser at http://localhost:8501.
Upload images or a ZIP file, adjust weights for the composite score, and explore the results.

Deploy to Streamlit Community Cloud

Push your repository to GitHub:git add app.py analyzer.py requirements.txt
git commit -m "Update Best Shot Finder"
git push origin main


Go to share.streamlit.io and sign in with GitHub.
Click New app and configure:
Repository: your-username/best-shot-finder
Branch: main
Main file path: app.py
App URL: Choose a unique name (e.g., best-shot-finder-yourname)
Python version: 3.9 or 3.10


Click Deploy and wait 2–5 minutes. Access your app at the provided URL.

📋 Requirements
The requirements.txt includes:
streamlit>=1.10.0
pillow
pandas
opencv-python
numpy
scikit-image

🛠️ How It Works

Upload: Add up to 10 images (JPG/PNG) individually or as a ZIP file.
Analysis: Each image is evaluated for sharpness, noise, brightness, contrast, saturation, and composition (metrics normalized to 0–100).
Ranking: Sort images by any metric or a weighted composite score.
Results: View top-ranked images, detailed metrics, and EXIF metadata in an expandable section.
Export: Download metrics as CSV or top images as ZIP.

📷 Example

Upload three photos (e.g., photo1.jpg, photo2.jpg, photo3.jpg).
Adjust weights for the composite score (e.g., prioritize sharpness).
Click Calculate Composite Score to rank images.
View the top 3 shots, expand results for metrics and EXIF data, and download results.

🙌 Contributing
Feel free to open issues or submit pull requests on GitHub. Suggestions for new metrics or features are welcome!
📜 License
This project is licensed under the MIT License.
👨‍💻 Author
Created by Silvio Thomi, 2025

🌟 Try it out and find your best shot!
