CREATE TABLE companies (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    auth_token VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL
); 