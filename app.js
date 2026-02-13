// app.js
const express = require("express");
const mongoose = require("mongoose");
const path = require("path");
const dotenv = require("dotenv");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const multer = require("multer");
const { spawn } = require("child_process"); // For running Python/FFmpeg processes
const fs = require("fs");
const cookieParser = require("cookie-parser");

mongoose.set('bufferCommands', false);

// Load environment variables
dotenv.config();

const { GoogleGenAI } = require('@google/genai');

const PYTHON_EXE_PATH = path.join(
  __dirname,
  "venv_new",
  "Scripts",
  "python.exe"
); // Path to your virtual environment's python.exe
const FFMPEG_NODE_PATH =
  "C:\\ffmpeg\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe"; // Correct absolute path to ffmpeg.exe

const app = express();
const PORT = process.env.PORT || 3000;

// --- Database Connection ---
const MONGO_URI = process.env.MONGO_URI;
mongoose
  .connect(MONGO_URI)
  .then(() => console.log("MongoDB Atlas Connected"))
  .catch((err) => console.error("MongoDB connection error:", err));

  
// --- Mongoose Models ---
const User = require("./models/User"); 
const GeneratedContent = require("./models/GeneratedContent");

const ai = new GoogleGenAI(process.env.GEMINI_API_KEY); 


// --- Middleware ---
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// Serve static files
app.use(express.static(path.join(__dirname, "public")));
app.use("/storage", express.static(path.join(__dirname, "storage")));

// --- Authentication Middleware for HTML pages ---
const requireAuth = (req, res, next) => {
  const token = req.cookies.token;

  if (!token) {
    return res.redirect("/login");
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded.user;
    next();
  } catch (err) {
    res.clearCookie("token");
    return res.redirect("/login");
  }
};

// Middleware for API routes that need user ID (returns 401, doesn't redirect HTML)
const authenticateAPI = (req, res, next) => {
  const token = req.cookies.token;
  if (!token) {
    req.user = null;
    return res
      .status(401)
      .json({ success: false, msg: "Unauthorized. No token provided." });
  }
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded.user;
    next();
  } catch (err) {
    res.clearCookie("token");
    return res
      .status(401)
      .json({ success: false, msg: "Unauthorized. Invalid token." });
  }
};

// --- Multer Setup for File Uploads ---
const uploadDir = path.join(__dirname, "public", "uploads");
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}
const upload = multer({
  dest: uploadDir,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
});

// --- NEW UTILITY AND DATA STRUCTURES FOR CONSISTENCY ---
const CONSISTENCY_TAGS = {
    styles: ["oil painting", "watercolor", "3D render", "cinematic photo", "hyperrealistic", "anime style", "pixel art"],
    artists: ["by Greg Rutkowski", "by Artgerm", "by Studio Ghibli", "by Katsuhiro Otomo"],
    lighting: ["cinematic lighting", "dramatic shadows", "volumetric lighting", "soft natural light", "neon glow"],
    camera: ["low angle shot", "high angle shot", "dutch angle", "bird's-eye view", "close-up portrait", "full body shot", "wide angle lens", "50mm prime lens"],
    quality: ["masterpiece", "highly detailed", "8k resolution", "sharp focus", "best quality", "trending on Artstation"],
    sliders: [
        "hyperrealistic", "8k resolution", "intricate detail", "cinematic quality",
        "highly detailed", "smooth finish", "sharp focus", "artistic sketch",
        "simple details", "muted colors", "dominant color hsl" // Color tag prefix
    ]
};

/**
 * Utility function to normalize the prompt and extract the core subject key.
 */
