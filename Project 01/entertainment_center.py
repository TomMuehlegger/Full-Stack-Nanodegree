import fresh_tomatoes
import media

# Create some favorite movies
deadpool = media.Movie("Deadpool",
                       "Justice has a new face",
                       "http://cdn.traileraddict.com/content/20th-century-fox/deadpool-poster-8.jpg", # noqa
                       "https://www.youtube.com/watch?v=Xithigfg7dA")

x_men = media.Movie("X-Men: Apocalypse",
                    "Only the strong will survive",
                    "http://cdn.traileraddict.com/content/20th-century-fox/xmen-apocalypse-3.jpg", # noqa
                    "https://www.youtube.com/watch?v=PfBVIHgQbYk")

captain_america = media.Movie("Captain America: Civil war",
                              "Divided we fall",
                              "http://cdn.traileraddict.com/content/marvel-studios/captain-america-civil-war.jpg", # noqa
                              "https://www.youtube.com/watch?v=dKrVegVI0Us")

hail_caesar = media.Movie("Hail, Caesar",
                          "Lights, camera, abduction.",
                          "http://cdn.traileraddict.com/content/universal-pictures/hail_caesar-2.jpg", # noqa
                          "https://www.youtube.com/watch?v=kMqeoW3XRa0")

kung_fu_panda_3 = media.Movie("Kung Fu Panda 3",
                              "The weight is over",
                              "http://cdn.traileraddict.com/content/dreamworks-animation/kung-fu-panda3.jpg", # noqa
                              "https://www.youtube.com/watch?v=10r9ozshGVE")

hateful_eight = media.Movie("The Hateful Eight",
                            "No one comes up here without a damn good reason",
                            "http://cdn.traileraddict.com/content/the-weinstein-company/hateful_eight.jpg", # noqa
                            "https://www.youtube.com/watch?v=6_UI1GzaWv0")

# Insert all the movies into a list
movies = [deadpool,
          x_men,
          captain_america,
          hail_caesar,
          kung_fu_panda_3,
          hateful_eight]

# Display these movies on the movie page
fresh_tomatoes.open_movies_page(movies)
