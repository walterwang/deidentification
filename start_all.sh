#!/bin/bash

(cd /home/walter/build_from_source/serving; bazel-bin/tensorflow_serving/model_servers/tensorflow_model_server --port=9001 --model_name=bilstm --model_base_path=/home/walter/Documents/my_git/deidentification/model) &
(cd /home/walter/Documents/my_git/deidentification; export FLASK_APP=flaskform.py; flask run)
