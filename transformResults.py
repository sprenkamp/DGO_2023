import pandas as pd
import json
import os 
import argparse

#define dictionaries for class names and canton chat links
class_name_dict = {-1:"no_class",
    0:"Medical Information",
    **dict.fromkeys([1, 13, 15], "Asylum Information and “S Permit” Application"),
    2:"Veterinarian",
    3:"Banking",
    4:"Consulate Services",
    **dict.fromkeys([5, 17], "Transportation between Ukraine and Switzerland"),
    **dict.fromkeys([6, 7], "Integration Problems"),
    8:"Education",
    9:"Accomodation",
    10:"Train and Bus Transport in Europe",
    11:"Dentistry Information",
    **dict.fromkeys([12, 16, 22, 23], "Social Services"),
    14:"Quality Refugee Camp",
    18:"Train Bus Transport in Switzerland",
    19:"Personal Care",
    20:"Employment Opportunities",
    21:"Accomodation", 
    24:"Vaccination"
}

canton_chat_dict = {'https://t.me/helpfulinfoforua': 'all Cantons',
 'https://t.me/ukraine_reborn': 'all Cantons',
 'https://t.me/BeautySwitzerland': 'all Cantons',
 'https://t.me/help_people_fromUkraine': 'all Cantons',
 'https://t.me/LousanneUkraine': 'Vaud',
 'https://t.me/LuzernUkraine': 'Lucerne',
 'https://t.me/ValaisUkraine': 'Valais',
 'https://t.me/ThurgauUkraine': 'Thurgau',
 'https://t.me/BielBienneUkraine': 'Bern',
 'https://t.me/fribourg1': 'Fribourg',
 'https://t.me/campax_ukraine_help_switzerland': 'all Cantons',
 'https://t.me/refugeesinSwitzerland': 'all Cantons',
 'https://t.me/zh_helps_ukraine': 'Zürich',
 'https://t.me/zh_helps_UArefugee': 'Zürich',
 'https://t.me/zurich_hb_help': 'Zürich',
 'https://t.me/zh_housing': 'Zürich',
 'https://t.me/helppetsfromukraine': 'all Cantons',
 'https://t.me/Zurich_UA': 'Zürich',
 'https://t.me/zh_helps_UArefugees': 'Zürich',
 'https://t.me/seep_helpukrainians': 'all Cantons',
 'https://t.me/Zh_helps_UA_mums': 'Zürich',
 'https://t.me/job_sw_ukrainians': 'all Cantons',
 'https://t.me/zh_back_ukraine': 'Zürich',
 'https://t.me/zh_helps_logistics': 'Zürich',
 'https://t.me/AargauUkraine': 'Aargau',
 'https://t.me/BernUkraine': 'Bern',
 'https://t.me/TicinoLuganoUkraine': 'Ticino',
 'https://t.me/UASchweiz': 'all Cantons',
 'https://t.me/SwissUA': 'all Cantons',
 'https://t.me/BaselUkraine': 'Basel',
 'https://t.me/ukrainer_basel': 'Basel',
 'https://t.me/GeneveUkraine': 'Genève',
 'https://t.me/StGallenUkraine': 'Sankt Gallen'}

# load dictionary with cities and cantons 
f = open('data/cities_in_canton.json') 
# returns JSON object as a dictionary
ciy_canton_dict = json.load(f)

def validate_file(f): #function to check if file exists
    if not os.path.exists(f):
        raise argparse.ArgumentTypeError("{0} does not exist".format(f))
    return f

#check if city is in message string and return canton
def check_key_in_string(string, dictionary):
    """
    Function to check if a key is in a string and returns 
    the value of the key if it is in the string.

    :string: string to check
    :dictionary: dictionary to check for keys
    """
    for key in dictionary:
        if key in string:
            return dictionary[key]
    return "all Cantons"

def transformResults(input_file_path, output_file_path):
    """
    This function transforms the results of the clustering, after doing
    a qualitative analysis of the clusters. It also adds the canton of message 
    if it can be estimated from messageText or the chat name.
    All messages that are not assigned to a cluster are removed.
    Further, it adds the week of the year to based on messageDatetime.

    :input_file_path: path to the input file
    :output_file_path: path to the output file
    """
    df = pd.read_csv(input_file_path) # read in csv file
    df = df[df.cluster!=-1] # remove messages that are not assigned to a cluster
    # gives each cluster a name based on the qualitative cluster analysis
    df['cluster_names'] = df['cluster'].apply(lambda x: class_name_dict[x]) 
    # check if city is in message string and return canton NOTE currently we solely use the most common spelling of a city
    # afterwards we use the chat name to get the canton
    # NOTE the chat name overrides the prior string analysis
    df['region'] = df['messageText'].apply(lambda x: check_key_in_string(x, ciy_canton_dict)) 
    df['region'] = df['chat'].apply(lambda x: canton_chat_dict[x])
    # get week of the year from messageDatetime
    df['week']=df['messageDatetime'].apply(lambda x: pd.to_datetime(x).isocalendar()[1])
    df = df[["chat","messageText","messageDatetime","cluster","cluster_names","region","week"]]
    df.to_csv(output_file_path, index=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', help="Specify the location of the input file", type=validate_file, required=True)
    parser.add_argument('-o', '--output_file', help="Specify location of the output file", required=True)
    args = parser.parse_args()
    transformResults(args.input_file, args.output_file)

if __name__ == '__main__':
    main()