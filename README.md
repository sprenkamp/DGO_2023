# R2G: Refugees to Government
This repository contains the code and resources for the paper "Refugees to Government: A Data-Driven Approach for Identifying Refugee Needs using Natural Language Processing and Topic Modeling" accepted at the [24th Annual International Conference on Digital Government Research](https://dgsociety.org/dgo-2023/conference/). R2G is a dashboard application designed to support public sector organizations in identifying and addressing the needs of refugees through a bottom-up approach, using state-of-the-art NLP techniques and topic modeling.

In this study, we focus on the refugee management scenario within Switzerland and demonstrate how R2G can be used to extract insights from large text corpora, in this case, public Telegram messages from the Ukrainian refugee population.

The application R2D was mainly created through the four python scripts: `scrapeTelegramChannelMessages.py`, `runBERTopic.py`, `transformResults.py`, `appSwitzerland.py`. We provide an architecture diagram below to show the complete interaction of the given files:

![architecture diagram](/architecture_diagram/architecture_diagram.png "architecture_diagram")

Further we provide a `reqiurements.txt` file, which allows to install the necessary python packages and dependencies. We tested the installation on a Linux based GPU cluster and a 2021 M1 Macbook Pro. To install the requirements we recommend create a new virtual environment and run:

`pip install -r requirements.txt`

Below each of the four files is explained briefly and sample usage is shown. More information can be gathered from the comments within the code.

1. `scrapeTelegramChannelMessages.py` takes a list of open telegram channels as input, compare `data/switzerland_groups.txt` and scrapes the message text and the date the message was written on. It then save the results as a `.csv` file, the sample use is shown below:

`python scrapeTelegramChannelMessages.py -i data/switzerland_groups.txt -o data/df_telegram.csv`

2. `runBERTopic.py` runs the BERTopic algorithm on a given dataset e.g. `data/df_telegram.csv` obtained from the prior step. Further, we can specify where the outputs, meaning the model, some visualisation for analysis and output `.csv` files will be saved. Moreover, we can specify the number of clusters the algorithm should create. Last, we can specify if the trained model should do inference as well, meaning if it should predict to which topic a message belongs to for the input dataset. The results of the model are saved under `myBERTopicModel/df_model.csv` Below the example usage is shown for the dataset `data/df_telegram.csv` we save our output to a folder, which the script creates named `myBERTopicModel`, we define the algorithm should create `25` cluster and also do infernece `--di`.

`python runBERTopic.py -i data/df_telegram.csv -o myBERTopicModel -k 25 --di`

3. `transformResults.py` takes the results of the BERTopic model and gives each cluster a name. This is done via qualitativ analysis of each cluster. Thus if the code is rerun, this qualitativ analysis has to be done by the user. Within the python script one can then modify the dictionary `class_name_dict` to give each cluster a distinctive name. The file takes as input the results of the BERTopic model and outputs the modified dataframe used within the Streamlit app. Example usage is shown below:

`python transformResults.py -i myBERTopicModel/df_model.csv -o data/df_prep.csv`

4. `appSwitzerland.py` contains the Streamlit application for displaying the results of the BERTopic analysis. The app can be utilized [here](https://dgosubmission2023-r2g.streamlit.app/). Local hosting of the app can be done using the command below. For the hosting provided by the Streamlit Cloud we utilized another private Github repo. For the app to run the prior created `data/df_prep.csv` must be available.

`streamlit run appSwitzerland.py`
