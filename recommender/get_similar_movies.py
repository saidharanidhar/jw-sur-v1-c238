#!/usr/bin/env python
# coding: utf-8

import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
from sklearn.metrics.pairwise import euclidean_distances

df_movie = pd.read_pickle("recommender/similar_movies.pkl")


def find_similar_movies(movie_name, df_movie=df_movie):
    """
    INPUT:
    movie_name - (int) a movie_name
    df_movie - (pandas dataframe) matrix of movie similarity
                
    size - (int) number of top similar movies
    OUTPUT:
    similar_users - (list) an ordered list where the closest movies (largest dot product movies)
                    are listed first
    
    Description:
    Computes the similarity of every pair of users based on the dot product
    Returns an ordered
    
    """
    if movie_name in df_movie.primaryTitle.tolist():
        provided_movie = df_movie[df_movie.primaryTitle == movie_name]
        similarity_df = df_movie[[0, 1]]
        df_movie['dist'] = euclidean_distances(similarity_df[[0, 1]], provided_movie[[0, 1]])
        df_movie.dist = df_movie.dist.abs()
        sorted_df = df_movie.sort_values('dist')
        sorted_df = sorted_df[sorted_df.primaryTitle != movie_name]
        most_similar_users = sorted_df['primaryTitle'].tolist()
        return most_similar_users
    else:
        return None


def get_similar_movies(movies, number_of_movies=1000):
    """
    INPUT:
    movies - (list) a list of movies    
    OUTPUT:
    similar_movies - (list) an ordered list where the closest movies (largest dot product movies)
                    are listed first
    
    Description:
    return movie recommendations
    """
    # check how many movies are in the dataset
    common_movies = np.intersect1d(movies, df_movie.primaryTitle)
    com_len = len(common_movies)
    if com_len < 1:
        return []
    else:
        rec_dict = {}
        for current_movie in common_movies:
            suggested_movies = find_similar_movies(current_movie)
            rec_dict[current_movie] = suggested_movies
        rec_df = pd.DataFrame(rec_dict)
        rec_df_long = rec_df.values.reshape((rec_df.shape[0] * rec_df.shape[1], 1))
        rec_df_long = pd.DataFrame(rec_df_long)
        rec_df_long.columns = ["movies"]
        recs = []
        while len(recs) < number_of_movies:
            for movie_name in rec_df_long.movies.values:
                if movie_name not in common_movies and movie_name not in recs:
                    recs.append(movie_name)
                if len(recs) > number_of_movies:
                    break
        return recs[0:number_of_movies]
