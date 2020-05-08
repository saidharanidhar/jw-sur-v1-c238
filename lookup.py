import json

movie_list = json.load(open("movieList.json"))

posters = json.load(open("moviePosters.json"))
custom = json.load(open("customMoviePosters.json"))

posters.update(custom)
