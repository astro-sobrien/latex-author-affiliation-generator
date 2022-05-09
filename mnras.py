import pandas as pd
import numpy as np
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-A','--authors',required=True,type=str,help='Relative file path to Authors_Affiliations.tsv')
parser.add_argument('-C','--commands',required=True,type=str,help='Relative file path to Commands_Affiliations.tsv')
parser.add_argument('-O','--output',required=True,type=str,help='Relative file path to output file you wish to write to (include .txt)')
parser.add_argument('--orcid',action='store_true',help="Include this argument if you wish to include ORCIDs")

args = parser.parse_args()

auth_df = pd.read_csv(args.authors,sep='\t',skiprows=5)
command_df = pd.read_csv(args.commands,sep='\t',skiprows=3)

output_path = args.output

print('Setting author order')
alpha_lastnames = sorted(auth_df.loc[np.isnan(auth_df['Order']),'Last Name'])
repeated_lastnames = set([x for x in alpha_lastnames if alpha_lastnames.count(x)>1])
unique_lastnames = sorted(np.unique(alpha_lastnames))

order_count = max(auth_df.Order)+1
for lname in unique_lastnames:
    if lname in repeated_lastnames:
        alpha_firstnames = sorted(auth_df.loc[auth_df['Last Name']==lname,'First Name(s)'])
        for fname in alpha_firstnames:
            auth_df.loc[(auth_df['Last Name']==lname) & (auth_df['First Name(s)']==fname),'Order']=order_count
            order_count += 1
    else:
        auth_df.loc[auth_df['Last Name']==lname,'Order']=order_count
        order_count += 1

print('Ordering affiliations')
auth_df = auth_df.sort_values('Order')

affil_order_full = []
for i in auth_df.Order:
    affil_list = auth_df.loc[auth_df['Order']==i,["Affiliation {}".format(j+1) for j in range(len(auth_df.columns)-5)]].to_numpy(dtype='str')[0]
    bool_arr = affil_list!='nan'
    affil_nonan = affil_list[bool_arr]
    for affil in affil_nonan:
        affil_order_full.append(affil)

_, idx = np.unique(affil_order_full, return_index=True)
affil_ordered = np.array(affil_order_full)[np.sort(idx)]

print(affil_ordered)

output_file = open(output_path, 'w')

output_file.write("%Copy this into the pre-amble\n")
if args.orcid:
    print("Including ORCID pre-amble")
    output_file.writelines(["%For ORCIDs\n", "\\usepackage{xcolor}\n", "\\usepackage{hyperref}\n","\\newcommand{\\orc}{$^{\\includegraphics[height=\\fontcharht\\font`A]{figures/orcidlogo.pdf}}$}\n","\\newcommand{\\orcid}[1]{\\href{https://orcid.org/#1}{\\orc}}\n"])

output_file.write("\n")
print("Defining commands")
output_file.write("%For affiliation commands\n")
for i in range(len(affil_ordered)):
    command = command_df.loc[command_df['Affiliation']==affil_ordered[i],'Command'].item()
    output_file.write("\\newcommand{\\"+command+"}{$^"+str(i+1)+"$}\n")

output_file.write("\n")
print("Creating author list")
output_file.write("%Author list, replaces full author[]{} section\n")

output_file.write("\\author[")
first_author = auth_df.loc[auth_df["Order"]==1,'First Name(s)'].item() +' '+ auth_df.loc[auth_df["Order"]==1,'Last Name'].item()
fap_listed = first_author.split(" ")
output_file.write(fap_listed[0][0]+". "+' '.join(fap_listed[1:])+" et al.]{\n")

for i in auth_df.Order:
    author_name = auth_df.loc[auth_df["Order"]==i,'First Name(s)'].item() +' '+ auth_df.loc[auth_df["Order"]==i,'Last Name'].item()
    affil_list = auth_df.loc[auth_df['Order']==i,["Affiliation {}".format(j+1) for j in range(len(auth_df.columns)-5)]].to_numpy(dtype='str')[0]
    bool_arr = affil_list!='nan'
    affil_nonan = affil_list[bool_arr]
    orcid_id = auth_df.loc[auth_df["Order"]==i,"ORCID"].item()
    if args.orcid and not pd.isna(orcid_id):
        if i>=max(auth_df.Order)-1:
            author_latex_line=[author_name,"\\orcid{"+orcid_id+"}"]
        else:
            author_latex_line=[author_name,"\\orcid{"+orcid_id+"}",","]
    else:
        if i>=max(auth_df.Order)-1:
            author_latex_line=[author_name]
        else:
            author_latex_line=[author_name,","]
    for affil in affil_nonan:
        command = command_df.loc[command_df["Affiliation"]==affil,"Command"].item()
        slash_com = "\{}".format(command)
        author_latex_line.append(slash_com)
        author_latex_line.append("$^,$")
    author_latex_line = author_latex_line[:-1]
    if i==1:
        author_latex_line.append("\\thanks{E-mail: "+auth_df.loc[auth_df["Order"]==1,'Email'].item()+"}\n")
    else:
        author_latex_line.append("\\\n")
    output_file.write(''.join(author_latex_line))

    if i%5==0:
        output_file.write("\\newauthor\n")

    if i==max(auth_df.Order)-1:
        output_file.write("and\n")

output_file.write("\\\\\n")

print("Creating list of institutions")
output_file.write("%List of institutions\n")
for i in range(len(affil_ordered)):
    command = command_df.loc[command_df['Affiliation']==affil_ordered[i],'Command'].item()
    output_file.write("\\"+command+" "+affil_ordered[i]+"\\\\\n")

output_file.write("}")
output_file.close()