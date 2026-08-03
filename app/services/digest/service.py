from pathlib import Path
from openai import OpenAI


class DigestService:

    def __init__(self):

        self.client = OpenAI()
        pass