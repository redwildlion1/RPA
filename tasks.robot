*** Settings ***
Library           RPA.Robocloud.Secrets
Library           RPA.Robocloud.Items
Library           RPA.Robocorp.Vault  # Use this if RPA.Python is deprecated

*** Variables ***
${REPO}           https://github.com/redwildlion1/RPA

*** Tasks ***
Extract News Data
    ${work_item}=    Get Work Item File    ${WORK_ITEM_ID}    # Replace ${WORK_ITEM_ID} with the actual work item ID
    ${search_phrase}=    Get Work Item Variable    ${work_item}    search_phrase
    ${news_category}=    Get Work Item Variable    ${work_item}    news_category
    ${num_months}=    Get Work Item Variable    ${work_item}    num_months

    Run Python Script   ${REPO}/news_scraper.py    ${search_phrase}    ${news_category}
