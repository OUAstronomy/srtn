     _______  ___ ___  _______ ___ ___ _______ ___     _______   _______ _______ _______ ______   ___ ___ _______
    |   _   |(   Y   )|   _   |   Y   |   _   |   |   |   _   | |   _   |   _   |   _   |   _  \ |   Y   |   _   |
    |.  1___| \  1  / |.  1   |.      |.  1   |.  |   |.  1___| |.  l   |.  1___|.  1   |.  |   \|.      |.  1___|
    |.  __)_  /  _  \ |.  _   |. \_/  |.  ____|.  |___|.  __)_  |.  _   |.  __)_|.  _   |.  |    |. \_/  |.  __)_
    |:  1   |/:  |   \|:  |   |:  |   |:  |   |:  1   |:  1   | |:  |   |:  1   |:  |   |:  1    |:  |   |:  1   |
    |::.. . (::. |:.  |::.|:. |::.|:. |::.|   |::.. . |::.. . | |::.|:. |::.. . |::.|:. |::.. . /|::.|:. |::.. . |
    `-------'`--- ---'`--- ---`--- ---`---'   `-------`-------' `--- ---`-------`--- ---`------' `--- ---`-------'    
-----------------------------------------------------------------------------------------------------------------

# Directory structure

> 'rawdata' = houses the raw data used in example + some extra data to try on own

> 'output'  = contains the output files for the example to show process

> 'answer'  = contains the the reduced data summarize and results if goal is to make PV diagram of milky way

# To reduce data yourself

In order to start, first *copy* the raw data 'exampledata.txt' to a working directory. Move all scripts found in srtn/scripts to this directory as well.
'''
python3 specparse.py -n exampledata.txt -o example -v 5
'''
Follow the onscreen prompts.

This will parse through the example file and output 'master_specparse_example_s_G0.0_v0.2.txt'

Then run 
'''
python3 specplot.py -i master_specparse_example_s_G0.0_v0.2.txt -o delf -v 5
'''

This will walk you through reducing the data, this will make many files at first (9 x # of sources + 3) but it will clean these up at the end leaving finalized (3 x # of sources). If you cancel mid way it will keep all files for debugging issues.



