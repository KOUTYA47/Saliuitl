# Saliuitl Docker Environment
# PyTorch 2.5.1 + CUDA 11.8 for RTX 3060 Ti

FROM pytorch/pytorch:2.5.1-cuda11.8-cudnn9-runtime

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies (excluding torch as it's in base image)
RUN pip install --no-cache-dir \
    scikit-image==0.24.0 \
    scikit-learn==1.6.1 \
    scipy==1.13.1 \
    matplotlib==3.9.4 \
    tqdm==4.67.1 \
    pillow==11.0.0 \
    imageio==2.37.0

# Copy project files
COPY . .

# Verify CUDA availability
RUN python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA:', torch.cuda.is_available())"

# Default command
CMD ["bash"]
