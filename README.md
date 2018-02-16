# Deidentification

A tensorflow-serving deidentification service. 

## Getting Started 


### Prerequisites
Install requirements
```
pip install -r requirements.txt
```

Install Spacy english models 

```
python -m spacy download en
```

Install Tensorflow Model Server
```angular2html
echo "deb [arch=amd64] http://storage.googleapis.com/tensorflow-serving-apt stable tensorflow-model-server tensorflow-model-server-universal" | sudo tee /etc/apt/sources.list.d/tensorflow-serving.list

curl https://storage.googleapis.com/tensorflow-serving-apt/tensorflow-serving.release.pub.gpg | sudo apt-key add -
```

```angular2html
sudo apt-get update && sudo apt-get install tensorflow-model-server
```
if tensorflow-model-server doesn't work, you can try to install _tensorflow-model-server-universal_ In that case modify the appropriate line in start_all.sh. For more details, take a look at https://www.tensorflow.org/serving/setup

## Getting started

```
1. bash start_all.sh

2. open web browser go to: 
http://127.0.0.1:5000/
```

## Acknowledgements

This is a modified version of NeuroNER designed for tensorflow serving. If you want to train or get additional features go to the original at:
https://github.com/Franck-Dernoncourt/NeuroNER
Look at my forked version of NeuroNER for details on modifying the model to a servable version. 