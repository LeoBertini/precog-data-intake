
"""
Loads Catalogue Dataframes for outputs of interest and downloads in parallel to user-specified path.
Once downloaded, it checks for file integrity and re-downloads if corrupted.

"""

import ast
import numpy as np
import requests
from intake_UtilFuncs import *
from multiprocessing.pool import ThreadPool
import hashlib
from pathlib import Path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__name__)))

def verify_hash(downloaded_file, expected_hash):
    # Calculate the hash of the downloaded file.
    calculated_hash = calculate_hash(downloaded_file)
    # Compare the calculated hash with the expected hash and return the result.
    return calculated_hash == expected_hash

def calculate_hash(file_path):
    # Create a SHA-256 hash object.
    sha256_hash = hashlib.sha256()
    # Open the file in binary mode for reading (rb).
    with open(file_path, "rb") as file:
        # Read the file in 64KB chunks to efficiently handle large files.
        while True:
            data = file.read(65536)  # Read the file in 64KB chunks.
            if not data:
                break
            # Update the hash object with the data read from the file.
            sha256_hash.update(data)
    # Return the hexadecimal representation of the calculated hash.
    return sha256_hash.hexdigest()

def test_dwnld_speed(df_single_line):

    url_list_str = df_single_line.iloc[0]['HTTPServer']  # Complete - TODO improvement change this call to func that retrieves the best url for the file in question
    url_list = ast.literal_eval(url_list_str)
    url_list = list(set(url_list)) #this removes repeated entries

    download_speeds = []

    for url in url_list:
        # Complete TODO - check if no timeout error is raised with the url and if so remove it from the list of urls for that file and test the next best url until one works.
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                chunk_size = 2 ** 20  # 1Mb in bytes
                for chunk in response.iter_content(
                        chunk_size=chunk_size):  # just do a dummy chunk download per url to test speed based on user's connection
                    if chunk:
                        download_speed = round((len(chunk) / (response.elapsed.microseconds)), 2)  # conversion to MBPS is numerically identical when data are in bytes per microsecond
                        #print(f'Downloading speed is {download_speed} Mbps for url: {url}')
                        break
                download_speeds.append(download_speed)

            else:
                if response.status_code == 404:
                    #print(f"File not found at server {url}")
                    #print("Trying next url if available...\n")
                    download_speeds.append(-1) # flag for non-existing file
                    continue

        except requests.ConnectTimeout as e:
            #print(f"Connect timeout for {url}.\nError: {e}")
            #print("Trying next url if available...\n")
            download_speeds.append(0)
            continue

        except requests.ConnectionError as e: #this catches error when server hangs up mid-ring because it thinks we are a bot
            #print(f"Critical error with {url}: {e}")
            #print("Trying next url if available...\n")
            download_speeds.append(0)
            continue

    # now return the url with fatest speed and use that
    # get indx of highest speed in the list
    fastest_url_idx = download_speeds.index(max(download_speeds))
    best_url = url_list[fastest_url_idx]

    return {'urls':url_list,'speeds': download_speeds}

def download_files(DF_Downloadable_single_line, download_path, download_logger):

    file_path = DF_Downloadable_single_line.iloc[0]['local_path']  # complete - TODO remove the first two levels from path to build the filename
    file_name = os.path.basename(file_path)
    outpath = os.path.join(download_path, os.path.dirname(file_path))
    file_fullname = os.path.join(outpath, file_name)

    content_length = DF_Downloadable_single_line.iloc[0]['size']

    if not os.path.isdir(outpath):
        os.makedirs(outpath)

    # complete TODO - change this call to func that retrieves the best url for the file in question
    speed_test_dict = test_dwnld_speed(DF_Downloadable_single_line)
    sorted_indices = np.argsort(speed_test_dict['speeds'])[::-1]
    sorted_urls = [speed_test_dict['urls'][i] for i in sorted_indices]

    if DF_Downloadable_single_line.iloc[0]['Downloadable'] == True and not os.path.isfile(file_fullname):  # if downloadable and file has not been downloaded yet#

        download_logger.info(text_align(f"Starting download for file: {file_name}\n"))
        try_download(sorted_urls, file_fullname, file_name, content_length, download_logger)

    elif os.path.isfile(file_fullname):  # if file already exists
        # checksum part to test corruption
        download_logger.info(text_align(f'File exists at {file_fullname}'))
        download_logger.info(f"Checking for file integrity...")

        hash_source = DF_Downloadable_single_line.iloc[0]['checksum']
        hash_test = verify_hash(file_fullname, hash_source)  # if returns TRUE then file is not corrupted

        if hash_test == False:  # if it exists but hash test showed corruption
            download_logger.info(text_align(f"File checksum indicates corruption. Downloading again to: {download_path}\n"))

            try_download(sorted_urls, file_fullname, file_name, content_length, download_logger)

        elif hash_test == True:
            download_logger.info(text_align(f"File is intact and already downloaded to {file_fullname}\n"))

