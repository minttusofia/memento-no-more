def get_tiny_model():
    from transformers import GPT2Config, GPT2LMHeadModel
    vocab_size = 32000  # Mistral's vocabulary size

    config = GPT2Config(
        vocab_size=vocab_size,
        n_positions=512,  # max sequence length
        n_ctx=1024,  # context size
        n_embd=512,  # smaller embeddings
        n_layer=4,  # fewer layers
        n_head=2  # fewer attention heads
    )
    model = GPT2LMHeadModel(config)
    return model


def get_tiny_mistral():
    from transformers import MistralConfig, MistralForCausalLM  # noqa

    config = MistralConfig(
        hidden_size=32,
        intermediate_size=128,
        num_hidden_layers=2,
        num_attention_heads=2,
        num_key_value_heads=2,
        max_position_embeddings=32 * 32,
    )
    model = MistralForCausalLM(config)
    return model


def get_tiny_llama():
    from transformers import LlamaConfig, LlamaForCausalLM  # noqa

    config = LlamaConfig(
        hidden_size=32,
        intermediate_size=128,
        max_position_embeddings=8192,
        num_hidden_layers=2,
        num_attention_heads=2,
        vocab_size=128256,
    )
    model = LlamaForCausalLM(config)
    return model
