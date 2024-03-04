# HacathonQC2024

**Goal** : make a open-ai-api based search engine to query through données Québec and get relevant data for research projects

## Pipeline

1. classify the question (agriculture et alimentation, economie et entreprises, ...)   
2. get all relevant titles for the research projects based on the classification and ask for the most closely related one
3. somehow get data using pandas by iteratively running generated python code
4. return output to user, alongside the source