---
title: PhaseNet-TF
description: Spectrogram Seismograph Phase Picker with deep learning
image: images/researchprojects/phasenet-tf/tongaml.png
tags: [seismology, machine learning, semantic image segmentation]
---

_Note: content below is a preliminary introduction, and will be updated once the manuscript has been prepared_

{{< load-photoswipe >}}

# Introduction

Seismic phase picking is the process of determining phase arrival times from seismic records, typically in the form of seismograms. This task serves as the foundation for various other activities in seismology, including earthquake location, magnitude estimation, and seismic tomography. Traditionally, this task has been performed manually, a method that can be time-consuming and subjective.

In recent years, deep learning has shown promising results in phase picking. Previous works such as PhaseNet (Zhu et al., 2018) and EQTransformer (Mousavi et al., 2020) have demonstrated that deep learning methods can perform comparably or even superior to human experts. These studies have utilized time domain data, the default choice for seismologists. However, time domain data may not be suitable for situations involving complex noise.

In such cases, human experts tend to prefer picking phases in the spectrogram domain, which offers better noise robustness. Building on this premise, we propose a new deep learning model, PhaseNet-TF, based on spectrogram domain data. Our work reveals that PhaseNet-TF performs comparably to PhaseNet and EQTransformer and exhibits greater resistance to noise. To train and test our model, we utilized one year of data from the Tonga ocean bottom seismometer (OBS).

Training a phase picker is the initial step in building a seismic event catalog. Subsequent steps include Phase Association (grouping phase picks to specific earthquake events) and event relocation (locating the earthquake events). These steps also help eliminate a significant number of false picks. The refined phase picks, linked to the new catalog, can be further used to retrain the phase picker. This process is repeated until the phase picker performs adequately for the specific dataset, aligning with the general approach of semi-supervised learning.

{{< figure src="images/researchprojects/phasenettf/workflow.png" caption="The workflow diagram showing the semi-supervised learning.">}}

The model is available on [my GitHub](https://github.com/ziyixi/PhaseNet-TF). I am currently working on a paper on this subject and will update its status when ready.

# Data

We have approximately 60,000 10-minute OBS data sets from Tonga, covering north, east, and vertical components. Human experts have provided phase picks, indicating timestamps of phase arrivals. The data is then split into training, validation, and test sets. The training set contains 90% of the data, while the validation and test sets each contain 5%.

For the training dataset, we applied special data augmentation techniques to improve model robustness against noise, including random stacking, random noise, and random time shift. We then converted the data into the spectrogram domain and fed it to the model. The model is trained to predict phase picks from the spectrogram, factoring in the possibilities of different phase arrivals like P waves and S waves.

# Model

PhaseNet-TF's input is a spectrogram, with the output resembling a 1D possibility curve. Taking cues from PhaseNet, we view the phase picking problem as an image segmentation task. If we can differentiate meaningful signal blocks in the spectrogram from noise, it means we can identify phase arrival times.

Initially, we used U-Net (Ronneberger et al., 2015), a semantic image segmentation model widely used in the medical imaging field, as the backbone of the model. Although it worked, the performance did not meet our expectations. Subsequently, we tested several other models and found that DeepLabV3+ (Chen et al., 2018) yielded the best results. This model, also for semantic image segmentation, has a more powerful encoder and decoder. It employs a modified ResNet (He et al., 2016) with atrous convolution for encoding and a modified U-Net for decoding. We trained the model using the cross-entropy loss function, and optimization was achieved using the Adam optimizer.

{{< figure src="images/researchprojects/phasenettf/phasenet-tf_arch.png" caption="The PhaseNet-TF model.">}}

Below is an example of our model's prediction.

{{< figure src="images/researchprojects/phasenettf/examples_manual.png" caption="An example of the model's prediction.">}}

# Results

The following table presents key metrics for the performance of the entire workflow:
| | Precision (P wave) | Recall (P wave) | F1 (P wave) | Precision (S wave) | Recall (S wave) | F1 (S wave) | Precision (Events) | Recall (Events) | F1 (Events) |
|--------------------------------------|-------------------|----------------|-------------|-------------------|----------------|-------------|-------------------|----------------|-------------|
| Manual picks And PhaseNet-TF iteration 1 (Model prediction) | 97.97% | 98.35% | 98.16% | 96.77% | 98.85% | 97.80% | N/A | N/A | N/A |
| Manual picks And PhaseNet-TF iteration 1 (Association) | N/A (100%) | 95.80% | 97.85% | N/A (100%) | 86.53% | 92.78% | 94.61% | 96.56% | 95.57% |
| Manual picks And PhaseNet-TF iteration 1 (Relocation) | N/A (100%) | 94.58% | 97.21% | N/A (100%) | 85.62% | 92.26% | 95.25% | 94.84% | 95.05% |
| PhaseNet-TF iteration 2 (Model prediction) | 98.73% | 99.15% | 98.94% | 95.71% | 99.50% | 97.57% | N/A | N/A | N/A |
| PhaseNet-TF iteration 3 (Model prediction) | 98.35% | 98.14% | 98.24% | 95.75% | 99.07% | 97.38% | N/A | N/A | N/A |

The table is kind of complicated. The model prediction rows are all measured on the test dataset while trainning the PhaseNet-TF model. While association and relocation are directly measured from the results calculated from the manual picks without the PahseNet-TF prediction involvement. The phase based metrics (P and S wave) are used to measure if phases have been succesfully picked, while event based metrics are used to measure if events have been succesfully detected. For example, "Manual picks And PhaseNet-TF iteration 1 (Association)" means we use the associator to cluster the manual picks, and then measure the performance of the associator. After associating, we use the relocator to relocate the events based on the preliminary event clustering information provided by the associator, thus "Manual picks And PhaseNet-TF iteration 1 (Relocation)" will measure both the associator and relocator's performance.

These metrics require some context for a proper understanding. The following figure demonstrates the event detection results of the entire workflow.

{{< figure src="images/researchprojects/phasenettf/manuscript_horizontal_continious.png" caption="The horizontal cross-sections during the catalog development. Note here I have also shown a bootstrapping step, which means we use the bootstrap method to filter out events with the large standard deviation when using different sets of stations to do relocation.">}}

We also compared vertical cross-sections for the reference catalog (the one we used to train the PhaseNet-TF model), and the final catalog. We observed a significant increase in the number of events detected.

{{< gallery >}}
{{< figure src="images/researchprojects/phasenettf/manuscript_vertical_cross_section_1hour_reference.png" caption="Left: the reference catalog.">}}
{{< figure src="images/researchprojects/phasenettf/manuscript_vertical_cross_section_continious_semi.png" caption="Right: the final catalog.">}}
{{< /gallery >}}

# Training Curves

The model training was performed using 16 V100 GPUs hosted on the Expanse HPC platform. The first iteration of the semi-supervised learning took about 8 hours, with subsequent iterations gradually extending to 24 hours as more training data became available.

The following figures illustrate typical training and validation loss:

{{< gallery >}}
{{< figure src="images/researchprojects/phasenettf/loss_train.png" caption="Training loss">}}
{{< figure src="images/researchprojects/phasenettf/loss_val.png" caption="Validation loss">}}
{{< /gallery >}}

We employed early stopping to halt training when the validation loss failed to decrease for 10 epochs. The model was saved at the epoch with the lowest validation loss.
