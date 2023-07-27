# Syntax analysis - Functions

#coding:utf-8

import datetime
import streamlit as st

def frequency_list(l, freq=False):
    """
    Compute the frequency of elements of a list

    Require module: None

    Args:
      l : The list to analyze
      freq : if False, the count is returned ; if True, the frequency count/total is returned (default = False)
    
    Out:
      a dictionnary
    """
    count = {}
    for i in l:
        count[i] = count.get(i, 0) + 1
    if freq==True:
        count = {k: v / total for total in (sum(count.values()),) for k, v in count.items()}
    return count


def convert_date(mydate):
    """
    Converting the format of a date from yyyymmdd to yyyy-mm-dd
    Require module: datetime

    Args: 
      mydate : The date to convert
    """
    ndate = datetime.datetime.strptime(str(mydate),'%Y%m%d')
    return ndate


def unique(l):
    """
    Get unique values from a list.

    Require module: None

    Args:
      l : a list from which to extract unique values
    
    Out:
      a list of unique values
    """
    # Insert the list to the set
    list_set = set(l)
    # Convert the set to the list
    unique_list = (list(list_set))

    return unique_list


def ndigit_nace_code(x):
    """
    Display the number of digits of NACE codes.

    Require module: None

    Args:
      x : a nace code in string format wherein division and group are separated by a "."
    
    Out:
      an integer indicating the number of digits

    """
    if x.isalpha():
        ndigit = 1
    elif ((len(x) == 1) | (len(x) == 2)) & ("." not in x):
        ndigit = 2
    else:
        ndigit = 2 + len(x.split(".")[1])
    return ndigit


@st.cache_data
def count_patent_nace(nace_l, patent_df, cpc_nace_df):
    """
    Count the number of patents by NACE sector

    Args:
      nace_l : a list of NACE codes of interest
      patent_df : a dataframe of patents
      cpc_nace_df : a dataframe providing the correspondance between CPC and NACE codes
    
    Out:
      a dictionary
    """

    # Initialize the counter of NACE codes
    nace_count = {nace:0 for nace in nace_l}

    # Set the list of CPC candidates for which there is a concordance with NACE codes
    cand_cpc = cpc_nace_df["cpc"].to_list()
    cand_cpc = unique(cand_cpc)

    ### Count the number of patents by NACE

    # Extract all CPC codes in patent data
    l_cpc_pat = []
    for patent in patent_df['cpc_low']:
        # Convert the column 'cpc_low' into a list of CPC codes
        p_lcpc = str(patent).strip("][").replace("'", "").replace("\n","").split(" ")
        # Keep only CPC candidates for which there is a concordance with NACE codes
        p_lcpc = unique([x for x in p_lcpc if x in cand_cpc])
        # Append the list
        l_cpc_pat.append(p_lcpc)

    # Convert a list of lists into a list of single elements
    lt_cpc_pat = [item for sublist in l_cpc_pat for item in sublist]
    # Count the occurence of each CPC code
    cpc_count = frequency_list(lt_cpc_pat, freq=False)

    # For each CPC code, assign the corresponding values to NACE codes
    for cpc in cpc_count:
        # For each CPC code, get the number of occurences
        ni = cpc_count[cpc]
        # For each CPC code, get the list of corresponding NACE codes
        l_nace = cpc_nace_df.loc[(cpc_nace_df["cpc"] == cpc), "nace"].to_list()
        for nace in l_nace:
            # For each CPC code and each corresponding NACE code, attribute (weight x ni) to the counter 
            nace_count[nace] += float(cpc_nace_df.loc[(cpc_nace_df["cpc"] == cpc) & (cpc_nace_df["nace"] == nace), "weight"])*ni

    return nace_count


def determine_nace_1d(s):
    """
    Determine the NACE 1 digit sector from the code at >=2 digit sector

    Args:
      s : NACE code at >=2 digit sector
    
    Out:
      a string
    """

    first_two_digits = s[:2]
    if first_two_digits in ["01", "02", "03"]:
        return "A"
    elif first_two_digits in ["05", "06", "07", "08", "09"]:
        return "B"
    elif int(first_two_digits) in range(10,33+1):
        return "C"
    elif first_two_digits == "35":
        return "D"
    elif first_two_digits in ["36", "37", "38", "39"]:
        return "E"
    elif first_two_digits in ["41", "42", "43"]:
        return "F"
    elif first_two_digits in ["45", "46", "47"]:
        return "G"
    elif int(first_two_digits) in range(49,53+1): 
        return "H"
    elif first_two_digits in ["55", "56"]:
        return "I"
    elif int(first_two_digits) in range(58,63+1):
        return "J"
    elif first_two_digits in ["64", "65", "66"]:
        return "K"
    elif first_two_digits == "68":
        return "L"
    elif int(first_two_digits) in range(69,75+1):
        return "M"
    elif int(first_two_digits) in range(77,82+1):
        return "N"
    elif first_two_digits == "84":
        return "O"
    elif first_two_digits == "85":
        return "P"
    elif int(first_two_digits) in range(86,88+1):
        return "Q"
    elif int(first_two_digits) in range(90,93+1):
        return "R"
    elif int(first_two_digits) in range(94,96+1):
        return "S"
    elif int(first_two_digits) in range(97,98+1):
        return "T"
    elif first_two_digits == "99":
        return "U"
    else:
        return None