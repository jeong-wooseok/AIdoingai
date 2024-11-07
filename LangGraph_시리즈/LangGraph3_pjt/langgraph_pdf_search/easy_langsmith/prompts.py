import yaml
import numpy as np
from langchain_core.example_selectors.base import BaseExampleSelector
from langchain_core.prompts import loading
from langchain_core.prompts.base import BasePromptTemplate


def load_prompt(file_path, encoding="utf8") -> BasePromptTemplate:
    """
	Loads a prompt configuration based on the provided file path.

	This function reads a YAML-formatted prompt configuration from the given file path
	and loads the prompt according to the specified configuration.

	Parameters:
	file_path (str): The path to the prompt configuration file.

	Returns:
	object: Returns the loaded prompt object.
   """
    with open(file_path, "r", encoding=encoding) as f:
        config = yaml.safe_load(f)

    return loading.load_prompt_from_config(config)


class CustomExampleSelector(BaseExampleSelector):
    """
	A class for selecting the most similar examples to a given input text.
	This class uses OpenAI's embedding model to pre-compute vector representations of the examples,
	and selects the most similar examples based on the cosine similarity between the input text and the examples.

	Attributes:
	    examples (list): A list of examples to be used as the selection criteria.
	    embedding_model (object): An embedding model for converting text into vectors.
	    search_key (str): The key in the examples to compare the input text against.
    """

    def __init__(self, examples, embedding_model, search_key="instruction"):
        """
        Initializes the list of examples, embedding model, and search key.

	Args:
	    examples (list): A list of example data.
	    embedding_model (object): The model to be used for computing embeddings.
	    search_key (str): The key in the examples to be used for comparison with the input.
"""
        self.examples = examples
        self.embedding_model = embedding_model
        self.search_key = search_key
        self.example_embeddings = [
            (example, self.embedding_model.embed_query(example[search_key]))
            for example in examples
        ]

    def cosine_similarity(self, vec1, vec2):
        """Compute the cosine similarity between two vectors:"""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def add_example(self, example):
        """Add a new example to the list of examples"""
        self.examples.append(example)

    def select_examples(self, input_variables, k=1):
        """
     Selects the top k most similar examples for the given input variables.

	Args:
	    input_variables (dict): A dictionary containing the input text along with the search key.
	    k (int): The number of top examples to return.

	Returns:
	    list: The top k examples with the highest similarity.
        """
        # Calculates the embedding of the input text.
        input_text = input_variables[self.search_key]
        input_embedding = self.embedding_model.embed_query(input_text)

        # Calculates the similarity and stores it with the examples.
        similarities = []
        for example, example_embedding in self.example_embeddings:
            similarity = self.cosine_similarity(input_embedding, example_embedding)
            similarities.append((example, similarity))

        # Sorts the examples in descending order of similarity.
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Returns the top k examples with the highest similarity.
        return [example for example, _ in similarities[:k]]
