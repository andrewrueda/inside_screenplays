# Inside Screenplays
Visualize movie character structure from screenplay PDF and TXT files!

## Overview

This Streamlit-powered app allows you to view
the character network of feature-length screenplays.
You can either choose a movie from the database, or add
your own PDF or TXT file and save it.

The resulting graph (powered by ```pyvis```) displays the characters as nodes,
with weighted edges representing scene co-occurrence, as well as
character-level information about their role in the network.

The characters are also separated into communities and color-coded.

## Dependencies and Setup

### requirements

```commandline
pip install -r requirements.txt
```

### sense2vec
Download ```s2v_reddit_2015_md.tar.gz```:

```
https://github.com/explosion/sense2vec
```
Place in ```ScreenPy/sv2``` and open.

## Usage

```commandline
streamlit run inside_screenplays.py
```

After running the app, you have the option to either
browse the movies in the database, or upload your own
PDF or TXT file of a feature length screenplay.

Selecting an option from the "Movie Catalog" will access the movie's
information from the database (an H5Py file) and display the graph.


<table>
  <tr>
    <td>
      <img alt="page1.png" height="300" src="screenshots/page1.png" width="400"/>
      <br>
      <figcaption>Home screen</figcaption>
    </td>
    <td>
      <img alt="page2.png" height="300" src="screenshots/page2.png" width="400"/>
      <br>
      <figcaption>Graph for selected movie</figcaption>
    </td>
  </tr>
</table>

The graph also contains node-level information, such as degree, ranks in
Degree, Betweenness, and Closeness centrality and the sentiment
polarity of their dialogue in the screenplay.

All movies in the database are compared for structural similarity, and the most similar
movies are returned.

<figure style="display: inline-block; margin-right: 0px; text-align: left;">
  <img alt="nodes.png" height="500" src="screenshots/nodes.png" width="550"/>
  <figcaption>Information for HARRY in Dumb and Dumber</figcaption>
</figure><br/><br/>

<figure style="display: inline-block; margin-right: 0px; text-align: left;">
  <img alt="similar_movies.png" height="400" src="screenshots/similar_movies.png" width="600"/>
  <figcaption>Similar movies to Dumb and Dumber by <code>protagonist_edges</code> and <code>edges_among_leads</code> similarity functions.</figcaption>
</figure><br/>

If you want to use your own PDF or TXT, drop it in and get a new graph. You can then save
it to add it to the database:

<figure style="display: inline-block; margin-right: 0px; text-align: left;">
  <img alt="add_movie.png" height="500" src="screenshots/add_movie.png" width="600"/>
  <figcaption>Save movie to database</figcaption>
</figure>

## Details

### App
The app was created in Streamlit. It connects to a text processing pipeline
that includes PDF to TXT (using ```pdftotext```), TXT to JSON (using ```ScreenPy```),
```read_script.py``` which parses the json-structured screenplay information
for character lines and interaction, and ```build_graph.py``` which builds the
graph and manages the movies in the database (```movie_catalog.h5``` with ```h5Py```).

### Graph Data

Part of the goal of this project is to highlight some insights into
the character structure of screenplays. In ```read_script.py```, each
character's lines are collected and run through NLTK's
```SentimentIntensityAnalyzer```, in order to assign a sentiment polarity
score for each character.

Also, we can use graph theory to calculate each node's importance in the
graph by calculating their Degree Centrality, Betweenness centrality
(importance to flow of the graph), and Closeness centrality
(strongly connected to other nodes).

Inside Screenplays also visualizes the community breakdown of the
character network using the ```community-louvain``` API by color-coding
the various communities in the network.

### Similarity Scores

There are several possible ways to measure similarity between two adjacency
matrices. Included in ```compare.py``` are Normalized Laplacian distance,
```edges_among_leads```: cosine distance between two vectors, each representing
a movie's weighted edges between its top k characters, and ```protagonist_edges```:
cosine distance where each vector represents a movie's main character's connections to
the top k other characters in the movie.

The latter two yield some promising results as a heuristic to identify movies
with similar structure. Take the movies <b>Dumber and Dumber</b> and <b>Rush Hour 2</b>,
which have a high similarity when using ```edges_among_leads```:

<figure style="display: inline-block; margin-right: 0px; text-align: left;">
  <img alt="dumbanddumber.png" height="500" src="screenshots/dumbanddumber.png" width="750"/>
</figure>

<figure style="display: inline-block; margin-right: 0px; text-align: left;">
  <img alt="rushhour2.png" height="500" src="screenshots/rushhour2.png" width="750"/>
  <figcaption>Comparison between <b>Dumber and Dumber</b> and
<b>Rush Hour 2</b>,
which have a low distance score of <code>0.0264</code>.</figcaption>
</figure>








