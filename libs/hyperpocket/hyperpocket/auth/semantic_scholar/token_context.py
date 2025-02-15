from hyperpocket.auth.semantic_scholar.context import SemanticScholarAuthContext
from hyperpocket.auth.semantic_scholar.token_schema import SemanticScholarTokenResponse
class SemanticScholarTokenAuthContext(SemanticScholarAuthContext):
    @classmethod
    def from_semantic_scholar_token_response(cls, response: SemanticScholarTokenResponse):
        description = f'SemanticScholar Token Context logged in'
        return cls(
            access_token=response.access_token,
            description=description,
            expires_at=None
        )