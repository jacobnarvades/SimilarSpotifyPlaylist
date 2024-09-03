from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np
import math
import os
from sklearn.metrics.pairwise import cosine_similarity

def song_pca(songs_metadata, song_ids, playlist_title='playlist', mode='default', mean=[], n_components=5):
    # Convert song metadata to a matrix (rows as songs, columns as features)
    songs_matrix = np.array(list(songs_metadata.values()))

    # Compute mean and variance to compare found songs, add to matrix/dictionary
    if (mode == 'playlist'):
        mean_features = np.mean(songs_matrix, axis=0)
        mean_features = [float(f'{val:.2f}') for val in mean_features] 
        songs_matrix = np.vstack([mean_features, songs_matrix])

        d_mean_features = {}
        d_mean_features['reference'] = mean_features
        songs_metadata = {**d_mean_features, **songs_metadata}

    # Standardize the data (mean=0, variance=1)
    scaler = StandardScaler()
    songs_std = scaler.fit_transform(songs_matrix)

    # Apply PCA
    if (mode == 'playlist'):
        n_components = math.floor(4*math.log(len(songs_metadata), 10)) #maps the n_components to a value based on the amount of tracks dynamically
        if (n_components > 12):
            n_components = 12

    pca = PCA(n_components)  # Define the number of principal components
    songs_pca = pca.fit_transform(songs_std)

    # Explained variance ratio
    explained_var_ratio = pca.explained_variance_ratio_

    # Calculate colors based on distances from mean and similarity ratios
    cosine_ratio = math.log(n_components, 10) - 0.1
    euclidean_ratio = 1-cosine_ratio
    if (mode == 'playlist'):
        mean = songs_pca[0]
    similarity_scores = calculate_similarities(songs_pca, mean, cosine_ratio, euclidean_ratio)  # Using first point as mean

    # Sort songs by similarity scores
    sorted_indices = sorted(range(len(similarity_scores)), key=lambda i: similarity_scores[i], reverse=True)

    # Retrieve top similar songs
    divisor = 0
    if (mode == 'playlist'):
        divisor = 2
    elif (mode == 'recommend'):
        divisor = 6

    top_similar_indices = sorted_indices[1:int(len(songs_metadata)/divisor)]  # Exclude the reference song itself
    top_similar_songs = [list(songs_metadata.keys())[index] for index in top_similar_indices]
    song_ids = [song_ids[index-1] for index in top_similar_indices]

    # create a pair of songs and ids
    songs_and_ids = {}
    length = math.floor(len(songs_metadata)/2)
    n = 0
    for song_name, song_id in zip(top_similar_songs, song_ids):
        if (n == length):
            break
        songs_and_ids[song_name] = song_id
        n += 1

    if (mode == 'recommend'):
        reference_song_index = 0  # Change this index to your chosen reference song
        reference_song_name = list(songs_metadata.keys())[reference_song_index]
        print(f"\n{playlist_title}:")
        for idx, song_index in enumerate(top_similar_indices):
            print(f"{top_similar_songs[idx]} {similarity_scores[song_index]:.2f}")
        print('\n')

    return songs_and_ids, mean, n_components


def calculate_similarities(points, mean, cosine_ratio, euclidean_ratio):
    similarity_scores = [(cosine_ratio * cosine_similarity([mean], [point])[0][0]) +
                         (euclidean_ratio * (1 / (1 + np.linalg.norm(mean - point)))) for point in points]

    # Min-Max scaling to standardize similarity scores to the range of 1 to 100
    max_similarity = max(similarity_scores)
    min_similarity = min(similarity_scores)
    scaled_similarities = [100 * (score - min_similarity) / (max_similarity - min_similarity) if max_similarity != min_similarity else 50 for score in similarity_scores]
    return scaled_similarities