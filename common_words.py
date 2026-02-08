import re 
import sys 

def signal_handler(sig, frame): 
    try:
        get_top_50_words()
    except Exception as err:
        print(f"ERROR obtaining the top 50 words: {err}")
    print("Exiting...")
    sys.exit(0)

def computeWordFrequencies(token_list: list) -> dict:
    try: 
        token_freqs = {}

        # Checks if parameter is a list 
        if not isinstance(token_list, list):
            raise TypeError("Expected a list of tokens")
        
        # Iterate through token list and add to dictionary with freqs
        for token in token_list:
            # Makes sure tokens are strings (can't use random lists)
            if not isinstance(token, str):
                continue

            # Adds the token to the dictionary and updates counter
            token_freqs[token] = token_freqs.get(token, 0) + 1

        return token_freqs
    
    except Exception as err: 
        print("Failed because of:", err)

def get_top_50_words(): 
    # Stop Words 
    stop_words = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an",
        "and", "any", "are", "aren't", "as", "at", "be", "because", "been",
        "before", "being", "below", "between", "both", "but", "by", "can't",
        "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
        "doing", "don't", "down", "during", "each", "few", "for", "from",
        "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having",
        "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers",
        "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
        "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its",
        "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
        "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
        "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
        "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't",
        "so", "some", "such", "than", "that", "that's", "the", "their",
        "theirs", "them", "themselves", "then", "there", "there's", "these",
        "they", "they'd", "they'll", "they're", "they've", "this", "those",
        "through", "to", "too", "under", "until", "up", "very", "was",
        "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't",
        "what", "what's", "when", "when's", "where", "where's", "which",
        "while", "who", "who's", "whom", "why", "why's", "with", "won't",
        "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
        "your", "yours", "yourself", "yourselves"
    }
    
    # Reads all saved text
    with open('crawled_text.txt', 'r', encoding='utf-8') as file:
        text = file.read()

    # Tokenizes by finding only alphabetic words
    tokens = re.findall(r'\b[a-z]+\b', text.lower()) 
    
    # Filter out based on stop words and single characters 
    filtered_tokens = []
    for token in tokens:
        if token not in stop_words and len(token) > 1:
            filtered_tokens.append(token)

    # Finds word frequencies and sorts only the top 50
    word_freqs = computeWordFrequencies(filtered_tokens)
    sorted_words = sorted(word_freqs.items(), key=lambda item: item[1], reverse=True)[:50] 
    
    # Saves to file 
    with open('top_50_words.txt', 'w') as file:
        for rank, (word, count) in enumerate(sorted_words, 1):
            file.write(f"{rank}. {word} - {count}\n")

    return sorted_words

if __name__ == "__main__": 
    # IMPORTANT - must run crawler first for this to work.
    top_words = get_top_50_words()

    # Print results
    print("TOP 50 MOST COMMON WORDS + FREQUENCIES:")
    for rank, (word, count) in enumerate(top_words, 1):
        print(f"{rank}. {word} - {count:,}")
