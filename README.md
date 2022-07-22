![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) 
![PyQt](https://img.shields.io/badge/-PyQt-yellowgreen?style=for-the-badge) 
![McsPyDataTools](https://img.shields.io/badge/-McsPyDataTools-green?style=for-the-badge) 


[![screenshot.png](https://i.postimg.cc/59nZNmh8/screenshot.png)](https://i.postimg.cc/59nZNmh8)

## **Overview**
NeuroSpace is an application where you can observe the brain signals, make analysis, filtering, visualization and everything related to neural signal processing.
During neuro research there were custom ideas which was not supported by the existing neuro analyzer apps, 
we made an app which takes neuro signal files, processes them, filters based on the requirements, calculates and detects both spikes and bursts too. and also the fantastic visualizarions are provided !


## **Why NeuroSpace**
- new and interesting approach in signal analysis
- easy, friendly and understandable UI
- modern technologies, for example: machine learning for spike calculations..
- continuously developing
- open to contribute

## **Run locally**
### **Installation**
#### **Quick install**
```
pip install -r requiremenets.txt
```
#### **Using conda (recommended)**
```
conda create -n <env_name> python==3.8
conda activate <env_name>
pip install -r requiremenets.txt
```
### **how to run**
```
python NeuroSpace.py
```


## **File structure**
this tree graph helps you to dive into our code and understand project file structure quickly. 
Controllers are the ones who takes care the whole process they call Modules objects and Widgets objects correspondently.

```bash
.
├── Controllers
│   ├── BinController.py
│   ├── Controller.py
│   ├── __init__.py
│   ├── SpikeController.py
│   ├── SpikeTogetherController.py
│   ├── StimulusActionController.py
│   ├── utils.py
│   └── WaveformController.py
├── default_parameters.json
├── dictionary.py
├── icons
├── Modules
│   ├── Bin.py
│   ├── Bursts.py
│   ├── __init__.py
│   ├── ParamChecker.py
│   ├── Spikes.py
│   ├── SpikeTogether.py
│   ├── StimulusAction.py
│   ├── stimulus.py
│   ├── utils.py
│   └── Waveform.py
├── NeuroSpace.py
├── PopupHandler.py
├── requirements.txt
├── styles
│   └── style.qss
├── UI.py
├── utils.py
└── Widgets
    ├── BinWidget.py
    ├── ChannelIdsWidget.py
    ├── default_widgets.py
    ├── __init__.py
    ├── SpikeTogetherWidget.py
    ├── SpikeWidget.py
    ├── StimulusActionWidget.py
    ├── utils.py
    └── WaveformWidget.py


## Contact

## **License**

