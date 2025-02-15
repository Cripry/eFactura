class EnvironmentConfig:
    BASE_URLS = {"TEST": "https://preproductie.sfs.md/ro", "PROD": "https://sfs.md/ro"}

    @classmethod
    def get_base_url(cls, environment: str) -> str:
        return cls.BASE_URLS.get(environment.upper())
