---
title: "Setting Up a Machine Learning Environment with Poetry on a Cluster"
date: 2022-04-28
draft: false
description: This post introduces the methods I utilized to establish my ML study environment.
tags: [icer, pytorch, gpu, poetry]
categories: machine-learning
---

## Introduction

Recently, I embarked on a project aimed at harnessing machine learning techniques to identify seismic phase arrival times for weak PS signals. The objective of this project is twofold: detection of new PS arrivals and the development of a robust slab interface model. While these methods are currently applied only to Tonga, the potential implications are substantial. This post provides an overview of the project's motivations and tackles the primary question: how do we construct the model?

While a detailed breakdown of the project will be provided separately, this post is dedicated to setting up the Python environment on a cluster, specifically ICER, for those at MSU. Conventional practice leans towards using `requirements.txt` for ML projects, but this isn't always optimal. Given that packages are continuously updated and certain functionalities depreciated, this could pose challenges when rerunning a package written a couple of years ago using only `requirements.txt`. As a workaround, some opt for a Conda environment with yml config files, but I found it bloated with unnecessary packages. Hence, I started exploring virtual environment managers that offer detailed dependency descriptions.

## Poetry: A Robust Package Manager

I settled on Poetry, a python package manager that serves as a worthy alternative to pip. I have utilized it to build my Python program [PyFK](https://github.com/ziyixi/pyfk) to good effect. By leveraging Python's new `pyproject.toml`, it can even replace `setup.py`. However, We are not creating a package here; all we need is its environmental management system. For more insights into its functionality, refer to the Poetry [documentation](https://python-poetry.org/docs/). My local environment on my Mac is structured as follows:

```toml
[tool.poetry]
name = "phasenet-pytorch"

[tool.poetry.dependencies]
python = "~3.9"
torch = {version="^1.11.0"}
torchvision = {version="^0.12.0"}
torchaudio = {version="^0.11.0"}

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

This configuration houses a simplified version of my dependencies for running the code, alongside several development dependencies. For this project, I am also using poetry=1.2.0b1, given its support for new features and bug fixes relevant to my needs. Although stable enough for personal project development, it's worth noting that Mac's lack of support for Nvidia GPU means I can only install the CPU version of Pytorch. Consequently, I employ Mac purely for development and prototype testing.

As evident from the project configuration file, PyTorch-lighting is employed to develop the model, facilitating parallel training and mixed precision. The highlight is its support for bf16, which, with its broader floating range, seems superior to the original implementation. This feature is exclusively compatible with GPUs after A100, of which ICER has procured plenty. Therefore, there's no need to endure floating overflow when using mixed precision. This, however, complicates the package dependency specification process.

According to Pytorch and Nvidia documentation, to leverage A100, `CUDA=11.3` is required as opposed to `CUDA=10.2`. The recommended method to install Pytorch with `CUDA=11.3` is by using its official whl via `pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113`. For Poetry, this gets tricky. Although Poetry supports private Pypi repositories, using https://download.pytorch.org/whl/cu113 directly isn't possible due to strange restrictions on certain subfolder paths without public access. As a result, pip can't index it. Alternatively, one can use private repositories maintained by some individuals that house downloadable Pytorch wheels. Despite this, other issues persist:

One of the problems with Poetry is the lengthy time it takes to resolve dependencies when specifying different dependencies on different platforms. For instance, modifying the above toml file to accommodate packages with `cu113` on ICER results in:

```toml
[tool.poetry]
name = "phasenet-pytorch"

[tool.poetry.dependencies]
python = "~3.9"
torch = [
    {url="https://download.pytorch.org/whl/cu113/torch-1.11.0%2Bcu113-cp39-cp39-linux_x86_64.whl",markers = "sys_platform == 'linux'"},
    {version="^1.11.0",markers = "sys_platform == 'darwin'"}]
torchvision = [
    {url="https://download.pytorch.org/whl/cu113/torchvision-0.12.0%2Bcu113-cp39-cp39-linux_x86_64.whl",markers = "sys_platform == 'linux'"},
    {version="^0.12.0",markers = "sys_platform == 'darwin'"}]
torchaudio = [
    {url="https://download.pytorch.org/whl/cu113/torchaudio-0.11.0%2Bcu113-cp39-cp39-linux_x86_64.whl",markers = "sys_platform == 'linux'"},
    {version="^0.11.0",markers = "sys_platform == 'darwin'"}]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

Poetry attempts to test pairing "torch+cu113" on Linux with "torchvision" on Darwin, and similarly for "torchaudio", resulting in eight different combinations in total! It's bewildering why they would pair a package marked "linux" with "darwin"! Worse still, they try to pair these eight cases with all potential candidates for NumPy and possibly Pandas. This prolongs the waiting time, necessitating an alternative solution.

## Seprate `pyproject.toml` for different platforms

My current solution involves renaming the initially mentioned `pyproject.toml` file to `pyproject.mac.toml`, and creating a soft link to `pyproject.toml` on my Mac. Furthermore, I added `poetry.lock` to `.gitignore`. On ICER, I created a new configuration file named `pyproject.linux.toml` with the following configuration:

```toml
[tool.poetry.dependencies]
[tool.poetry]
name = "phasenet-pytorch"

[tool.poetry.dependencies]
python = "~3.9"
torch = {url="https://download.pytorch.org/whl/cu113/torch-1.11.0%2Bcu113-cp39-cp39-linux_x86_64.whl"}
torchvision = {url="https://download.pytorch.org/whl/cu113/torchvision-0.12.0%2Bcu113-cp39-cp39-linux_x86_64.whl"}
torchaudio = {url="https://download.pytorch.org/whl/cu113/torchaudio-0.11.0%2Bcu113-cp39-cp39-linux_x86_64.whl"}

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

On ICER, I also linked it to `pyproject.toml`. This arrangement works flawlessly, and I simply need to make soft links when transitioning to new systems. This approach is commonly adopted when dealing with different Makefiles to avoid inundating scripts with if-else statements.

Even though Poetry's dependency resolution can be challenging, I remain convinced that specifying the package version used in Python program development is a sound practice. Many Python packages don't clearly specify their dependencies, which makes resolving dependencies for Poetry quite challenging. Nonetheless, I admire the Poetry package developers and am grateful for such a valuable tool!