def try_download(sorted_urls, file_fullname, file_name, content_length, download_logger):

    for url_test in sorted_urls:
        try:
            response = requests.get(url_test, stream=True)
            chunk_size = 2 ** 20  # 1 Mb

            with open(file_fullname, mode="wb") as file:
                pbar = tqdm(unit="B", unit_scale=True, unit_divisor=1024, miniters=1,
                            total=content_length)  # shows pbar in Kilobytes
                pbar.set_description("Downloading « %s »" % file_name)
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:  # filter out keep-alive new chunks
                        pbar.update(len(chunk))
                        file.write(chunk)
            break


        except requests.ConnectionError as e:  # this catches error when server hangs up mid-ring because it thinks we are a bot
            download_logger.debug(text_align(f"Critical error with {url_test}: {e}"))
            download_logger.debug("Trying second best url...\n")
            continue
    else:
        download_logger.debug(text_align(f"Unable to automatically download {file_name}."))
        download_logger.debug(f"All url options exhausted.Please check ESGF nodes manually at:")
        download_logger.debug('##########')
        download_logger.debug(text_align("\n".join([f"{url}" for url in sorted_urls])))
        download_logger.debug('##########\n')

#############################################

if __name__=="__main__":

    print_precog_header()

    ### Defining paths and loading dataframes
    download_path = input("Define the download path. Either type path or drag desired download folder onto this terminal window:")
    download_path = Path(download_path.strip(" ")) #strip added as dragging onto terminal adds a trailing 'space'

    df_filename = input("Now either drag onto terminal or type path to Dataframe with the Filtered ESGF search results desired:")
    df_filename = Path(df_filename.strip(" ")).name #strip added as dragging onto terminal adds a trailing 'space'

    # TODO logging file: append exception catching from within download_files function
    today = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    log_dl_name = df_filename.split('DF_Downloadable_')[1].split('.xlsx')[0]
    log_dl_path = os.path.join(download_path, f"ESGF_DownloadLog_{log_dl_name}_{today}.txt")
    logger_dld = instantiate_logging_file(log_dl_path, logger_name=str(log_dl_name)) # start the logger

    print('Checking if Dataframe is readable')
    print(os.path.isfile(os.path.join(download_path, df_filename)))
    print(f'Importing Dataframe {df_filename}')

    # ### Defining paths and loading dataframes using Tkinter system GUI window
    # print('Select Download path on the open window')
    # download_path = tk.filedialog.askdirectory(
    #                                         title='Select path where files will be downloaded to',
    #                                         initialdir=os.getcwd())
    #
    # df_filename = tk.filedialog.askopenfilename(
    #                                         title='Select Dataframe with the Filtered ESGF search results',
    #                                         initialdir=os.getcwd(),
    #                                         filetypes=(('CSV','*.csv'), ('Excel', '*.xlsx')),
    #                                         )
    # df_filename = Path(df_filename).name

    # #Complete TODO Load filtered search 'Downloadable' Dataframe prompting user for space required
    df_downloadable = pd.read_excel(os.path.join(download_path, df_filename))

    ## NOW ONTO DOWNLOADING FILES
    #Complete TODO prompt for user input
    print(f'There are {len(df_downloadable)} files totalling {(sum(df_downloadable['size'])/1e9):.2f} Gb for variable(s) {df_downloadable['variable_id'].unique().tolist()}')
    user_input = input("Do you want to continue to downloads? (yes/no): ")

    if user_input.lower() in ["yes", "y"]:
        print("Continuing...\n")

        # parallelizing download
        iterable_dwnld = []
        for i in range(0, len(df_downloadable)):
            # building_iterable
            df_single = df_downloadable.iloc[[i]]
            iterable_dwnld.append(
                (df_single, download_path, logger_dld))  # this is the iterable being passed to the download function with 2 args

        #iterable_dwnld = iterable_dwnld[0:4]  # this is for testing. #TODO delete this line in the future

        with  ThreadPool(min(32, os.cpu_count() + 4)) as pool:
            pool.starmap(download_files, iterable_dwnld) #starmap unpacks the iterable args to function

        #TODO check if all files were downloaded to destination and append file status to dataframe
        print('Download sweep complete \n')

    else:
        print("Exiting...\n")

    #Motivanional quote
    print_precog_footer()
    print(f'Downloaded ESM outputs should have been saved at {os.path.join(download_path, 'CMIP6')}')
    print('You got the data. Now go be amazing!')


#############################################
########### NEXT STEPS ####################
# COMPLETE TODO - New program : new catalogue search to retrieve ocean cell measures for the models that have been shortlisted
# TODO - New program : find models after screening for pi and Historical which have forward branching simulations available in for example 'ScenarioMIP' activities
