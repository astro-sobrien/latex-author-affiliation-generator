# latex-author-affiliation-generator
Tools for collecting author names and affiliations, setting the order and generating required LaTeX

Requires numpy, pandas.

Input author names and affiliations into the spreadsheet `author-affiliation-example.xlsx` (including LaTeX-specific characters such as `Ren\'{e} Artois` for an accented e). Preferably import the sheet into a Google Sheet first so it can be shared with collaborators who can input their information themselves.

Set the order of authors in the 'Order' column of this first sheet, you don't need to sort the list as the Python script will handle this.
Any author with a blank 'Order' will be automatically ordered in the alphabetical section of the author list

In the Commands_Affiliations sheet, set the shorthand commands (I suggest three letter codes, but there's no restrictions) for each unique affiliation. Be careful not to define an already common/previously defined LaTeX command). If the spreadsheet is working properly it should have identified all the unique affiliations. Be sure to check the Google Sheet command is searching the full list of affiliations:

The command in cell B2 by default is `=UNIQUE(FILTER(FLATTEN(Authors_Affiliations!D5:F9),FLATTEN(Authors_Affiliations!D5:F())<>""))`.
This means it is searching the range `D5:F9` of the first sheet, flattenning it into a list, removing blanks (the `FILTER` command) and then finding the unique entries. You should only need to change the `F9` in both parts of this command depending on the number of affiliation columns and number of authors.

Next, export BOTH sheets as .tsv files. **Important** .csv files WILL NOT WORK, the commas in affiliation addresses make this not viable.

Place the .tsv files wherever you want, I'd suggest the same folder as the .py file you will use to generate the LaTeX.

The mnras.py file requires three arguments in the command line, relative paths to: the Author_Affiliations.tsv file; the Commands_Affiliations.tsv file; and the name of the file you with to create and write to.

In the example, I ran the command `python mnras.py -A "example/author-affiliation-example - Authors_Affiliations.tsv" -C "example/author-affiliation-example - Commands_Affiliations.tsv" -O example/example_output.txt` to generate example_output.txt.

Finally, copy the relevant sections of example_output.txt into your LaTeX file. In the case of MNRAS, the first block of commands are placed with the other command definitions. The author list and affiliation list should be copied into the `\author{}` section.
