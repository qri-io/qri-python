qri-python
========================

.. code:: python
    """
     ██████╗ ██████╗ ██╗
    ██╔═══██╗██╔══██╗██║
    ██║   ██║██████╔╝██║
    ██║▄▄ ██║██╔══██╗██║
    ╚██████╔╝██║  ██║██║
     ╚══▀▀═╝ ╚═╝  ╚═╝╚═╝
    """

qri python client


Installation
-------------

.. code:: sh

    pip install qri


Usage
---------

.. code:: python

    import qri
  
    # List datasets on your qri node
    qri.list_ds()
  
    """
    >>> [u'movies', u'airports', ..., u'detroit_exposure_and_aerosol', ]
    """
  
    # Load a dataset by referencing its name
    movies = qri.load_ds("me/movies")
  
    #access metadata
    movies.head["meta"]["title"]
    """
    >>> u'imdb-5000-movie-dataset'
    """
  
    movies.ds_name
    """
    >>> u'movies'
    """
  
    movies.head["meata"]["description"]
    """
    >>> u"This is a dataset of 5000 films sourced from the Internet Movie Databse (IMDB) with relevant information on the films' production (director, actors, etc) and critical reception (IMDB score, facebook likes etc) among other details"
    """

    #access data
    movies.body
    """ #returns pandas DataFrame containing the data

                     color       director_name  num_critic_for_reviews  duration  \
    0                Color       James Cameron                   723.0     178.0
    1                Color      Gore Verbinski                   302.0     169.0
    2                Color          Sam Mendes                   602.0     148.0
    3                Color   Christopher Nolan                   813.0     164.0
    4                  NaN         Doug Walker                     NaN       NaN
    5                Color      Andrew Stanton                   462.0     132.0
    6                Color           Sam Raimi                   392.0     156.0
    ...
  
    """
  
    # make a change and save the changes
    movies.body["director_name"] = movies.body["director_name"].apply(lambda x: x.lower())
    # save and include a commit message
    movies.save("made director field lower case")
  
  

