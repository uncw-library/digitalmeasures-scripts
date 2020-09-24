These are a variety of scripts related to the DigitalMeasures/ActivityInsight API.

They have text comments describing the dataset.  But you'll need an API login user/pass to actually run them.

## scrape_userrecords.py

This grabs all the user records from the API & saves them as xml in ./output/users/

## QueryingAPI.ipynb

A jupyter notebook with all the available API endpoints & examples for many of them.

## ParsingUsers.ipynb

A jupyter notebook that finds the edges of our dataset.  Finds which files are outliers.  Describes the normal user files.

Lots of *Take Aways* summaries in this notebook.

## Unique_Identifiers.ipynb

A jupyter notebook that finds which *id* attributes show up more than once.  These *id* tags link the same object between user files.

## FindingBrokenText.ipynb

A jupyter notebook that searches ./output/users/ files for characters that may not be representable in utf-8.


