import pandas as pd
import numpy as np
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-A','--authors',required=True,type=str,help='Relative file path to Authors_Affiliations.tsv')
parser.add_argument('-C','--commands',required=True,type=str,help='Relative file path to Commands_Affiliations.tsv')
parser.add_argument('-O','--output',required=True,type=str,help='Relative file path to output file you wish to write to (include .txt)')

args = parser.parse_args()

auth_df = pd.read_csv(args.authors,sep='\t')
command_df = pd.read_csv(args.commands,sep='\t')

output_path = args.output

print('Ordering affiliations')
auth_df = auth_df.sort_values('Order')

affil_order_full = []
for i in auth_df.Order:
    author_name = auth_df.loc[auth_df['Order']==i,'Name'].item()
    affil_list = auth_df.loc[auth_df['Order']==i,["Affiliation {}".format(j+1) for j in range(len(auth_df)-2)]].to_numpy(dtype='str')[0]
    bool_arr = affil_list!='nan'
    affil_nonan = affil_list[bool_arr]
    for affil in affil_nonan:
        affil_order_full.append(affil)

_, idx = np.unique(affil_order_full, return_index=True)
affil_ordered = np.array(affil_order_full)[np.sort(idx)]

print(affil_ordered)

output_file = open(output_path, 'w')

print("Defining commands")
output_file.write("%Copy this into the pre-amble\n")
for i in range(len(affil_ordered)):
    command = command_df.loc[command_df['Affiliation']==affil_ordered[i],'Command'].item()
    output_file.write("\\newcommand{\\"+command+"}{$^"+str(i+1)+"$}\n")

output_file.write("\n")
print("Creating author list")
output_file.write("%Copy this into the author list\n")
for i in auth_df.Order:
    author_name = auth_df.loc[auth_df['Order']==i,'Name'].item()
    affil_list = auth_df.loc[auth_df['Order']==i,["Affiliation {}".format(j+1) for j in range(len(auth_df)-2)]].to_numpy(dtype='str')[0]
    bool_arr = affil_list!='nan'
    affil_nonan = affil_list[bool_arr]
    if i==max(auth_df.Order)-1:
        author_latex_line=[author_name]
    elif i==max(auth_df.Order):
        author_latex_line=[author_name]
    else:
        author_latex_line=[author_name,","]
    for affil in affil_nonan:
        command = command_df.loc[command_df["Affiliation"]==affil,"Command"].item()
        slash_com = "\{}".format(command)
        author_latex_line.append(slash_com)
        author_latex_line.append("$^,$")
    author_latex_line = author_latex_line[:-1]
    author_latex_line.append("\\\n")
    output_file.write(''.join(author_latex_line))

    if i==max(auth_df.Order)-1:
        output_file.write("and\n")

output_file.write("\\\\\n\n")

print("Creating list of institutions")
output_file.write("%Copy this into the list of institutions\n")
for i in range(len(affil_ordered)):
    command = command_df.loc[command_df['Affiliation']==affil_ordered[i],'Command'].item()
    output_file.write("\\"+command+" "+affil_ordered[i]+"\\\\\n")

output_file.close()