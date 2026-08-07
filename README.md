# 🎨 Echoverse — AI Multi-Model Content Generator & Editor

**Echoverse** is a full-stack Generative AI platform that transforms text prompts into **AI-generated images, cinematic video clips, and stories**.

The platform combines **Generative AI, diffusion models, automated prompt enhancement, and a professional image editor** into a single application.

---

## ✨ Key Features

### 🖼️ AI Image Generation

* Generate high-quality images using **Stable Diffusion**.
* Support for seed consistency to maintain recurring subjects across generations.

### 🎬 Video Generation

* Generate cinematic video clips using **Stable Video Diffusion (SVD)**.
* Includes optimized VRAM management for the ML pipeline.

### 🧠 AI Prompt Enhancement

* Uses **Google Gemini AI** to transform simple ideas into detailed and descriptive prompts.
* Helps users create better prompts for image generation.

### 🎨 Professional Image Editor

* Built-in **Fabric.js** image editor.# 🎨 Echoverse — AI Multi-Model Content Generator & Editor

**Echoverse** is a full-stack Generative AI platform that transforms text prompts into **AI-generated images, cinematic video clips, and stories**.

The platform combines **Generative AI, diffusion models, automated prompt enhancement, and a professional image editor** into a single application.

---

## ✨ Key Features

### 🖼️ AI Image Generation

* Generate high-quality images using **Stable Diffusion**.
* Support for seed consistency to maintain recurring subjects across generations.

### 🎬 Video Generation

* Generate cinematic video clips using **Stable Video Diffusion (SVD)**.
* Includes optimized VRAM management for the ML pipeline.

### 🧠 AI Prompt Enhancement

* Uses **Google Gemini AI** to transform simple ideas into detailed and descriptive prompts.
* Helps users create better prompts for image generation.

### 🎨 Professional Image Editor

* Built-in **Fabric.js** image editor.
* Supports:

  * Cropping
  * Rotation
  * Brightness
  * Contrast
  * Saturation
  * Blur
  * Real-time editing

### 🔐 Secure Authentication

* User authentication using **JWT**.
* Password hashing using **Bcrypt**.
* User and content data stored in **MongoDB**.

### 🖼️ Smart Gallery

* Automatically tracks generated content.
* Displays generation status such as:

  * Pending
  * Completed
  * Failed

---

## 🏗️ Application Architecture

Echoverse combines a web application layer with a dedicated Python-based machine learning pipeline.

```text
                    ┌─────────────────────┐
                    │       User          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Web Application   │
                    │ HTML / CSS / JS     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Node.js + Express │
                    │      Backend        │
                    └──────┬───────┬──────┘
                           │       │
                ┌──────────┘       └──────────┐
                ▼                             ▼
       ┌────────────────┐             ┌──────────────┐
       │    MongoDB     │             │ Gemini AI    │
       │ User & Content │             │Prompt Enhance│
       └────────────────┘             └──────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Python ML       │
                  │ Pipeline        │
                  └────────┬────────┘
                           │
                  ┌────────┴────────┐
                  ▼                 ▼
          ┌───────────────┐  ┌──────────────────┐
          │Stable Diffusion│  │Stable Video     │
          │ Image Generation│ │Diffusion (SVD) │
          └───────────────┘  └──────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend

* HTML5
* CSS3
* JavaScript (ES6+)
* Fabric.js

### Backend

* Node.js
* Express.js
* MongoDB
* Mongoose
* JWT

### Machine Learning & Generative AI

* Python 3.10+
* PyTorch
* Hugging Face Diffusers
* Stable Diffusion
* Stable Video Diffusion
* Google Gemini AI

---

## 📂 Project Structure

```text
Echoverse/
│
├── ml_scripts/          # Python-based ML generation scripts
├── models/              # Model-related components
├── views/               # Application views
│
├── app.js               # Node.js / Express application
├── package.json         # Node.js dependencies
├── package-lock.json    # Dependency lock file
├── README.md            # Project documentation
└── .gitignore           # Ignored files and folders
```

> The project structure may evolve as additional modules and features are added.

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/lakshmiaravind1234/Echoverse.git
cd Echoverse
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
MONGO_URI=your_mongodb_connection_string
JWT_SECRET=your_random_secret_key
PORT=3000
```

> **Never commit your `.env` file or expose API keys, database credentials, or other secrets on GitHub.**

### 3. Install Node.js Dependencies

```bash
npm install
```

### 4. Create a Python Virtual Environment

The machine learning pipeline uses Python.

```bash
python -m venv venv_new
```

#### Windows

```powershell
.\venv_new\Scripts\activate
```

#### Linux / macOS

```bash
source venv_new/bin/activate
```

### 5. Install Python Dependencies

For a CUDA 11.8 environment:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

Then install the core ML libraries:

```bash
pip install diffusers transformers accelerate safetensors Pillow
```

If the project contains a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 6. Start the Application

```bash
node app.js
```

### 7. Open the Application

Open the following address in your browser:

```text
http://localhost:3000
```

---

## 📸 Screenshots

Screenshots of the application will be added here to demonstrate:

* Image generation
* AI prompt enhancement
* Video generation
* Image editor
* Smart gallery
* User authentication

---

## 🔮 Future Enhancements

Potential future improvements include:

* Additional generative AI models
* Improved video generation capabilities
* More advanced image editing tools
* Enhanced generation history and gallery management
* Cloud-based deployment
* Performance optimization for ML inference

---

## 👨‍💻 Author

**Lakshmi Aravind Reddy**

Aspiring **Data Analyst & Data Scientist** with an interest in **Generative AI, Machine Learning, Data Analytics, and AI-powered applications**.

---

⭐ If you find this project interesting, consider giving the repository a star!

