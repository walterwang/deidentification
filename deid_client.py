# -*- coding: utf-8 -*-
# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

# !/usr/bin/env python2.7

"""Send sentences to Tensorflow serving to be de-identified
"""

from __future__ import print_function

from grpc.beta import implementations
import tensorflow as tf
import numpy as np
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2
# tf.app.flags.DEFINE_string('server', 'localhost:9001', 'PredictionService host:port')
# FLAGS = tf.app.flags.FLAGS
import spacy
import pickle
import re
import unidecode
import os


def get_token_indices(token_lists):
    with open("resources/token_to_index.pkl", 'rb') as f:
        token_to_index = pickle.load(f)
    with open("resources/character_to_index.pkl", 'rb') as f:
        character_to_index = pickle.load(f)

    glove_index_data = []
    char_index_data = []
    for i in range(len(token_lists)):

        glove_index_seq = []
        char_index_seq = []

        max_token_length = len(max(token_lists[i], key=len))
        for token in token_lists[i]:
            char_token = []
            if token in token_to_index.keys():
                glove_index_seq.append(token_to_index[token])
            elif token.lower() in token_to_index.keys():
                glove_index_seq.append(token_to_index[token.lower()])
            elif re.sub('\d', '0', token) in token_to_index.keys():
                glove_index_seq.append(token_to_index[re.sub('\d', '0', token)])
            elif re.sub('\d', '0', token.lower()) in token_to_index.keys():
                glove_index_seq.append(token_to_index[re.sub('\d', '0', token.lower())])
            else:  # unknown indices #edited glove vector file with the last line 400001 (index=400000) being the unkonwn vector
                glove_index_seq.append(400000)
            for char in token:
                if char in character_to_index:
                    char_token.append(character_to_index[char])
                else:
                    char_token.append(0)
            for _ in range(max_token_length - len(token)):
                char_token.append(0)
            char_index_seq.append(char_token)

        glove_index_data.append(glove_index_seq)
        char_index_data.append(char_index_seq)

    return glove_index_data, char_index_data


def get_start_and_end_offset_of_token_from_spacy(token):
    start = token.idx

    end = start + len(token)
    return start, end

def get_sentences_and_tokens_from_spacy(text):

    spacy_nlp = spacy.load('en')
    document = spacy_nlp(text.decode('utf-8'))

    text = unidecode.unidecode(text.decode('utf-8'))
    sentences = []
    token_lists = []
    token_lenght_list = []

    for span in document.sents:

        sentence = [document[i] for i in range(span.start, span.end)]

        sentence_tokens = []
        sentence_lists =[]
        token_length = []
        for token in sentence:
            token_dict = {}
            token_dict['start'], token_dict['end'] = get_start_and_end_offset_of_token_from_spacy(token)
            token_dict['text'] = text[token_dict['start']:token_dict['end']]
            if token_dict['text'].strip() in ['\n', '\t', ' ', '']:
                continue

            sentence_lists.append(token_dict['text'])  # sentence lists
            token_length.append(len(token_dict['text']))
            sentence_tokens.append(token_dict)
        sentences.append(sentence_tokens)
        token_lenght_list.append(token_length)
        token_lists.append(sentence_lists)  # token_lists
    return sentences, token_lists, token_lenght_list


def run_client(sample_text):
    total_prediction_labels = []
    results = []
    with open("resources/prediction_index_to_label.pkl", 'rb') as f:
        index_to_label = pickle.load(f)
    label_vector = np.load("resources/input_label_indices_vector.npy")
    dropout_keep_prob = np.load('resources/dropout_keep_prob.npy')
    # host, port = FLAGS.server.split(':')
    host = 'localhost'
    port = 9001
    channel = implementations.insecure_channel(host, int(port))
    stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)

    # Send request
    # See prediction_service.proto for gRPC request/response details.
    request = predict_pb2.PredictRequest()
    request.model_spec.name = 'bilstm'
    request.model_spec.signature_name = 'predict_ner'
    sentences, tokens, token_lenght_list = get_sentences_and_tokens_from_spacy(
        sample_text)

    glove_index_data, char_index_data = get_token_indices(tokens)

    for i in range(len(glove_index_data)):

        request.inputs['dropout_keep_prob'].CopyFrom(tf.contrib.util.make_tensor_proto(dropout_keep_prob))
        request.inputs['tci'].CopyFrom(tf.contrib.util.make_tensor_proto(char_index_data[i]))
        request.inputs['input_token_lengths'].CopyFrom(
            tf.contrib.util.make_tensor_proto(token_lenght_list[i]))
        request.inputs['token_indices'].CopyFrom(tf.contrib.util.make_tensor_proto(glove_index_data[i]))
        request.inputs['label_indices_vector'].CopyFrom(
            tf.contrib.util.make_tensor_proto(label_vector, dtype=tf.float32))

        result = stub.Predict(request, 10.0)

        transitions, unary = result.__str__().split("unary")
        transitions = transitions.split("\n    float_val: ")[1:]
        transitions[-1] = transitions[-1][0:13]
        transitions = np.asarray(map(float, transitions)).reshape(95, 95)
        unary = unary.split("\n    float_val: ")[1:]
        unary[-1] = unary[-1].split("\n")[0]
        input_length = len(unary) / 95
        unary = np.asarray(map(float, unary)).reshape(input_length, 95)
        predictions, _ = tf.contrib.crf.viterbi_decode(unary, transitions)
        predictions = predictions[1:-1]
        prediction_labels = [index_to_label[prediction].encode('utf-8') for prediction in predictions]
        results.append(zip(tokens[i], prediction_labels))
        total_prediction_labels.append(prediction_labels)

    return total_prediction_labels, results, sentences


def run_on_text(sample_text, show_bio=False):
    predictions, results, sentences= run_client(sample_text)
    highlighted_words = []
    sample_text = sample_text.decode('utf8')

    for i in range(len(results)):
        for j in range(len(results[i])):
            if results[i][j][1] != "O":
                highlighted_words.append((results[i][j][1],sentences[i][j]['start'],sentences[i][j]['end']))

    for phi in reversed(highlighted_words):
        if not show_bio:
            label_name =phi[0].split("-")[-1]
        else:
            label_name = phi[0]
        sample_text = "".join((sample_text[:phi[1]],"{%s}"%label_name, sample_text[phi[2]:]))

    return sample_text


def run_on_textfile(filename, show_bio=False):
    f = open(filename, 'r')
    sample_text = f.read()
    f.close()
    deided_text = run_on_text(sample_text, show_bio)
    result_path =os.path.join("results_folder","deid_%s"%filename.split('/')[-1])
    with open(result_path, 'w') as results_file:
        results_file.write(deided_text.encode('utf-8'))
    return result_path

if __name__ == '__main__':
    run_on_textfile('uploaded_folder/texts_copy.txt', show_bio=False)


