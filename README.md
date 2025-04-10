There are totally 6 sets of Python scripts. Below are the description of each set.

1. Data_Collection_Clean.py - This script is used to collect data from the web. For this assessment, I chose Google News RSS as data scource. The difficult part is that the Google News RSS does not provide the full text of the news. I have to convert google search result to an actual news link and then extract the full text from the news link, which is a time-consuming task.
2. Entity_Recognition_and_Extraction.py - This script is used to extract entities from the text.

Different methods are used to classify the adverse news and how relevance score and model measurement are calculated.

3. Adverse_News_Classification_1.py - LLM Zero/Few-Shot Classification
4. Adverse_News_Classification_2.py - BERTopic (Unsupervised Topic Modeling)
5. Adverse_News_Classification_3.py - Rule-Based Weak Supervision + ML
6. Adverse_News_Classification_4.py - Embedding + Clustering