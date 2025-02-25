import os
from typing import Any, List, Optional

try:
    from transformers import LlamaForCausalLM, LlamaTokenizer
except ImportError:
    LlamaForCausalLM = None
    LlamaTokenizer = None

from cbc.lm.base import LMEngine
from cbc.utils.python import singleton


class HuggingFaceLlamaLMEngine(LMEngine):
    def __init__(self, model: str, weight_root: str, device: Optional[str] = None):

        if LlamaForCausalLM is None or LlamaTokenizer is None:
            raise ImportError("Please install the transformers >= 4.28.0 to use this LM engine.")

        self._device = device
        self.tokenizer = LlamaTokenizer.from_pretrained(f"{os.environ.get(weight_root, '')}{model}")
        self._generator = LlamaForCausalLM.from_pretrained(
            f"{os.environ.get(weight_root, '')}{model}", device_map="auto"
        )

    def __call__(
        self, prompt: str, n_completions: int = 1, temperature: Optional[float] = None, **kwargs: Any
    ) -> List[str]:
        input = self.tokenizer(prompt, return_tensors="pt").input_ids.to(self._generator.device)

        if temperature is not None and temperature > 0:
            outputs = self._generator.generate(
                input,
                max_new_tokens=128,
                num_return_sequences=n_completions,
                temperature=temperature,
                do_sample=True,
            )
        elif n_completions > 1:
            outputs = self._generator.generate(
                input,
                max_new_tokens=128,
                num_return_sequences=n_completions,
                do_sample=True,
            )
        else:
            outputs = self._generator.generate(
                input,
                max_new_tokens=128,
                num_return_sequences=n_completions,
                do_sample=False,
            )

        outputs = self.tokenizer.batch_decode(outputs, skip_special_tokens=True, clean_up_tokenization_spaces=False)

        # We have to return the output without the prompt, but this can be hard to identify.
        # We'll strip the prompt, and get the last 10 characters, and then partition the output based on that.
        # This is a hack, but it should work in most cases.
        split = prompt.strip()[-10:]
        outputs = [output.partition(split)[2] for output in outputs]

        return outputs

    def best(self, prompt: str) -> str:
        input = self.tokenizer(prompt, return_tensors="pt").input_ids.to(self._generator.device)

        # Beam search here doesn't work, since it requires too much GPU memory.
        outputs = self._generator.generate(
            input,
            max_new_tokens=128,
            do_sample=True,
            temperature=1.0,
            num_return_sequences=1,
            top_k=1,
            top_p=0.95,
        )
        outputs = self.tokenizer.batch_decode(outputs, skip_special_tokens=True, clean_up_tokenization_spaces=False)

        # We have to return the output without the prompt, but this can be hard to identify.
        # We'll strip the prompt, and get the last 10 characters, and then partition the output based on that.
        # This is a hack, but it should work in most cases.
        split = prompt.strip()[-10:]
        _, _, output = outputs[0].partition(split)
        return output


@singleton
class Llama7B(HuggingFaceLlamaLMEngine):
    def __init__(self, device: Optional[str] = None) -> None:
        super().__init__("7B", "HUGGINGFACE_LLAMA_WEIGHTS_ROOT", device=device)


@singleton
class Llama13B(HuggingFaceLlamaLMEngine):
    def __init__(self, device: Optional[str] = None) -> None:
        super().__init__("13B", "HUGGINGFACE_LLAMA_WEIGHTS_ROOT", device=device)


@singleton
class Llama30B(HuggingFaceLlamaLMEngine):
    def __init__(self, device: Optional[str] = None) -> None:
        super().__init__("30B", "HUGGINGFACE_LLAMA_WEIGHTS_ROOT", device=device)


@singleton
class Llama65B(HuggingFaceLlamaLMEngine):
    def __init__(self, device: Optional[str] = None) -> None:
        super().__init__("65B", "HUGGINGFACE_LLAMA_WEIGHTS_ROOT", device=device)


@singleton
class Alpaca7B(HuggingFaceLlamaLMEngine):
    def __init__(self, device: Optional[str] = None) -> None:
        super().__init__("alpaca_7B", "HUGGINGFACE_ALPACA_WEIGHTS_ROOT", device=device)


@singleton
class Koala7B(HuggingFaceLlamaLMEngine):
    def __init__(self, device: Optional[str] = None) -> None:
        super().__init__("koala_7B", "HUGGINGFACE_KOALA_WEIGHTS_ROOT", device=device)


@singleton
class Koala13B_V1(HuggingFaceLlamaLMEngine):  # noqa: N801
    def __init__(self, device: Optional[str] = None) -> None:
        super().__init__("koala_13B_v1", "HUGGINGFACE_KOALA_WEIGHTS_ROOT", device=device)


@singleton
class Koala13B_V2(HuggingFaceLlamaLMEngine):  # noqa: N801
    def __init__(self, device: Optional[str] = None) -> None:
        super().__init__("koala_13B_v2", "HUGGINGFACE_KOALA_WEIGHTS_ROOT", device=device)


@singleton
class Vicuna_7B(HuggingFaceLlamaLMEngine):  # noqa: N801
    def __init__(self, device: Optional[str] = None) -> None:
        super().__init__("vicuna_7B", "HUGGINGFACE_VICUNA_WEIGHTS_ROOT", device=device)


@singleton
class Vicuna_13B(HuggingFaceLlamaLMEngine):  # noqa: N801
    def __init__(self, device: Optional[str] = None) -> None:
        super().__init__("vicuna_13B", "HUGGINGFACE_VICUNA_WEIGHTS_ROOT", device=device)
