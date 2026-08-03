from pydantic import BaseModel


class DigestScene(BaseModel):

    id: str

    purpose: str

    summary: str

    educational_contribution: str

    duration_seconds: int


class StoryDigest(BaseModel):

    title: str

    educational_objective: str

    audience: str

    language: str

    emotional_arc: str

    main_conflict: str

    learning_journey: str

    characters: list[str]

    environments: list[str]

    scenes: list[DigestScene]