function normalizePrompt(prompt) {
    let normalized = prompt.toLowerCase().trim();

    const allTagsToRemove = [
        ...CONSISTENCY_TAGS.styles,
        ...CONSISTENCY_TAGS.artists,
        ...CONSISTENCY_TAGS.lighting,
        ...CONSISTENCY_TAGS.camera,
        ...CONSISTENCY_TAGS.quality,
        ...CONSISTENCY_TAGS.sliders
    ].map(tag => tag.toLowerCase());

    allTagsToRemove.forEach(tag => {
        const regex = new RegExp(`[,\\s]*${tag.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')}`, 'g');
        normalized = normalized.replace(regex, '');
    });

    normalized = normalized.replace(/dominant color hsl\([0-9\s,]+\%\)/g, '');
    
    normalized = normalized.replace(/,(\s*),/g, ','); 
    normalized = normalized.replace(/,\s*$/g, ''); 
    
    // let subject = normalized.split(',')[0].trim();
    let subject = normalized.split(',')[0].trim().replace(/\./g, '');
    
    if (subject.length === 0) {
        subject = prompt.substring(0, 50).trim();
    }

    return subject.substring(0, 100);
}
// --- END NEW UTILITY FUNCTIONS ---


// --- HTML Page Routes ---
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "views", "login.html"));
});

app.get("/app", requireAuth, (req, res) => {
  res.sendFile(path.join(__dirname, "views", "index.html"));
});

app.get("/login", (req, res) => {
  if (req.cookies.token) {
    try {
      jwt.verify(req.cookies.token, process.env.JWT_SECRET);
      return res.redirect("/app");
    } catch (err) {
      res.clearCookie("token");
    }
  }
  res.sendFile(path.join(__dirname, "views", "login.html"));
});

app.get("/register", (req, res) => {
  if (req.cookies.token) {
    try {
      jwt.verify(req.cookies.token, process.env.JWT_SECRET);
      return res.redirect("/app");
    } catch (err) {
      res.clearCookie("token");
    }
  }
  res.sendFile(path.join(__dirname, "views", "register.html"));
});

// Register User
// --- Add this line to the very top of your file to see if logs work at all ---
console.log("SERVER IS INITIALIZING...");

app.post("/api/register", async (req, res) => {
    console.log(">>> REGISTER REQUEST RECEIVED <<<"); // If you don't see this, the server isn't reading the request
    try {
        const { username, email, password } = req.body;
        console.log("Payload:", username, email);
        
        const newUser = new User({ username, email, password });
        await newUser.save();
        
        console.log("User saved!");
        res.json({ success: true });
    } catch (err) {
        console.error("CATCH ERROR:", err.message);
        res.status(500).json({ success: false, msg: err.message });
    }
});

// --- LOGIN USER ---
app.post("/api/login", async (req, res) => {
  const { email, password } = req.body;
  try {
    const user = await User.findOne({ email });
    if (!user) return res.status(400).json({ success: false, msg: "User not found" });

    // Using bcrypt directly is safer than user.matchPassword
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) return res.status(400).json({ success: false, msg: "Wrong password" });

    const token = jwt.sign({ user: { id: user._id } }, process.env.JWT_SECRET, { expiresIn: "1h" });
    res.cookie("token", token, { httpOnly: true });
    return res.status(200).json({ success: true, msg: "Login successful!" });
  } catch (err) {
    console.error("LOGIN CRASH:", err);
    return res.status(500).json({ success: false, msg: err.message });
  }
});

// Logout User
app.post("/api/logout", (req, res) => {
  res.clearCookie("token");
  res.status(200).json({ success: true, msg: "Logged out successfully" });
});



