#!/bin/bash

(/tensorflow-serving/bazel-bin/tensorflow_serving/model_servers/tensorflow_model_server --port=9001 --model_name=bilstm --model_base_path=/deidentification/model) &
(cd /deidentification; export FLASK_APP=flaskform.py; flask run --host=0.0.0.0)
