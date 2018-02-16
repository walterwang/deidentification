#!/bin/bash

#(/home/walter/build_from_source/serving/bazel-bin/tensorflow_serving/model_servers/tensorflow_model_server --port=9001 --model_name=bilstm --model_base_path=$PWD/model) &
(tensorflow_model_server --port=9001 --model_name=bilstm --model_base_path=$PWD/model) &
(export FLASK_APP=flaskform.py; flask run)