app.post("/api/generate/image", authenticateAPI, async (req, res) => {
    // We expect the prompt only; seed is managed automatically here.
    const { prompt } = req.body; 
    const userId = req.user.id;
    
    // Normalize the prompt to find the core subject key
    const coreSubjectKey = normalizePrompt(prompt); 

    if (!prompt || !coreSubjectKey) {
        return res.status(400).json({ success: false, msg: "Prompt is required and must contain a clear subject." });
    }

    // 1. Fetch the user's profile and check the promptSpecificSeeds map
    // We retrieve the 'promptSpecificSeeds' map from the database.
    const user = await User.findById(userId, 'promptSpecificSeeds'); 
    
    // Retrieve the remembered seed for this specific subject key
    const rememberedSeed = user.promptSpecificSeeds.get(coreSubjectKey) || null;

    // The seed to use for this generation (Use remembered seed or null/random)
    const seedToUse = rememberedSeed; 
    
    // 2. Create the pending content entry
    const newContent = new GeneratedContent({
        userId,
        type: "image",
        prompt,
        shortTitle: coreSubjectKey,
        filePath: "",
        status: "pending",
        seed: seedToUse, // Store the seed that was attempted (null if new)
    });
    await newContent.save();
    const contentId = newContent._id.toString();

    // 3. Send initial 202 response
    res.status(202).json({
        success: true,
        msg: `Generation started for '${coreSubjectKey}'. Consistency: ${seedToUse ? 'Locked' : 'Random'}.`,
        contentId: contentId,
        seed: seedToUse, // Return the seed being used
    });

    // 4. Start the asynchronous generation process
    const pythonArgs = [
        path.join(__dirname, "ml_scripts", "image_gen.py"),
        prompt,
        contentId,
        seedToUse || "random", // Pass the remembered seed or "random"
    ];

    const pythonProcess = spawn(PYTHON_EXE_PATH, pythonArgs);
    
    let outputResult = "";
    let errorOutput = "";

    pythonProcess.stdout.on('data', (data) => {
        outputResult += data.toString().trim();
    });
    pythonProcess.stderr.on('data', (data) => {
        errorOutput += data.toString();
    });


    // 5. Handle process completion (The Critical Step: Auto-Save Seed)
    pythonProcess.on('close', async (code) => {
        try {
            if (code === 0) {
                // ASSUMPTION: Python script returns data in the format "filepath:seed"
                const parts = outputResult.split(":");
                
                const finalSeed = parts.pop(); 
                const filePath = parts.join(":"); 
                
                if (filePath && finalSeed && finalSeed.trim() !== '') {
                    
                    // A. Update the GeneratedContent entry
                    await GeneratedContent.findByIdAndUpdate(contentId, {
                        status: "completed",
                        filePath: filePath,
                        seed: finalSeed, // The final seed used by the model
                        updatedAt: new Date(),
                    });

                    // B. AUTOMATICALLY SAVE: Update the User's Map
                    // Fetch the user document again to ensure we don't overwrite concurrent changes
                    const userToUpdate = await User.findById(userId, 'promptSpecificSeeds');

                    if (userToUpdate) {
                         // Set the new seed for the core subject key
                         userToUpdate.promptSpecificSeeds.set(coreSubjectKey, String(finalSeed));
                         await userToUpdate.save();
                         console.log(`Image generated for ${userId}. Subject '${coreSubjectKey}' seed saved: ${finalSeed}`);
                    }


                } else {
                    // Handle case where output format is unexpected or incomplete
                    await GeneratedContent.findByIdAndUpdate(newContent._id, {
                        status: "failed",
                        updatedAt: new Date(),
                    });
                    console.error(`Python script returned incomplete output format: ${outputResult}`);
                }
            } else {
                await GeneratedContent.findByIdAndUpdate(newContent._id, {
                    status: "failed",
                    updatedAt: new Date(),
                });
                console.error(`Image generation failed for ${userId}: Code ${code}, Error: ${errorOutput}`);
            }
        } catch (err) {
            console.error("Error updating content document or user profile after Python process:", err);
        }
    });

    pythonProcess.on("error", (err) => {
        console.error(`Failed to start Python process for image generation: ${err.message}`); 
        GeneratedContent.findByIdAndUpdate(newContent._id, {
            status: "failed",
            updatedAt: new Date(),
        }).catch((updateErr) => {
            console.error("Error updating document after process error:", updateErr);
        });
    });
});

