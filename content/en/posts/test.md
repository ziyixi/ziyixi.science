---
title: "Poetry for ML on Cluster"
date: 2022-04-28
draft: false
description: this post introduce the way I set up my ML study environment
tags: [icer, pytorch, gpu, poetry]
categories: machine-learning
---

## Motivation

My recent project uses the machine learning method to pick the seismic phase arrival time for the weak PS signal. If the phases can be successfully selected, we will have some big news to get many new detected PS arrivals. And further, we can establish a more robust slab interface model. Even if this work can only apply to Tonga, it's still meaningful. Well, this is the big picture and the motivation, so the problem is how to build the model?

I will put the details into my project description. And this post will simply talk about how I set up the python environment on the cluster. For MSU, it refers to ICER. But I suppose this workflow can apply to any other clusters. In practice, people usually use requirements.txt for ML projects. However, we all know it's not a good practice. Packages are updating, and there is always something being depreciated. It is tough to rerun a package written two years ago with simply a requirements.txt. So instead, some people prefer to use a conda environment with yml config files. It works, and it works well. But I wouldn't say I like it. A conda environment contains many packages that I don't need, and sometimes it's too heavy. Previously I have tried to build a docker image with the conda environment to serve my developed Earth model. Its size is too large for a docker image. There do have some ways to "shrink" a docker image. But after that, we lost the layer of information. So, in summary, I prefer some virtual environment managers with details dependency descriptions.

## A better package manager, Poetry

I am using Poetry, a python package manager that can replace pip. I have used it to build my Python program [PyFK](https://github.com/ziyixi/pyfk), which works well. By using Python's new pyproject.toml, it can replace setup.py. We are not making a package here, and all we need is just its environmental management system. For more details, you can read its [documentation](https://python-poetry.org/docs/). And below is my environment in my local mac, 

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

It contains all my required dependencies to run the code and several development dependencies. And I am also using poetry=1.2.0b1 as it supports lots of new features and fixes many bugs that I care about. It's stable enough for personal project development. As Mac doesn't support Nvidia GPU, I can only install the CPU version of Pytorch. The purpose of using a mac is just for development and prototype testing.

As you can see from the project configuration file, I have used PyTorch-lighting to develop the model, which supports parallel training and mixed precision. The most exciting part is that it supports bf16, which seems to be better than the original implementation with a larger floating range. This feature only supports GPUs after A100, and ICER has bought lots of them! No need to tolerate the floating overflow when using the mixed precision. However, it brings the difficulty of specifying the package dependency.

According to the document of Pytorch and Nvidia, to use A100, I have to use `CUDA=11.3` but not `CUDA=10.2`. The recommended way to install Pytorch with CUDA=11.3 is to use its official whl by `pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113`. For Poetry, it gets pretty tricky. Although Poetry supports the private Pypi repository, we can't directly use `https://download.pytorch.org/whl/cu113` as there are several locations this URL is forbidden to visit. Thus pip couldn't index it. Some people have maintained similar private repositories containing the downloadable wheels for Pytorch, and we can certainly use them instead. Alright, I have tested them, but now we have other problems.

Poetry is very slow to resolve the dependency when specifying different dependencies on different platforms. For example, if I change the above toml file to use  packages with cu113 on ICER, it will be:

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

Poetry seems to try several pretty silly pairings. Such as pair "torch+cu113" on Linux with "torchvision" on Darwin, and also all possible candidates for "torchaudio". So there are eight different combinations in total! I don't know why they pair the package with a clear marker "linux" with "darwin"! Even worse, they will also try to pair these 8 cases with all the possible candidates for NumPy. Maybe also Pandas? The waiting time is too long, so I must come up with a new idea.

## Seprate `pyproject.toml` for different platforms

So my current approach is to rename my first mentioned `pyproject.toml` file as `pyproject.mac.toml`, and make a soft link to `pyproject.toml` on my Mac. And also, I add `poetry.lock` to `.gitignore`. On ICER, I created a new configuration file named `pyproject.linux.toml` with the following content:


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

And On ICER, I also linked it to `pyproject.toml`. Everything works fine, and I just need to make soft links when migrating to new systems. I believe it's a common approach when people handle different `Makefiles` if they don't want their scripts to be filled with if and else.

Although Poetry's dependency resolving is difficult to use, I insist it's a good practice to detail the package version we have used in Python program development. It's indeed a historical problem that many Python packages have not specified clearly about their dependency, so resolving dependency for Poetry will be pretty tricky. However, I do admire the package developers from Poetry, and thanks for providing such a helpful tool!

