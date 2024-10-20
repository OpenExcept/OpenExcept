import pytest
from openexcept.embeddings.sentence_transformers import SentenceTransformerEmbedding
from openexcept.core import ExceptionEvent

@pytest.fixture
def embedding():
    return SentenceTransformerEmbedding()

def test_sentence_transformer_embedding_init():
    embedding = SentenceTransformerEmbedding()
    assert embedding.model.get_sentence_embedding_dimension() > 0

def test_sentence_transformer_embedding_init_custom_model():
    custom_model = "paraphrase-MiniLM-L3-v2"
    embedding = SentenceTransformerEmbedding(model_name=custom_model)
    assert embedding.model.get_sentence_embedding_dimension() > 0

def test_sentence_transformer_embedding_embed(embedding):
    exception = ExceptionEvent(type="ValueError", message="Invalid input")
    result = embedding.embed(exception)
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(x, float) for x in result)

def test_sentence_transformer_embedding_embed_different_exception(embedding):
    exception = ExceptionEvent(type="TypeError", message="Unsupported operand type")
    result = embedding.embed(exception)
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(x, float) for x in result)

def test_sentence_transformer_embedding_consistency(embedding):
    exception1 = ExceptionEvent(type="ValueError", message="Invalid input")
    exception2 = ExceptionEvent(type="ValueError", message="Invalid input")
    
    result1 = embedding.embed(exception1)
    result2 = embedding.embed(exception2)
    
    assert result1 == result2

def test_sentence_transformer_embedding_different_exceptions(embedding):
    exception1 = ExceptionEvent(type="ValueError", message="Invalid input")
    exception2 = ExceptionEvent(type="TypeError", message="Unsupported operand type")
    
    result1 = embedding.embed(exception1)
    result2 = embedding.embed(exception2)
    
    assert result1 != result2