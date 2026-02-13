# AI Multi-Modal Content Generator & Editor

A full-stack generative AI platform that allows users to create high-quality images, cinematic video clips, and stories from text prompts. The application features a dedicated ML pipeline, an automated prompt engineering assistant, and a built-in professional image editor.

## Key Features

* **AI Image Generation:** Generate images using Stable Diffusion with automatic seed consistency for recurring subjects.
* **Video Generation:** Text-to-video pipeline powered by Stable Video Diffusion (SVD) with optimized VRAM management.
* **AI Prompt Enhancer:** Integrated Gemini AI assistant to transform simple ideas into descriptive, high-quality art prompts.
* **Pro Photo Editor:** Built-in Fabric.js editor allowing for cropping, rotation, and real-time filters (Brightness, Contrast, Saturation, Blur).
* **Secure Auth:** Complete User Authentication system with JWT, Bcrypt password hashing, and MongoDB storage.
* **Smart Gallery:** Automated gallery that polls for content status (Pending/Completed/Failed) in real-time.

---

## Tech Stack

* **Frontend:** HTML5, CSS3, JavaScript (ES6+), Fabric.js.
* **Backend:** Node.js, Express.js, MongoDB (Mongoose), JWT.
* **Machine Learning:** Python 3.10+, PyTorch, Diffusers (Stable Diffusion & SVD).


---

## Installation & Setup

### 1. Clone the Repository

git clone [https://github.com/lakshmiaravind1234/MAJOR-PROJECT.git](https://github.com/lakshmiaravind1234/MAJOR-PROJECT.git)

cd MAJOR-PROJECT

### 2. Set Up Environment Variables
Create a .env file in the root directory and add:

MONGO_URI=your_mongodb_connection_string

JWT_SECRET=your_random_secret_key

PORT=3000


### 3. Install Node.js Dependencies

npm install

### 4. Python Environment Setup (venv)
The ML pipeline runs on Python. It is highly recommended to use a virtual environment to avoid package conflicts.

Create the Virtual Environment:

python -m venv venv_new

### 5.Activate the Environment:

* **Windows:**

PowerShell
.\venv_new\Scripts\activate

* **Linux/MacOS:**


source venv_new/bin/activate
Install Required Packages:
Once activated, install the core ML libraries:


pip install torch torchvision torchaudio --index-url [https://download.pytorch.org/whl/cu118](https://download.pytorch.org/whl/cu118)

pip install diffusers transformers accelerate safetensors Pillow

Note: If you have a requirements.txt file, you can install everything at once using:
pip install -r requirements.txt

### 6. Running the Application
Start the Backend:

node app.js
### 7. Access the App:
Open http://localhost:3000 in your browser.
