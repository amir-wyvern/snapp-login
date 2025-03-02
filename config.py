from pydantic_settings import BaseSettings


class EnvsConfig(BaseSettings):

    SNP_URL: str
    SQLITE_ADDRESS: str

    class Config:
 
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


envs = EnvsConfig()
