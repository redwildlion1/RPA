*** Settings ***
Library           RPA.Robocloud.Secrets
Library           RPA.Robocloud.Items
Library           RPA.Robocorp.Vault
Library           RPA.FileSystem

*** Variables ***
${REPO}           https://github.com/redwildlion1/RPA

*** Tasks *** 
Extract News Data
    # Get the environment variables
    ${search_phrase}=    Get Value From User    Enter the search phrase
    ${news_category}=    Get Value From User    Enter the news category
    ${num_months}=   Get Value From User    Enter the number of months to search

    # Run the Python script with the fetched variables
    Run Python Script   ${REPO}/news_scraper.py    ${search_phrase}    ${news_category}    ${num_months}

    # Read the output file
    ${output}=    Read File    /output/news_data.xlsx