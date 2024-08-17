"""Functions for comparing structural similarity of screenplays."""

from read_script import *
from build_graph import *
import numpy as np
from scipy import spatial


def index_matrix(matrix, k=20):
    """Pad or truncate square matrix."""
    m = len(matrix)
    if m < k:
        padded_matrix = np.zeros((k, k))
        padded_matrix[:m, :m] = matrix
        return padded_matrix
    else:
        return matrix[:k, :k]


def index_vector(vec, k=10):
    """Pad or truncate vector."""
    m = len(vec)
    if m < k:
        padded_vec = np.zeros(k)
        padded_vec[:m] = vec
        return padded_vec
    else:
        return vec[:k]


def normalized_laplacian_distance(A1, A2):
    """Normalized Laplacian distance between two adjacency matrices."""
    L1 = nx.normalized_laplacian_matrix(nx.from_numpy_array(A1)).toarray()
    L2 = nx.normalized_laplacian_matrix(nx.from_numpy_array(A2)).toarray()

    distance = np.linalg.norm(L1 - L2, 'fro')
    return distance


def protagonist_edges(A1, A2):
    """Compare protagonists' interactions with other charcters."""
    p1 = A1[0, 1:]
    p2 = A2[0, 1:]
    return spatial.distance.cosine(p1, p2)


def edges_among_leads(A1, A2, k=10):
    """Compare the interactions between the top k leads."""
    p1 = np.zeros(int((k*(k-1))/2),)
    p2 = np.zeros(int((k*(k-1))/2),)
    start = 0
    end = 0
    for i in range(k):
        end += (k-i-1)
        p1[start:end] = A1[i, i+1:k]
        p2[start:end] = A2[i, i+1:k]
        start = end
    return spatial.distance.cosine(p1, p2)


def lead_moods(m1, m2, k=10):
    """Compare polarities of top k leads."""
    return spatial.distance.cosine(index_vector(m1, k), index_vector(m2, k))


def filter_blobs(matrix):
    """Some faulty parses treat the screenplay as one whole scene, leading to a 'blob' structure.
    Filter these out for the purposes of better comparisons."""
    char_degrees = np.sum(matrix, axis=1)
    return char_degrees[0] != char_degrees[-1]


def get_similar_movies(query_movie, query_matrix=None,
                       similarity_fn=normalized_laplacian_distance, k=20, n=10):
    """Get top n similar movies of query_movie, along with scores."""
    if query_matrix is None:
        chars, _, query_matrix = get_movie(query_movie)
    top_n = []

    with (h5py.File('movie_catalog.h5', 'r') as f):
        movie_catalog = list(f.keys())
        for key_movie in movie_catalog:
            if query_movie != key_movie:
                chars, _, key_matrix = get_movie(key_movie)
                if np.sum(key_matrix) > 200 and filter_blobs(key_matrix):
                    distance = similarity_fn(index_matrix(query_matrix, k), index_matrix(key_matrix, k))
                    if len(top_n) < n:
                        # get protagonist in case of comparing protagonists
                        top_n.append((key_movie, chars[0], distance))
                    elif distance < top_n[-1][-1]:
                        top_n[-1] = (key_movie, chars[0], distance)
                    top_n = sorted(top_n, key=lambda x: x[-1])
    return top_n


if __name__ == "__main__":
    # print(get_similar_movies("nashville", similarity_fn=protagonist_edges()))
    # A2 = index_matrix(get_movie("littleathens")[1])
    # edges_among_leads(A1, A2)

    _, m1, _ = get_movie("nashville")
    _, m2, _ = get_movie("hungergamesthe")
    print(lead_moods(m1, m2))


