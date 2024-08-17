"""Straemlit app for displaying screenplay character graphs and accessing database (H5Py)."""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from pdf_to_txt import *
from build_graph import *
from compare import *


def main():
    if "latest_action" not in st.session_state:
        st.session_state.latest_action = None
    if "latest_title" not in st.session_state:
        st.session_state.latest_title = None
    if "latest_matrix" not in st.session_state:
        st.session_state.latest_matrix = None
    if "latest_html" not in st.session_state:
        st.session_state.latest_html = None

    st.markdown(
        "<h1 style='font-size: 70px;'>Inside Screenplays</h1>",
        unsafe_allow_html=True)
    st.markdown('## Enter a screenplay to learn about its internal structure!')

    # Process uploaded file
    uploaded_file = st.file_uploader('Enter your PDF', type=['pdf', 'txt'])

    if uploaded_file:
        name = "_".join(uploaded_file.name.split(".")[:-1])
        if uploaded_file.name.endswith("pdf"):
            pdf = pdftotext.PDF(uploaded_file, physical=True)
            script = pdf_to_text_buffer(pdf)
        else:
            script = StringIO(uploaded_file.getvalue().decode("utf-8"))

        parsed_script = annotate(script)
        char_list, polarities, adjacency_matrix = read_script(parsed_script)

        graph_net = build_graph(char_list, polarities, adjacency_matrix)
        st.session_state.latest_html = graph_net.generate_html()
        st.session_state.latest_title = name
        st.session_state.latest_matrix = adjacency_matrix
        st.session_state.latest_action = "uploaded"

    # Process from Database
    st.write("")
    with st.form("form1"):
        with (h5py.File('movie_catalog.h5', 'r') as f):
            movie_catalog = ['Movie Catalog'] + list(f.keys())
            selected_movie = st.selectbox('Browse Movies', movie_catalog)

            if st.form_submit_button("Select") and selected_movie != "Movie Catalog":
                char_list, polarities, adjacency_matrix = get_movie(selected_movie)
                graph_net = build_graph(char_list, polarities, adjacency_matrix)
                st.session_state.latest_html = graph_net.generate_html()
                st.session_state.latest_title = selected_movie
                st.session_state.latest_matrix = adjacency_matrix
                st.session_state.latest_action = "selected"

    if st.session_state.latest_html:
        st.write(f"Network for {st.session_state.latest_title}")
        components.html(st.session_state.latest_html, height=750, width=750)

    if st.session_state.latest_action == "uploaded":
        if st.button("Save movie?", type="primary"):
            try:
                st.write(add_movie(st.session_state.latest_title, char_list, polarities, adjacency_matrix))
            except:
                st.write("Error.")

    if st.session_state.latest_title:
        col1, col2 = st.columns([2.33, 3])

        with col1:
            st.write("### Most similar movies by character structure:")
            similar_movies = get_similar_movies(st.session_state.latest_title, query_matrix=st.session_state.latest_matrix,
                                                similarity_fn=edges_among_leads)
            df = pd.DataFrame(similar_movies, columns=["Title", "Protagonist", "Distance"])
            st.dataframe(df.iloc[:, [0, 2]])
        with col2:
            st.write(f"### Most similar protagonists to {char_list[0]} by interactions:")
            similar_movies = get_similar_movies(st.session_state.latest_title, query_matrix=st.session_state.latest_matrix,
                                                similarity_fn=protagonist_edges)
            df = pd.DataFrame(similar_movies, columns=["Title", "Protagonist", "Distance"])
            st.dataframe(df, hide_index=True)


if __name__ == "__main__":
    # with h5py.File('movie_catalog.h5', 'r') as f:
    #     print([char.decode('utf-8') for char in f['harrypotter']['chars'][:]])
    #     print(f['harrypotter']['adjacency_matrix'][:])
    main()