// Video Generation from Text Prompt (Local CPU-bound Stable Diffusion)
app.post("/api/generate/video/text", authenticateAPI, async (req, res) => {
  const { prompt } = req.body;
  const userId = req.user.id;

  if (!prompt) {
    return res.status(400).json({ success: false, msg: "Prompt is required" });
  }

  const newContent = new GeneratedContent({
    userId,
    type: "video",
    prompt,
    filePath: "",
    status: "pending",
  });
  await newContent.save();
  const contentId = newContent._id.toString(); // Get ID for use in update

  res
    .status(202)
    .json({
      success: true,
      msg: "Video generation started. Check gallery soon.",
      contentId: contentId,
    });

  const pythonProcess = spawn(PYTHON_EXE_PATH, [
    path.join(__dirname, "ml_scripts", "svd_video_gen.py"),
    prompt,
    contentId, // Pass contentId
  ]);

  let outputResult = "";
  let errorOutput = "";

  pythonProcess.stdout.on("data", (data) => {
    outputResult += data.toString().trim();
  });
  pythonProcess.stderr.on("data", (data) => {
    errorOutput += data.toString();
  });

  pythonProcess.on("close", async (code) => {
    try {
      // ⭐ FIX 1: Use findByIdAndUpdate and robustly check output
      if (code === 0 && outputResult.trim()) {
        const finalFilePath = outputResult.trim();
        await GeneratedContent.findByIdAndUpdate(contentId, {
          filePath: finalFilePath,
          status: "completed",
          updatedAt: new Date(),
        });
        console.log(`Video generated for ${userId}: ${finalFilePath}`);
      } else {
        await GeneratedContent.findByIdAndUpdate(contentId, {
          status: "failed",
          updatedAt: new Date(),
        });
        console.error(
          `Video generation failed for ${userId}: Code ${code}, Error: ${
            errorOutput || 'No output received.'
          }`
        );
      }
    } catch (err) {
        console.error("Error updating video content document after process:", err);
    }
  });
  
  pythonProcess.on("error", (err) => {
    console.error(
      `Failed to start Python process for video generation: ${err.message}`
    );
    // ⭐ FIX 2: Ensure database is updated immediately on process launch error
    GeneratedContent.findByIdAndUpdate(contentId, {
        status: 'failed',
        updatedAt: new Date(),
    }).catch(updateErr => {
        console.error("Error updating video document after process error:", updateErr);
    });
  });
});


// Video Generation from File (Supports Image or PDF input)
app.post(
  "/api/generate/story",
  authenticateAPI,
  upload.single("sourceFile"),
  async (req, res) => {
    const userId = req.user.id;
    if (!req.file) {
      return res.status(400).json({ success: false, msg: "No file uploaded." });
    }
    const inputFile = req.file.path; // Path to the temporarily uploaded file by Multer

    const newContent = new GeneratedContent({
      userId,
      type: "video", // Set the type to 'video' for the gallery to display it correctly
      prompt: `Video story from file: ${req.file.originalname}`,
      filePath: "",
      status: "pending",
    });
    await newContent.save();
    const contentId = newContent._id.toString(); // Get ID for use in update


    res
      .status(202)
      .json({
        success: true,
        msg: "Story video generation started. Check gallery soon.",
        contentId: contentId,
      });

    // The key here is the 'outputResult' variable, which will buffer the stdout.
    let outputResult = "";
    let errorOutput = "";

    // Call the new Python script
    const pythonProcess = spawn(PYTHON_EXE_PATH, [
      path.join(__dirname, "ml_scripts", "story_to_video_gen.py"),
      inputFile,
      contentId, // Pass contentId
    ]);

    pythonProcess.stdout.on("data", (data) => {
      outputResult += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      errorOutput += data.toString();
      console.error(`Python stderr: ${data.toString()}`);
    });

    pythonProcess.on("close", async (code) => {
      fs.unlink(inputFile, (unlinkErr) => {
        if (unlinkErr)
          console.error("Error deleting temp upload file:", unlinkErr);
      });

      if (code === 0 && outputResult.trim()) {
        const filePath = outputResult.trim();
        await GeneratedContent.findByIdAndUpdate(contentId, {
          status: "completed",
          filePath: filePath,
          updatedAt: new Date(),
        });
        console.log(`Story video generated successfully: ${filePath}`);
      } else {
        await GeneratedContent.findByIdAndUpdate(contentId, {
          status: "failed",
          updatedAt: new Date(),
        });
        console.error(
          `Story video generation failed with code ${code}. Error: ${errorOutput}`
        );
      }
    });
     pythonProcess.on("error", (err) => {
        console.error(`Failed to start Python process for story generation: ${err.message}`);
        // Ensure database is updated immediately on process launch error
        GeneratedContent.findByIdAndUpdate(contentId, {
            status: 'failed',
            updatedAt: new Date(),
        }).catch(updateErr => {
            console.error("Error updating document after process error:", updateErr);
        });
    });
  }
);

