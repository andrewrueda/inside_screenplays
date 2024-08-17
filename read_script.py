"""Comb through screenplay json to get characters, polarity of the characters' lines,
and adjacency matrix of their scene co-occurrences."""

import json
import os
from nltk.sentiment import SentimentIntensityAnalyzer

import numpy as np
import regex as re
from collections import defaultdict, Counter
from pdf_to_txt import *
from ScreenPy.screenpile import *

nltk.download('vader_lexicon')
sentiment = SentimentIntensityAnalyzer()


class Character:
    """Store character-level information"""
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.lines = []
        self.co_occurrences = Counter()
        self.polarity = None

    def add_line(self, line):
        self.lines.append(line)


def read_headings(movie_path):
    """Print all heading types (for testing)"""
    movie_file = open(movie_path)
    movie_data = json.load(movie_file)
    for scene in movie_data:
        for shot in scene:
            print(shot['head_type'])


def read_script(movie_input, from_disk=False, do_print=False):
    """Parses script JSON, converts into list of characters, character polarities,
    and associated Adjacency Matrix."""
    if from_disk:
        movie_file = open(movie_input)
        movie_data = json.load(movie_file)
    else:
        movie_data = json.load(movie_input)
    characters = dict()

    n_scenes = 0
    for scene in movie_data:
        n_scenes += 1
        # scene_lines = Counter()
        in_scene = set()

        for shot in scene:
            # Handle speaker/title segments
            if shot['head_type'] == "speaker/title":
                speaker = process_speaker(shot['head_text']['speaker/title'])
                if speaker and speaker not in {'CUT TO:', 'THE END'}:
                    pattern = r'^(?!.*:).*$'
                    if '(V.O.)' not in speaker.split(' ') and re.match(pattern, speaker):
                        characters.setdefault(speaker, Character(speaker)).add_line(shot['text'])
                        in_scene.add(speaker)
                        # scene_lines[speaker] += 1

        # track co-occurrences:
        for name in in_scene:
            for co_occur in in_scene:
                if name != co_occur:
                    characters[name].co_occurrences[co_occur] += 1

    # Store character lists, character polarities, and adjacency matrix
    char_list = [char for char in characters.keys() if len(characters[char].co_occurrences) > 0]
    char_list.sort(key=lambda x: sum(characters[x].co_occurrences.values()), reverse=True)
    char_indices = {char: index for index, char in enumerate(char_list)}
    adjacency_matrix = np.zeros((len(char_list), len(char_list)))

    polarities = []
    for character_name in char_list:
        character = characters[character_name]
        co_occurs = character.co_occurrences
        for co_occur, count in co_occurs.items():
            adjacency_matrix[char_indices[character_name]][char_indices[co_occur]] = count

        char_polarity = sentiment.polarity_scores(" ".join(character.lines))
        character.polarity = char_polarity['pos'] - char_polarity['neg']
        polarities.append(character.polarity)

    if do_print:
        print(n_scenes)
        for name, character in characters.items():
            print(f"{name} {sum(characters[name].co_occurrences.values())}")
            print(characters[name].co_occurrences)
            print(characters[name].lines)
            print(characters[name].polarity)
            print()

    return char_list, polarities, adjacency_matrix


def process_speaker(speaker_line):
    """Clean speaker string"""
    split_pattern = r'[ ,]'
    remove_pattern = r'[()*]'
    to_split = re.compile(split_pattern)
    to_remove = re.compile(remove_pattern)

    tokens = re.split(to_split, speaker_line)
    for token in reversed(tokens):
        if to_remove.search(token):
            tokens.remove(token)
    return " ".join(tokens).strip()


if __name__ == "__main__":
    movie = "harrypotterandthechamberofsecrets"

    pdf_to_txt(f"test_files/test_pdf/{movie}.pdf")
    annotate_disk(f"test_files/test_txt/{movie}.txt")

    # annotate_disk(f"ScreenPy/imsdb_raw_nov_2015/Action/{movie}.txt")
    read_script(f"test_files/test_json/{movie}.json", from_disk=True, do_print=True)
