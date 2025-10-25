# EchoMark

## Authors

|                   |                                                                                                                     |
|-------------------|---------------------------------------------------------------------------------------------------------------------|
| Cezary Dymicki    | [![GitHub](https://img.shields.io/badge/GitHub-Cezym-181717?logo=github)](https://github.com/Cezym)                 |
| Szymon Jankowski  | [![GitHub](https://img.shields.io/badge/GitHub-szymonjank111-181717?logo=github)](https://github.com/szymonjank111) |
| Ireneusz Okniński | [![GitHub](https://img.shields.io/badge/GitHub-AndFirst-181717?logo=github)](https://github.com/AndFirst)           |

<style>
    th {
        display: none;
    }
</style>

## Inspiration

In the article [Tralie et al., 2024](https://doi.org/10.48550/arXiv.2412.10649) it was shown that generative models can
preserve echoes added to an audio track.
This phenomenon can be used to mark audio works and verify whether they have been illegally used by creators of
generative models.

Our goal was to develop an application that allows users to embed a watermark into an audio track and later decode it
from the modified recording.
By comparing the extracted signature with the original watermark, it becomes possible to identify audio pieces marked
with a specific watermark.

In addition to developing the application, several experiments were conducted:

1. Experiment 1
2. Experiment 2

## What is it?

**EchoMark** is an application designed for audio watermarking using the technique of **hidden echoes**.  
Its main goal is to enable the embedding of watermarks in audio recordings in a way that is **imperceptible to the human
ear**, while ensuring **reliable detection**.

The project focuses on the **time spread echo** method, which, by distributing echoes over time, allows for hiding a
greater amount of information while preserving the audio quality.

### Simple echo

This technique

### Time spread echo

## Usage

Project has two main goals: app and experiments. You can run app in which you can embed watermark in your vaw file or
run script to reproduce our experiments.

### App

    make app

### Experiments

    TODO

## Our experiments

## Bibliography

1. Christopher J. Tralie, Matt Amery, Benjamin Douglas, Ian Utz (2024). *Hidden Echoes Survive Training in Audio To
   Audio Generative Instrument Models.* arXiv:
   2412.10649. [https://doi.org/10.48550/arXiv.2412.10649](https://doi.org/10.48550/arXiv.2412.10649), [https://www.ctralie.com/echoes/](https://www.ctralie.com/echoes/)
2. Djebbar, F., Ayad, B., Meraim, K.A. et al. (2012). *Comparative study of digital audio steganography techniques.* J
   AUDIO SPEECH MUSIC PROC. 2012,
    25. [https://doi.org/10.1186/1687-4722-2012-25](https://doi.org/10.1186/1687-4722-2012-25)
3. Mohammad Shorif Uddin, Ohidujjaman, Mahmudul Hasan, Tetsuya Shimamura (2024). *Audio Watermarking: A Comprehensive
   Review.* [https://dx.doi.org/10.14569/IJACSA.2024.01505141](https://dx.doi.org/10.14569/IJACSA.2024.01505141)
