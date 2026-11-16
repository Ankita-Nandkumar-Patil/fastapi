from fastapi import FastAPI, HTTPException

from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr


app = FastAPI()

class ProfileCreate(BaseModel):
    name: str = Field(min_length= 3, max_length= 120)
    email: EmailStr
    age: int = Field(ge= 18, le=120)
    height: float = Field(ge=50, le=250)
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)

    @field_validator("name")
    @classmethod
    def validate_name(cls, val):
        if any(char.isdigit() for char in val):
            raise ValueError("name should not contain numbers")
        return val

    @model_validator(mode="after")
    def validate_password(self):
        if self.password != self.confirm_password:
            raise ValueError("Password did not match")
        return self

class ProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int
    height: float


profile_id = 1
profiles ={}

@app.post("/profiles", response_model = ProfileResponse)
async def createProfile(profile: ProfileCreate):
    global profile_id
    new_profile = profile.model_dump(
        exclude={"password", "confirm_password"}
    )

    new_profile["id"] = profile_id

    profiles[profile_id] = new_profile

    profile_id += 1

    return new_profile


@app.get("/profiles")
async def getProfiles():
    if not profiles:
        raise HTTPException(
            status_code=404,
            detail="no profiles created yet"
        )

    return profiles


@app.get("/profiles/{profile_id}", response_model = ProfileResponse)
async def getProfile(profile_id: int):
    profile = profiles.get(profile_id)

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="profile not found"
        )

    return profile

@app.put("/profiles/{profile_id}", response_model = ProfileResponse)
async def update_profile(profile_id: int, profile: ProfileCreate):
    data = profiles.get(profile_id)
    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Profile Not Found"
        )

    updated_profile = profile.model_dump( exclude={"password", "confirm_password"})

    updated_profile["id"] = profile_id

    profiles[profile_id] = updated_profile

    return updated_profile

@app.delete("/profiles/{profile_id}")
async def deleteProfile(profile_id: int):
    profile = profiles.get(profile_id)
    if profile is None:
        raise HTTPException(
            status_code = 404,
            detail="profile not found"
        )

    profiles.pop(profile_id)

    return {"detail" : "Profile deleted successfully"}



  
