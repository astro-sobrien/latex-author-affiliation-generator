import pandas as pd
import numpy as np
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-A','--authors',required=True,type=str,help='Relative file path to Authors_Affiliations.tsv')
parser.add_argument('-C','--commands',required=True,type=str,help='Relative file path to Commands_Affiliations.tsv')
parser.add_argument('-O','--output',required=True,type=str,help='Relative file path to output file you wish to write to (include .txt)')

args = parser.parse_args()

# Read in tsv files, skipping rows containing the instructions
auth_df = pd.read_csv(args.authors,sep='\t',comment='#')
command_df = pd.read_csv(args.commands,sep='\t', comment='#')

output_path = args.output

# Sets order of authors such that numbered ones are first, followed by an alphabetical list (by last name)
print('Setting author order')
alpha_lastnames = sorted(auth_df.loc[np.isnan(auth_df['Order']),'Last Name'])
# Checks for authors with same last name
repeated_lastnames = set([x for x in alpha_lastnames if alpha_lastnames.count(x)>1])
unique_lastnames = sorted(np.unique(alpha_lastnames))

order_count = max(auth_df.Order)+1  # Start counter from n+1 where n is number of Ordered authors
for lname in unique_lastnames:
    if lname in repeated_lastnames:
        # Sort by first name is authors share last name
        alpha_firstnames = sorted(auth_df.loc[auth_df['Last Name']==lname,'First Name(s)'])
        for fname in alpha_firstnames:
            auth_df.loc[(auth_df['Last Name']==lname) & (auth_df['First Name(s)']==fname),'Order']=order_count
            order_count += 1
    else:
        auth_df.loc[auth_df['Last Name']==lname,'Order']=order_count
        order_count += 1

auth_df = auth_df.sort_values('Order')

output_file = open(output_path, 'w')

# Defines affiliations commands
print("Defining commands")
output_file.write("%For affiliation commands\n")
for i, row in command_df.iterrows():
    output_file.write("\\newcommand{\\"+row.Command+"}{"+row.Affiliation+"}\n")

output_file.write("\n")

print("Creating author list")
output_file.write("%Author list. Paste below paper title\n")

for i in auth_df.Order:
    # Finds author list and affiliations for each author, in order set by Order
    author_name = auth_df.loc[auth_df["Order"]==i,'First Name(s)'].item() +' '+ auth_df.loc[auth_df["Order"]==i,'Last Name'].item()
    affil_list = auth_df.loc[auth_df['Order']==i,["Affiliation {}".format(j+1) for j in range(len(auth_df.columns)-6)]].to_numpy(dtype='str')[0]
    bool_arr = affil_list!='nan'
    affil_nonan = affil_list[bool_arr]

    # Includes ORCID if applicable
    orcid_id = auth_df.loc[auth_df["Order"]==i,"ORCID"].item()
    if pd.isna(orcid_id):
        author_latex_line = ["\\author{",author_name,"}","\n"]
    else:
        author_latex_line = ["\\author[",orcid_id,"]{",author_name,"}","\n"]
    # Appends each affiliation for each author
    for affil in affil_nonan:
        command = command_df.loc[command_df["Affiliation"]==affil,"Command"].item()
        slash_com = "\{}".format(command)
        author_latex_line.append("\\affiliation{")
        author_latex_line.append(slash_com)
        author_latex_line.append("}\n")
    # for affil in affil_nonan:
    #     author_latex_line.append("\\affiliation{")
    #     author_latex_line.append(affil)
    #     author_latex_line.append("}\n")
    output_file.write(''.join(author_latex_line))
    output_file.write("\n")

print("Appending acknowledgements")
output_file.write("%Copy below into acknowledgements section\n")
ack_arr = auth_df.Acknowledgements.to_numpy(dtype=str)
ack_arr = ack_arr[~(ack_arr=='nan')]
for i in ack_arr:
    output_file.write("{}\n".format(i))

output_file.close()