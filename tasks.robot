*** Settings ***
Library           RPA.Robocloud.Secrets
Library           RPA.Robocloud.Items
Library           RPA.Robocorp.Vault
Library           RPA.FileSystem
Library           Process
Library           OperatingSystem

*** Variables ***
${REPO}           https://github.com/redwildlion1/RPA
${OUTPUT_FOLDER}   ${CURDIR}/output

*** Tasks ***
Extract News Data
    # Get the environment variables
    ${search_phrase}=    Get work item variable    search_phrase    default=example
    ${news_category}=    Get work item variable    news_category    default=STORIES
    ${num_months}=       Get work item variable    num_months       default=3

    # Run the Python script with the fetched variables
    Run Process    python    ${REPO}/news_scraper.py    ${search_phrase}    ${news_category}    ${num_months}

    # Create the output folder if it doesn't exist
    Create Directory    ${OUTPUT_FOLDER}

    # Set the output folder as a suite variable
    Set Suite Variable    ${OUTPUT_FOLDER}

    # Add the output folder to artifacts
    Set Suite Metadata    Artifacts    ${OUTPUT_FOLDER}
