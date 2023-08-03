---
title: PyFK
description: Python port of FK with Cython, GPU, and MPI acceleration
tags: [seismology, parallel computing]
---

{{< load-photoswipe >}}

_Note: content below is modified from my AGU 2021 poster, and will be updated once the manuscript has been prepared_

## Introduction

The frequency-wavenumber (FK) package (Zhu & Rivera, 2002) has been widely used in calculating synthetic seismograms. It can provide numerical solutions for a one-dimension layered seismic model. The current serial version of the FK package has the advantages of accuracy and accessibility. However, the simulation speed slows down for either relatively large epicenter distances or higher frequencies. It becomes more challenging for multiple events and a large number of models. Here we develop a parallel-computing version of the FK package using Message Passing Interface (MPI) and Compute Unified Device Architecture (CUDA). Users can choose either to run the program on multiple CPUs using MPI or GPU using CUDA.

Our benchmark results show that the MPI version is optimal for using a small number of CPUs, which leads to almost a linear speedup ratio. But the acceleration is not significant when using more than 30 CPUs, because of the overhead restriction of the process communication. On the other hand, the CUDA version shows a noticeable speedup on a single GPU. Furthermore, we use Cython, a superset of the Python programming language designed to give C-like performance, to rewrite the core code of FK to accelerate the calculation further. Within the Python framework, PyFk flexibly supports visualization and post-procession of the results using Obspy and other common seismic tools.

## The frequency-wavenumber method

Historically, Haskell (1963, 1964) and Harkrider (1964) use the propagator matrix technique, which study the matrix formalism of wave propagation in a multi-layered medium, to derive the solution of the surface displacement due to a point source. Zhu and Rivera (2002) redefine the propagator matrix and find the static solution can be a special case of the dynamic solution. In the meantime, Prof. Zhu wrote the package FK to calculate the 1D layered model synthetics, which is then widely used by the community of the seismology.

By setting up a cylindrical coordinate system, the displacement in a vertically heterogeneous medium can be expanded in terms of three orthogonal vectors (Takeuchi and Saito 1972):
$\mathbf{u}(r, \theta, z, t)=\frac{1}{2 \pi} \sum_{m=0, \pm 1, \ldots} \int \mathrm{e}^{-\mathrm{i} \omega t} d \omega \int_0^{\infty} k d k\left(U_z \mathbf{R}\_m^k+U_r \mathbf{S}\_m^k+U_\theta \mathbf{T}\_m^k\right)$

Here the integration of $\omega$ is an inverse Fourier transform, the integration of the wavenumber k must be done numerically. R, S and T are Bessel functions, while $U_z$, $U_r$, and $U_\theta$ can be solved by the propagator matrix technique (Zhu & Rivera, 2002).

PyFK focus on paralling the numerical integration of the wavenumber k. The kernel part can be implented by either Cython or CUDA kernels.

{{< figure src="images/researchprojects/pyfk/pyfk_usage.png" caption="An example to run PyFK v3.0">}}

## Weak and strong scaling

{{< figure src="images/researchprojects/pyfk/pyfk_strong.jpg" caption="Strong scaling test for the MPI mode: Strong scaling measures the performance with more processes. The result shows the optimized number of processes to utilize is around 50.">}}
{{< figure src="images/researchprojects/pyfk/pyfk_weak.jpg" caption="Weak scaling test for the MPI mode: Linear scaling is achieved if the run time stays constant while the workload is increased. It can imply no bottlenecks such as the memory IO.">}}
{{< figure src="images/researchprojects/pyfk/pyfk_gpu.jpg" caption="The GPU speed up ratio for the tested devices can attain ~40 times comparing with FK, ~100 times comparing with PyFK.">}}

## Marsquake simulation

PyFK is also able to simulate the "quakes" in other planets such as Marsquake or Moonquake. The following figure shows the synthetic seismograms of a Marsquake event:
{{< figure src="images/researchprojects/pyfk/pyfk_marsquake.jpg" caption="The waveform simulation for an Marsquake. Scientists already know more about the Aug. 25 quakes: The magnitude 4.2 event occurred about 5,280 miles (8,500 kilometers) from InSight – the most distant temblor the lander has detected so far. (cited from https://www.jpl.nasa.gov/news/nasas-insight-finds-three-big-marsquakes-thanks-to-solar-panel-dusting). The Mars model is cited from Stähler et al. (2021).">}}

## Aknowledgement

This work is supported by NSF grant 1802247. We thank the High-Performance Computing Center (HPCC) at Michigan State University, the Extreme Science and Engineering Discovery Environment (XSEDE supported by NSF grant ACI-1053575).
