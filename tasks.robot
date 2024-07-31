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
    ${search_phrase}=    Get work item variable   search_phrase default=example
    ${news_category}=    Get work item variable   news_category default=STORIES
    ${num_months}=   Get work item variable   num_months default=3

    # Run the Python script with the fetched variables
    Run Python Script   ${REPO}/news_scraper.py    ${search_phrase}    ${news_category}    ${num_months}

    # Read the output file
    ${output}=    Read File    /output/news_data.xlsx