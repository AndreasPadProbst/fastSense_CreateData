# Extracting Training Data for Word Sense Disambiguation from German Wikipedia Dump

## Table of contents
* [General info](#general-info)
* [Setup](#setup)
* [Required Data](#required-data)
* [How to Use](#how-to-use)
* [Code Example](#code-example)
* [Hints](#hints)

## General Info
This package creates a WSD Trainings Corpus from the disambiguation pages of the German Wikipedia. The main structure of this code is taken from [https://github.com/texttechnologylab/fastSense](https://github.com/texttechnologylab/fastSense) (accessed: 20.02.2021) and modified to be able to parse
the German version of the Wikipedia. Also, the original code uses the [CoreNLP](https://stanfordnlp.github.io/CoreNLP/) java library from the Stanford NLP Group. As
not all desired modules are available for the German language, like a lemmatizer, the spaCy library is used here instead. 

[https://github.com/texttechnologylab/fastSense](https://github.com/texttechnologylab/fastSense) is a model based on fastSense (see [paper](https://www.aclweb.org/anthology/L18-1168/)).
The model from the texttechnology lab extended the original fastSense model is entirely written in Python and can be used without any external applications, in contrast to the original
paper which used an external UIMA-based framework called "Textimager" for the preprocessing of their text data. Also, texttechnology lab's model is optimized to run on six processing cores simulatenously.

## Setup
This package was used with **Python 3.6** with the following package specifications:
* **ftfy** = 5.9
* **mwparserfromhell** = 0.6
* **spacy** = 3.0 (along with the "de_core_news_lg" pipeline)

## Required Data
Following dumps need to be downloaded from [here](https://dumps.wikimedia.org/dewiki/) (accessed: 21.02.2021):

* dewiki-*-categorylinks.sql.gz
* dewiki-*-page.sql.gz
* dewiki-*-pages-articles.xml.bz2

## How to Use
Step 1: 
to extract the relevant senses, corresponding page links, sense groups and tokens, the cli_wiki_extract.py script has to be executed with the following command line arguments:

* **--dump**: path to the Bz2-compressed XML dump of the German Wikipedia (dewiki-*-pages-articles.xml.bz2)
* **--page_table**: path to Gzip-compressed SQL dump of page table (dewiki-*-page.sql.gz)
* **--categorylinks_table**: path to Gzip-compressed SQL dump of categorylinks table. (dewiki-*-categorylinks.sql.gz)
* **--intermediate**: path to folder where intermediate information about tokens and links will be stored
* **--db**:  path to sqlite3 database where information about the senses and sense groups is stored

Step 2:
to export the extracted data into a format more suitable for training, the cli_wiki_export.py script has to be executed with the following command line arguments:

* **--intermediate**: path to the folder where intermediate files from previous step are stored
* **--db**: path to sqlite3 database from previous step
* **--output**: path to output folder for training data
* **-f**: Comma-separated options for output. [Name],[N-Gram Size],[Caseless],[Ignore Punctuation],[Add PoS Tags], [Uses Lemma],[Uses Sentences]. E.g.: *-f p_out,1,0,0,1,1,0 s_out,1,0,0,1,1,1\*

## Code Example
```
python cli_wiki_extract.py --page_table ./data/dewiki-latest-page.sql.gz --categorylinks_table ./data/dewiki-latest-categorylinks.sql.gz 
--db ./data/sql3_db/fastSense.db --intermediate_output ./data/intermediate --dump ./data/dewiki-latest-pages-articles.xml.bz2
```
```
python cli_wiki_export.py --intermediate ./data/intermediate --db ./data/sql3_db/fastSense.db --output ./data/export_output -f p_out,1,0,0,1,1,0 
```

## Hints
* run scripts over night (10+ hours runtime each)
* the second script creates over 60M training samples and requires 500GB+ disk storage, so use external hard disk/ssd to store training data
