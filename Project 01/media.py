class Movie():
    """Movie class containing some informations about a movie
    
    Attributes:
        title: Title of the movie
        description: Description of the movie
        poster_image_url: URL of the poster image
        trailer_youtube_url: URL of the youtube trailer
    """
    
    def __init__(self, movie_title, movie_description, poster_image_url, trailer_youtube_url):
        """Inits a Movie with specified informations."""
        self.title = movie_title
        self.description = movie_description
        self.poster_image_url = poster_image_url
        self.trailer_youtube_url = trailer_youtube_url
