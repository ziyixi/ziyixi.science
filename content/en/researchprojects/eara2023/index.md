---
title: "Introducing EARA2023: A 3-D Seismic Model"
description: "The East Asia Radially Anisotropic Model 2023 (EARA2023) – Pioneering Insights into Seismic Imaging"
tags: [seismology, full waveform inversion]
---

{{< load-photoswipe >}}

I'm excited to unveil the East Asia Radially Anisotropic Model 2023 (EARA2023), a state-of-the-art three-dimensional wave speed model. This cutting-edge development provides a comprehensive seismic view of the crust and upper mantle beneath Eurasia, particularly the Western Pacific subduction zone. It capitalizes on Full Waveform Inversion (FWI) to reveal detailed seismic structures. Below, you can observe a comparison between the initial iteration and the final iteration of the model.
{{< gallery >}}
{{< figure src="images/researchprojects/eara2023/eara2023-m01.png" caption="Left: the model at the first iteration. The horizontal cross-section is located at 500 km depth.">}}
{{< figure src="images/researchprojects/eara2023/eara2023-m30.png" caption="Right: the model at the 30 iteration. The horizontal cross-section is located at 500 km depth.">}}
{{< /gallery >}}

Furthermore, I've created an intriguing animation that displays the changes in the model over time:
{{< figure src="images/researchprojects/eara2023/model_animation.gif" >}}

To construct EARA2023, I iteratively minimized the waveform similarity misfit between synthetic and observed waveforms. The model used data from approximately 2,000 broadband stations across Eurasia, with a primary focus on East Asia. These stations recorded 142 earthquakes.
{{< figure src="images/researchprojects/eara2023/eara2023-data.png" >}}

My findings enhance our understanding of seismic structures when compared with previous research. After 20 iterations, EARA2023 provides enhanced images of large-scale subducted oceanic plate morphology in the upper mantle, the transition zone, and the uppermost of the lower mantle. The model captures the trenches of Kuril, Japan, Izu-Bonin, and Ryukyu in high resolution, presenting wave speed anomalies reaching a maximum of 8% for $V_p$ and 13% for $V_s$. Low wave speed anomalies, primarily in the asthenosphere and particularly within mantle wedges and backarc basins, suggest the presence of melt, possibly due to high-temperature anomalies or the addition of volatiles. These are characterized by a maximum of 6% wave speed reduction for both $V_p$ and $V_s$.

Here are examples of the imaged slabs in detail:
{{< figure src="images/researchprojects/eara2023/eara2023-slab.png" >}}

Moreover, EARA2023 offers fresh insights into the origins of the intraplate volcanoes in East Asia. For instance, the model reveals several 'holes' beneath the Changbaishan volcano. This observation could potentially offer new understanding of the volcanic activity in this region.
{{< figure src="images/researchprojects/eara2023/eara2023-changbaishan.png" caption="Model comparison beneath the Changbaishan volcano with different models.">}}

In conclusion, a dynamic visual representation of our model is available, which my advisor and I have transformed into a 'real 3D' view using Paraview. You can view this below:
{{< vimeo id="839844594" title="Our 3D seismic model visualization" >}}