app.post("/api/prompt/enhance", authenticateAPI, async (req, res) => {
    const { originalPrompt } = req.body;
    const userId = req.user.id; // User ID from authenticateAPI

    if (!originalPrompt) {
        return res.status(400).json({ success: false, msg: "Prompt is missing." });
    }
    
    // ⭐ Your Expert Prompt Engineering System Instruction
    const systemInstruction = `You are a world-class, creative AI art prompt engineer. Your goal is to take the user's simple prompt and transform it into a highly detailed, visually descriptive, and effective core narrative prompt for a photorealistic image generation model. You must add detail about the scene, mood, and subject (e.g., textures, environment). Do NOT include any instructions about camera angle, realism level, style, or color palette, as these will be added later by the user's controls. Your response MUST be only the refined prompt text, with no introductory or concluding sentences, and no markdown formatting.`;

    try {
        // ⭐ Actual API Call to Gemini
        const result = await ai.models.generateContent({
            model: 'gemini-2.5-flash', // Fast and effective for this task
            contents: [{ parts: [{ text: originalPrompt }] }],
            config: {
                systemInstruction: systemInstruction,
                temperature: 0.8, // Higher temperature for creativity
            }
        });

        const enhancedText = result.text.trim();

        if (enhancedText) {
            // 3. Send the successful JSON result back to the frontend
            return res.json({
                success: true,
                enhancedPrompt: enhancedText
            });
        } else {
            throw new Error("LLM returned an empty or unparsable response.");
        }

    } catch (error) {
        console.error("LLM Enhancement Processing Error:", error);
        // This is a safety catch for logic errors within the route itself
        // In a real setup, error.response.status or similar fields help debug
        return res.status(500).json({ success: false, msg: "Failed to communicate with the AI assistant. Check your API key and server logs." });
    }
});


app.get("/api/suggest", (req, res) => {
  // Return all categorized suggestions
  const categorizedSuggestions = {
    subjects: ["A bustling futuristic city", "A serene mountain landscape", "A whimsical creature", "A valiant knight", "A cozy study"],
    styles: ["oil painting", "watercolor", "3D render", "cinematic photo", "hyperrealistic", "anime style", "pixel art"],
    artists: ["by Greg Rutkowski", "by Artgerm", "by Studio Ghibli", "by Katsuhiro Otomo"],
    lighting: ["cinematic lighting", "dramatic shadows", "volumetric lighting", "soft natural light", "neon glow"],
    camera: ["low angle shot, powerful perspective", "high angle shot", "dutch angle", "bird's-eye view", "close-up portrait", "full body shot", "wide angle lens", "50mm prime lens"],
    quality: ["masterpiece", "highly detailed", "8k resolution", "sharp focus", "best quality", "trending on Artstation"],
  };
  res.json(categorizedSuggestions);
});

// --- API Route to Fetch Gallery Content ---
app.get("/api/gallery", authenticateAPI, async (req, res) => {
    const userId = req.user.id;

    try {
        // Find all content generated by the current user, sort by newest first
        const galleryItems = await GeneratedContent.find({ userId })
            .sort({ createdAt: -1 }) // Sort newest first
            .lean(); // Convert Mongoose documents to plain JavaScript objects

        res.json({
            success: true,
            gallery: galleryItems,
        });

    } catch (err) {
        console.error("Error fetching user gallery:", err);
        res.status(500).json({ success: false, msg: "Failed to retrieve gallery items." });
    }
});

// Start the server
app.listen(PORT, () =>
  console.log(`Server running on http://localhost:${PORT}`)
);



