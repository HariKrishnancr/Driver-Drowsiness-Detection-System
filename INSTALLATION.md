# Installation Guide for Drowsiness Detection

## Prerequisites

Before running the drowsiness detection program, you need to install the required Python packages. The main challenge is installing `dlib` on Windows, which requires C++ build tools.

## Method 1: Install Pre-compiled dlib (Recommended for Windows)

### Option A: Using pip with pre-compiled wheel
```bash
# Download the appropriate dlib wheel file for your system from:
# https://pypi.org/project/dlib/#files
# Then install it directly:
pip install path/to/downloaded/dlib-wheel-file.whl
```

### Option B: Using conda (if you have Anaconda/Miniconda)
```bash
conda install -c conda-forge dlib
```

## Method 2: Install Build Tools for Compiling dlib

If you want to compile dlib from source:

1. Install Visual Studio Build Tools or Visual Studio Community
2. Make sure CMake is installed and in your PATH
3. Run: `pip install dlib`

## Complete Installation Steps

1. Install the required packages:
```bash
pip install opencv-python imutils scipy
```

2. Install dlib using one of the methods above:
```bash
pip install dlib
```

3. Run the program:
```bash
python Drowsiness_Detection.py
```

## Alternative: Running Without dlib

If you cannot install dlib, the program will fall back to using OpenCV's Haar cascade for face and eye detection. While this won't provide the full eye aspect ratio calculations, it will still detect faces and eyes.

## Troubleshooting

### If you get "Microsoft Visual C++ 14.0 is required":
- Install Microsoft C++ Build Tools
- Or use the pre-compiled wheel method

### If you get CMake errors:
- Install CMake from https://cmake.org/download/
- Make sure it's added to your system PATH

### If you're on Windows and having persistent issues:
Consider using Anaconda/Miniconda, which makes installing dlib much easier:
```bash
conda install -c conda-forge dlib opencv imutils scipy
```