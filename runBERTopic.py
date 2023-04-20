import os
import argparse
from bertopic import BERTopic
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP 
from hdbscan import HDBSCAN
import pandas as pd

#define stopwords
stopWords = stopwords.words('english') 
for word in stopwords.words('german'):
    stopWords.append(word)
for word in stopwords.words('russian'):
    stopWords.append(word)
with open("data/stopwords_ua.txt") as file: #add ukrainian stopwords loaded from .txt file
    ukrstopWords = [line.rstrip() for line in file]
for stopwords in ukrstopWords:
    stopWords.append(stopwords)

vectorizer_model = CountVectorizer(ngram_range=(1, 2), stop_words=stopWords) #define vectorizer model with stopwords

def validate_file(f): #function to check if file exists
    if not os.path.exists(f):
        raise argparse.ArgumentTypeError("{0} does not exist".format(f))
    return f

class BERTopicAnalysis:
    """
    The following Class trains a BERTopic model on a given input file 
    and saves the model and visualizations in the given output folder.
    If the model already exists, meaning the output_folder already contains a BERTopic model,
    it can be loaded and solely used for inference.

    Parameters for the class:
    input_file: path to the input file
    output_folder: path to the output folder
    k_cluster: number of clusters to be used for the model
    do_inference: boolean to indicate if the model should also be used for inference, 
                predicting the class of each text line in the input file
    """

    # initialize class
    def __init__(self, input_file, output_folder, k_cluster, do_inference):
        self.input_file = input_file
        self.output_folder = output_folder
        self.k_cluster = k_cluster
        self.do_inference = do_inference

    # read input file and prepare data for BERTopic
    def read_data(self):
        self.df = pd.read_csv(self.input_file)
        self.df = self.df[self.df['messageText'].map(type) == str]
        self.df["messageText"] = self.df['messageText'].str.split().str.join(' ')
        lines = self.df[self.df['messageText'].str.len() >= 100].messageText.values
        self.text_to_analyse_list = [line.rstrip() for line in lines]

    # load potentially existing model
    def read_model(self):
        print("loading model")
        self.model=BERTopic.load(f"{self.output_folder}/BERTopicmodel")


    # check if k_cluster is numeric and convert to int if so.
    # this is necessary for BERTopic if the cluster number is given as a string, 
    # as BERTopic can be set to automatically determine the number of clusters using the string "auto".
    def k_cluster_type(self):
        if self.k_cluster.isnumeric():
            self.k_cluster = int(self.k_cluster)

    # train BERTopic model we use basic parameters for the model, 
    # using basic umap_model and hdbscan_model,
    # as defined in the BERTopic documentation
    def fit_BERTopic(self):
        umap_model = UMAP(n_neighbors=25, n_components=10, metric='cosine', low_memory=False, random_state=42)
        hdbscan_model = HDBSCAN(min_cluster_size=10, metric='euclidean', prediction_data=True)
        self.model = BERTopic(verbose=True,
                              language="multilingual",
                              nr_topics=self.k_cluster, 
                              vectorizer_model=vectorizer_model,
                              umap_model=umap_model,
                              hdbscan_model=hdbscan_model,
                              )
        topics, probs = self.model.fit_transform(self.text_to_analyse_list)

    # save model and visualizations
    def save_results(self):
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        fig = self.model.visualize_topics()
        fig.write_html(f"{self.output_folder}/bert_topic_model_distance_model.html")
        fig = self.model.visualize_hierarchy()
        fig.write_html(f"{self.output_folder}/bert_topic_model_hierarchical_clustering.html")
        fig = self.model.visualize_barchart(top_n_topics=30)
        fig.write_html(f"{self.output_folder}/bert_topic_model_word_scores.html")
        fig = self.model.visualize_heatmap()
        fig.write_html(f"{self.output_folder}/bert_topic_model_word_heatmap.html")
        self.model.save(f"{self.output_folder}/BERTopicmodel")
    
    # save representative documents for each topic
    def write_multi_sheet_excel(self):
        writer = pd.ExcelWriter(f"{self.output_folder}/representative_docs.xlsx", engine='xlsxwriter')
        for i in self.model.get_representative_docs().keys():
            df = pd.DataFrame(self.model.get_representative_docs()[i], columns=['message'])
            df.to_excel(writer, sheet_name=self.model.get_topic_info()[self.model.get_topic_info()['Topic']==i]['Name'].values[0][:31])
        writer.save()
        self.model.get_topic_info().to_csv(f"{self.output_folder}/topic_info.csv")

    # predict the class of each text line in the input file
    def inference(self):
        pred, prob = self.model.transform(self.df['messageText'].values)
        self.df['cluster'] = pred
        self.df.to_csv(f"{self.output_folder}/df_model.csv", index=False)

    # run all functions
    def run_all(self):
        self.read_data()
        if os.path.exists(f"{self.output_folder}/BERTopicmodel"):
            self.read_model()
        else:
            self.k_cluster_type()
            self.fit_BERTopic()
            self.save_results()
            self.write_multi_sheet_excel()
        if self.do_inference:
            self.inference()

def main():
    # define parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', help="Specify the input file", type=validate_file, required=True) #TODO change to argparse.FileType('r')
    parser.add_argument('-o', '--output_folder', help="Specify folder for results", required=True)
    parser.add_argument('-k', '--k_cluster', help="number of topic cluster", required=False, default="auto")
    parser.add_argument('-di', '--do_inference', help="does inference on data", action='store_true')
    args = parser.parse_args()
    # initialize class
    BERTopic_Analysis = BERTopicAnalysis(args.input_file,
                                         args.output_folder,
                                         args.k_cluster,
                                         args.do_inference
                                         )
    # run all functions
    BERTopic_Analysis.run_all()

if __name__ == '__main__':
    main()